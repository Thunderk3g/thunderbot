"""Local stand-in for Supabase: a tiny PostgREST-compatible API over the SQLite journal.

``thunderbot serve`` lets the dashboard run end to end on one machine with no
cloud services: point the dashboard's ``SUPABASE_URL`` at this server and its
``SUPABASE_SERVICE_ROLE_KEY`` at ``TB_LOCAL_API_KEY``. It implements only what the
dashboard uses:

- ``GET /rest/v1/<table>?select=a,b&order=col.desc&limit=n&col=eq.x`` (eq, neq, gt, gte, lt, lte, in)
- ``POST /rest/v1/<table>`` insert/upsert (object or array)
- ``PATCH /rest/v1/<table>?id=eq.x`` partial update

It binds to 127.0.0.1 by default and requires the API key on every request.
It also runs the research job runner in a background thread.
"""

from __future__ import annotations

import json
import logging
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from .config import Settings
from .store import TABLES, SQLiteStore, new_id
from .strategy import catalog

log = logging.getLogger(__name__)

ALLOWED_TABLES = set(TABLES) | {"control"}
OPS = ("eq", "neq", "gt", "gte", "lt", "lte", "in")
MAX_BODY = 2_000_000


def _coerce(a: Any, b: str) -> tuple[Any, Any]:
    if isinstance(a, bool):
        return str(a).lower(), b.lower()
    try:
        return float(a), float(b)
    except (TypeError, ValueError):
        return ("" if a is None else str(a)), b


def _match(row: dict[str, Any], col: str, expr: str) -> bool:
    op, _, raw = expr.partition(".")
    if op not in OPS:
        return True
    value = row.get(col)
    if op == "in":
        options = [x.strip().strip('"') for x in raw.strip("()").split(",")]
        return str(value) in options
    if raw == "null":
        return (value is None) == (op == "eq")
    a, b = _coerce(value, raw)
    try:
        return {
            "eq": a == b, "neq": a != b, "gt": a > b, "gte": a >= b, "lt": a < b, "lte": a <= b,
        }[op]
    except TypeError:
        return False


def query_rows(store: SQLiteStore, table: str, params: list[tuple[str, str]]) -> list[dict[str, Any]]:
    select = order = None
    limit = 1000
    filters = []
    for k, v in params:
        if k == "select":
            select = v
        elif k == "order":
            order = v
        elif k == "limit":
            limit = max(1, min(int(v), 10_000))
        elif k != "offset":
            filters.append((k, v))
    if table == "control":
        rows = [{"key": k, "value": v} for k, v in store.get_control().items()]
    elif not filters and (order is None or order.startswith("created_at.desc")):
        rows = store.select(table, None, order="created_at", desc=True, limit=limit, scan=limit)
    else:
        rows = store.select(table, None, order="created_at", desc=True, limit=50_000, scan=50_000)
    rows = [r for r in rows if all(_match(r, c, e) for c, e in filters)]
    if order:
        col, *mods = order.split(".")
        desc = "desc" in mods
        rows.sort(key=lambda r: (r.get(col) is not None, r.get(col) if isinstance(r.get(col), (int, float)) else str(r.get(col))),
                  reverse=desc)
    rows = rows[:limit]
    if select and select != "*":
        cols = [c.strip() for c in select.split(",")]
        rows = [{c: r.get(c) for c in cols} for r in rows]
    return rows


class LocalAPI:
    def __init__(self, store: SQLiteStore, settings: Settings, api_key: str) -> None:
        self.store = store
        self.settings = settings
        self.api_key = api_key
        self.publish_defaults()

    def publish_defaults(self) -> None:
        control = self.store.get_control()
        self.store.set_control("strategy_catalog", catalog())
        if "effective_settings" not in control or "settings_overrides" in control:
            self.refresh_effective(control.get("settings_overrides") or {})
        for key in ("kill_switch", "paused"):
            if key not in control:
                self.store.set_control(key, False)

    def refresh_effective(self, overrides: dict[str, Any]) -> None:
        new, rejected = self.settings.with_overrides(overrides)
        self.store.set_control("effective_settings", {**new.public_view(), "rejected": rejected})

    def write(self, table: str, body: Any) -> None:
        rows = body if isinstance(body, list) else [body]
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("rows must be JSON objects")
            if table == "control":
                self.store.set_control(str(row["key"]), row.get("value"))
                if row["key"] == "settings_overrides":
                    self.refresh_effective(row.get("value") or {})
            else:
                row.setdefault("id", new_id())
                self.store.insert(table, row)

    def patch(self, table: str, params: list[tuple[str, str]], body: dict[str, Any]) -> int:
        ids = [v.partition(".")[2] for k, v in params if k == "id" and v.startswith("eq.")]
        if not ids:
            raise ValueError("PATCH requires an id=eq.<id> filter")
        for row_id in ids:
            self.store.update(table, row_id, body)
        return len(ids)


def make_handler(api: LocalAPI):
    class Handler(BaseHTTPRequestHandler):
        server_version = "thunderbot-local"

        def log_message(self, fmt, *args):  # quiet
            log.debug("%s - %s", self.address_string(), fmt % args)

        def _send(self, code: int, payload: Any = None) -> None:
            body = b"" if payload is None else json.dumps(payload, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _route(self) -> tuple[str, list[tuple[str, str]]] | None:
            key = self.headers.get("apikey") or self.headers.get("Authorization", "").removeprefix("Bearer ")
            if not secrets.compare_digest(key or "", api.api_key):
                self._send(401, {"message": "invalid api key"})
                return None
            parts = urlsplit(self.path)
            if not parts.path.startswith("/rest/v1/"):
                self._send(404, {"message": "not found"})
                return None
            table = parts.path[len("/rest/v1/"):].strip("/")
            if table not in ALLOWED_TABLES:
                self._send(404, {"message": f"unknown table {table}"})
                return None
            return table, parse_qsl(parts.query, keep_blank_values=True)

        def _body(self) -> Any:
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                raise ValueError("body too large")
            return json.loads(self.rfile.read(n) or b"null")

        def do_GET(self):
            if self.path == "/health":
                return self._send(200, {"ok": True})
            r = self._route()
            if r is None:
                return
            try:
                self._send(200, query_rows(api.store, *r))
            except Exception as e:
                self._send(400, {"message": str(e)})

        def do_POST(self):
            r = self._route()
            if r is None:
                return
            try:
                api.write(r[0], self._body())
                self._send(201)
            except Exception as e:
                self._send(400, {"message": str(e)})

        def do_PATCH(self):
            r = self._route()
            if r is None:
                return
            try:
                api.patch(r[0], r[1], self._body())
                self._send(204)
            except Exception as e:
                self._send(400, {"message": str(e)})

    return Handler


def serve(settings: Settings, host: str, port: int, api_key: str, run_jobs: bool = True, groww_client_factory=None):
    from .jobs import JobRunner
    from .store import CompositeStore

    local = SQLiteStore(settings.data_path / "journal.sqlite3")
    api = LocalAPI(local, settings, api_key)
    if run_jobs:
        runner = JobRunner(CompositeStore(local), settings, groww_client_factory)
        threading.Thread(target=runner.run_forever, name="jobs", daemon=True).start()
    httpd = ThreadingHTTPServer((host, port), make_handler(api))
    log.info("local API on http://%s:%d (jobs %s)", host, port, "on" if run_jobs else "off")
    return httpd
