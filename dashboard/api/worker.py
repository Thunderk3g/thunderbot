"""Thunderbot's worker as a Vercel Function (Python runtime), served at /api/worker.

Nothing runs between calls. Schedulers wake it with a GET (one pass of the daily investing worker);
the dashboard POSTs ?op=job&id=... to run a backtest. All logic lives in the thunderbot package
(worker/ in this repository, installed through requirements.txt); this file only speaks HTTP.

Callers must send either `Authorization: Bearer $CRON_SECRET` (Vercel Cron, Supabase pg_cron) or the
dashboard's Basic credentials (the browser does this by itself). Anything else gets a 401.
"""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlsplit


class handler(BaseHTTPRequestHandler):
    def _run(self, default_op: str) -> None:
        from thunderbot import serverless

        if not serverless.authorized(dict(self.headers.items())):
            return self._send(401, {"error": "send the cron secret as a Bearer token, or the dashboard login"})
        params = dict(parse_qsl(urlsplit(self.path).query))
        status, body = serverless.handle(params.pop("op", default_op), params)
        self._send(status, body)

    def _send(self, status: int, body: dict) -> None:
        raw = json.dumps(body, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # Vercel Cron and pg_net call with GET
        self._run("tick")

    def do_POST(self) -> None:
        self._run("tick")

    def log_message(self, fmt, *args) -> None:  # the platform already logs requests
        return
