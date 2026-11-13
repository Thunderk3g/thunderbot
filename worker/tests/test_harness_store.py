"""A worker newer than its database must not lose a journal row over a bookkeeping column."""

from __future__ import annotations

import json

import pytest

from thunderbot.store import SupabaseStore


class Resp:
    def __init__(self, status: int, body=None):
        self.status_code, self._body, self.content = status, body, b"x"

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class Http:
    """A PostgREST that does not have the columns in ``missing`` yet."""

    def __init__(self, missing: set[str]):
        self.missing, self.headers, self.sent = missing, {}, []

    def post(self, url, data=None, timeout=None, **kw):
        row = json.loads(data)
        self.sent.append(row)
        for column in self.missing:
            if column in row:
                table = url.rsplit("/", 1)[1]
                return Resp(400, {"code": "PGRST204", "message": f"Could not find the '{column}' column of '{table}' in the schema cache"})
        return Resp(201)


def test_columns_the_database_lacks_are_left_out_and_the_row_is_kept(caplog):
    s = SupabaseStore("https://x.supabase.co", "sb_secret_k")
    s.http = Http({"harness_id", "net_r"})
    s.insert("signal_outcomes", {"id": "1", "symbol": "AAA", "harness_id": "abc", "net_r": -1.1, "r_multiple": -1.0})
    assert s.http.sent[-1] == {"id": "1", "symbol": "AAA", "r_multiple": -1.0}
    assert "apply the latest migration" in caplog.text
    caplog.clear()
    s.insert("signal_outcomes", {"id": "2", "symbol": "AAA", "harness_id": "abc"})
    assert s.http.sent[-1] == {"id": "2", "symbol": "AAA"} and "apply the latest migration" not in caplog.text  # said once


def test_other_errors_are_still_errors():
    s = SupabaseStore("https://x.supabase.co", "sb_secret_k")

    class Broken(Http):
        def post(self, url, data=None, timeout=None, **kw):
            return Resp(400, {"code": "23502", "message": "null value in column symbol"})

    s.http = Broken(set())
    with pytest.raises(RuntimeError):
        s.insert("signal_outcomes", {"id": "1"})
    s.http = Http(set())
    s.insert("signals", {"id": "1", "harness_id": "abc"})  # a database that has the column gets it
    assert s.http.sent[-1]["harness_id"] == "abc"
