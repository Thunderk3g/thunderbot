"""Audit log and control-plane storage.

Every signal, LLM decision (with the full prompt), order, closed trade and
compliance event is written to a local SQLite journal. That journal is the
source of truth on the VPS and works offline. If Supabase is configured, the
same rows are mirrored to Postgres for the dashboard, and the dashboard's
controls (kill switch, pause, login confirmation) are read back from Supabase.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import uuid
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from .clock import now_ist

log = logging.getLogger(__name__)

TABLES = ("events", "signals", "llm_decisions", "orders", "trades", "jobs", "equity", "signal_outcomes")


def _matches(row: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    for k, v in (filters or {}).items():
        if str(row.get(k)) != str(v):
            return False
    return True


def _sort_key(value: Any) -> tuple:
    # None sorts first; mixed types compare as strings
    return (value is not None, value if isinstance(value, (int, float)) else str(value))


def _jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def new_id() -> str:
    return str(uuid.uuid4())


class Store(Protocol):
    def insert(self, table: str, row: dict[str, Any]) -> None: ...

    def get_control(self) -> dict[str, Any]: ...

    def set_control(self, key: str, value: Any) -> None: ...


class SQLiteStore:
    """Rows are stored as JSON blobs keyed by table, so the schema can evolve freely."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False, timeout=30)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS journal (id TEXT PRIMARY KEY, tbl TEXT NOT NULL, ts TEXT NOT NULL, row TEXT NOT NULL)"
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS journal_tbl_ts ON journal (tbl, ts)")
        self._conn.execute("CREATE TABLE IF NOT EXISTS control (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)")
        self._conn.commit()

    def insert(self, table: str, row: dict[str, Any]) -> None:
        row = _jsonable(row)
        row.setdefault("id", new_id())
        row.setdefault("created_at", now_ist().isoformat())
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO journal (id, tbl, ts, row) VALUES (?, ?, ?, ?)",
                (row["id"], table, row["created_at"], json.dumps(row, default=str)),
            )
            self._conn.commit()

    def rows(self, table: str, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT row FROM journal WHERE tbl = ? ORDER BY ts DESC LIMIT ?", (table, limit)
            )
            return [json.loads(r[0]) for r in cur.fetchall()]

    def select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        order: str = "created_at",
        desc: bool = True,
        limit: int = 100,
        scan: int = 20_000,
    ) -> list[dict[str, Any]]:
        """Equality-filtered, ordered rows. Scans the newest ``scan`` rows of the table."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT row FROM journal WHERE tbl = ? ORDER BY ts DESC LIMIT ?", (table, scan)
            )
            rows = [json.loads(r[0]) for r in cur.fetchall()]
        rows = [r for r in rows if _matches(r, filters)]
        rows.sort(key=lambda r: _sort_key(r.get(order)), reverse=desc)
        return rows[:limit]

    def update(self, table: str, row_id: str, fields: dict[str, Any]) -> None:
        fields = _jsonable(fields)
        with self._lock:
            cur = self._conn.execute("SELECT row FROM journal WHERE id = ? AND tbl = ?", (row_id, table))
            found = cur.fetchone()
            row = json.loads(found[0]) if found else {"id": row_id, "created_at": now_ist().isoformat()}
            row.update(fields)
            self._conn.execute(
                "INSERT OR REPLACE INTO journal (id, tbl, ts, row) VALUES (?, ?, ?, ?)",
                (row_id, table, row["created_at"], json.dumps(row, default=str)),
            )
            self._conn.commit()

    def get_control(self) -> dict[str, Any]:
        with self._lock:
            cur = self._conn.execute("SELECT key, value FROM control")
            return {k: json.loads(v) for k, v in cur.fetchall()}

    def set_control(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO control (key, value, updated_at) VALUES (?, ?, ?)",
                (key, json.dumps(_jsonable(value)), now_ist().isoformat()),
            )
            self._conn.commit()


class SupabaseStore:
    """Mirrors rows to Supabase via PostgREST using the service-role key (worker side only)."""

    def __init__(self, url: str, service_key: str, timeout: float = 5.0) -> None:
        import requests

        self.base = url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self.http = requests.Session()
        self.http.headers.update(
            {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal,resolution=merge-duplicates",
            }
        )

    def insert(self, table: str, row: dict[str, Any]) -> None:
        resp = self.http.post(f"{self.base}/{table}", data=json.dumps(_jsonable(row), default=str), timeout=self.timeout)
        resp.raise_for_status()

    def select(self, table: str, filters: dict[str, Any] | None = None, order: str = "created_at",
               desc: bool = True, limit: int = 100) -> list[dict[str, Any]]:
        params = {"select": "*", "order": f"{order}.{'desc' if desc else 'asc'}", "limit": str(limit)}
        for k, v in (filters or {}).items():
            params[k] = f"eq.{v}"
        resp = self.http.get(f"{self.base}/{table}", params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def update(self, table: str, row_id: str, fields: dict[str, Any]) -> None:
        resp = self.http.patch(f"{self.base}/{table}", params={"id": f"eq.{row_id}"},
                               data=json.dumps(_jsonable(fields), default=str), timeout=self.timeout)
        resp.raise_for_status()

    def get_control(self) -> dict[str, Any]:
        resp = self.http.get(f"{self.base}/control", params={"select": "key,value"}, timeout=self.timeout)
        resp.raise_for_status()
        return {r["key"]: r["value"] for r in resp.json()}

    def set_control(self, key: str, value: Any) -> None:
        resp = self.http.post(
            f"{self.base}/control",
            data=json.dumps({"key": key, "value": _jsonable(value), "updated_at": now_ist().isoformat()}),
            timeout=self.timeout,
        )
        resp.raise_for_status()


class CompositeStore:
    """Writes to the local journal first, then best-effort to the mirror.

    Control reads prefer the mirror (where the dashboard writes) and fall back to local.
    A failing mirror never stops trading or loses the local record.
    """

    def __init__(self, local: SQLiteStore, mirror: Any | None = None) -> None:
        self.local = local
        self.mirror = mirror

    def insert(self, table: str, row: dict[str, Any]) -> None:
        row = _jsonable(row)
        row.setdefault("id", new_id())
        row.setdefault("created_at", now_ist().isoformat())
        self.local.insert(table, row)
        if self.mirror is not None:
            try:
                self.mirror.insert(table, row)
            except Exception as e:
                log.warning("mirror insert into %s failed: %s", table, e)

    def select(self, table: str, filters: dict[str, Any] | None = None, order: str = "created_at",
               desc: bool = True, limit: int = 100) -> list[dict[str, Any]]:
        """Reads come from the mirror when configured (the dashboard writes jobs there), else local."""
        if self.mirror is not None:
            return self.mirror.select(table, filters, order, desc, limit)
        return self.local.select(table, filters, order, desc, limit)

    def update(self, table: str, row_id: str, fields: dict[str, Any]) -> None:
        if self.mirror is not None:
            self.mirror.update(table, row_id, fields)
        try:
            self.local.update(table, row_id, fields)
        except Exception as e:
            log.warning("local update of %s/%s failed: %s", table, row_id, e)

    def get_control(self) -> dict[str, Any]:
        control = self.local.get_control()
        if self.mirror is not None:
            try:
                control.update(self.mirror.get_control())
            except Exception as e:
                log.warning("mirror control read failed, using local: %s", e)
        return control

    def set_control(self, key: str, value: Any) -> None:
        self.local.set_control(key, value)
        if self.mirror is not None:
            try:
                self.mirror.set_control(key, value)
            except Exception as e:
                log.warning("mirror control write failed: %s", e)

    def event(self, kind: str, message: str, **data: Any) -> None:
        log.info("[%s] %s", kind, message)
        self.insert("events", {"kind": kind, "message": message, "data": data})


def build_store(data_dir: Path, supabase_url: str | None, supabase_key: str | None) -> CompositeStore:
    local = SQLiteStore(data_dir / "journal.sqlite3")
    mirror = SupabaseStore(supabase_url, supabase_key) if supabase_url and supabase_key else None
    return CompositeStore(local, mirror)
