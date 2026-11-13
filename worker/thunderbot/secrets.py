"""Keys saved from the dashboard's setup screen, encrypted at rest.

The dashboard encrypts each secret before it reaches the database and the worker decrypts it when it
starts a pass. The database (Supabase, or the local SQLite journal behind ``thunderbot serve``) only
ever holds ciphertext, a masked hint such as ``sk-…a1b2`` and a little non-secret metadata.

Format, shared with ``dashboard/lib/secrets.ts``:

- key: SHA-256 of ``"thunderbot-secrets-v1:" + master``
- master: ``TB_SECRET_KEY``; when unset, the key the two sides already share to reach the database
  (``SUPABASE_SERVICE_ROLE_KEY``, or ``TB_LOCAL_API_KEY`` for the local API)
- stored string: ``"v1:" + base64(iv(12 bytes) || ciphertext || tag(16 bytes))``, AES-256-GCM
- plaintext: one JSON object

One install holds one person's keys. Nothing here can turn on real orders: live trading, the static
IP and MTF are read from the worker's environment only (see ``credentials.apply_credentials``).
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import time
from collections.abc import Mapping
from typing import Any

log = logging.getLogger(__name__)

KDF_PREFIX = "thunderbot-secrets-v1:"
VERSION = "v1"
TABLE = "secrets"
# (environment variable, what the dashboard calls that source)
MASTER_SOURCES = (("TB_SECRET_KEY", "TB_SECRET_KEY"), ("SUPABASE_SERVICE_ROLE_KEY", "service_key"),
                  ("TB_LOCAL_API_KEY", "service_key"))

TABLE_RETRY_SECONDS = 600.0  # after a failed read of the table, do not ask again for this long

_warned: set[str] = set()
_table_down_until = 0.0


class SecretError(Exception):
    """A stored secret could not be read. The message never contains key material."""


def _warn_once(key: str, message: str) -> None:
    if key not in _warned:
        _warned.add(key)
        log.warning(message)


def master_key(env: Mapping[str, str] | None = None) -> tuple[str | None, str | None]:
    """The passphrase secrets are encrypted under, and where it came from."""
    env = os.environ if env is None else env
    for name, source in MASTER_SOURCES:
        value = (env.get(name) or "").strip()
        if value:
            return value, source
    return None, None


def _aes_key(master: str) -> bytes:
    return hashlib.sha256((KDF_PREFIX + master).encode()).digest()


def _aesgcm(master: str):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:
        raise SecretError("the 'cryptography' package is not installed (pip install 'thunderbot[secrets]')") from e
    return AESGCM(_aes_key(master))


def encrypt(obj: Mapping[str, Any], master: str, iv: bytes | None = None) -> str:
    iv = iv or os.urandom(12)
    if len(iv) != 12:
        raise ValueError("iv must be 12 bytes")
    # Same bytes as JSON.stringify on the dashboard side, so both produce identical ciphertext for one IV.
    plain = json.dumps(dict(obj), separators=(",", ":"), ensure_ascii=False).encode()
    sealed = _aesgcm(master).encrypt(iv, plain, None)
    return f"{VERSION}:" + base64.b64encode(iv + sealed).decode()


def decrypt(blob: str, master: str) -> dict[str, Any]:
    version, _, payload = (blob or "").partition(":")
    if version != VERSION or not payload:
        raise SecretError("unknown secret format")
    try:
        raw = base64.b64decode(payload, validate=True)
    except ValueError as e:
        raise SecretError("stored secret is not valid base64") from e
    if len(raw) < 12 + 16:
        raise SecretError("stored secret is too short")
    cipher = _aesgcm(master)
    try:
        plain = cipher.decrypt(raw[:12], raw[12:], None)
    except Exception as e:  # cryptography.exceptions.InvalidTag
        raise SecretError("wrong key or damaged data") from e
    out = json.loads(plain)
    if not isinstance(out, dict):
        raise SecretError("stored secret is not a JSON object")
    return out


def read_row(store: Any, name: str) -> dict[str, Any] | None:
    """The stored row for ``name`` (ciphertext, hint, meta), or None. A store without the table reads as empty."""
    global _table_down_until
    select = getattr(store, "select", None)
    if select is None or time.monotonic() < _table_down_until:
        return None
    try:
        rows = select(TABLE, {"name": name}, order="updated_at", desc=True, limit=1)
    except Exception as e:
        # Usually the migration that adds the table has not been applied yet. Do not pay for the
        # store's retries on every pass.
        _table_down_until = time.monotonic() + TABLE_RETRY_SECONDS
        _warn_once("table", f"could not read the secrets table ({type(e).__name__}); using environment keys only. "
                            "Apply the latest Supabase migration to save keys from the dashboard")
        return None
    return rows[0] if rows else None


def read_secret(store: Any, name: str, env: Mapping[str, str] | None = None) -> dict[str, Any] | None:
    """Decrypt the secret saved as ``name``. None when there is none or it cannot be read; the reason
    is logged once and never includes the secret."""
    row = read_row(store, name)
    if not row or not row.get("ciphertext"):
        return None
    master, _ = master_key(env)
    if not master:
        _warn_once("master", "a key is saved in the dashboard but this worker has no TB_SECRET_KEY (or database key) "
                             "to decrypt it; using environment keys only")
        return None
    try:
        return decrypt(str(row["ciphertext"]), master)
    except SecretError as e:
        _warn_once(f"read:{name}:{e}", f"the saved '{name}' key was ignored: {e}. Set the same TB_SECRET_KEY on the "
                                       "dashboard and the worker, or save the key again in Setup")
        return None
