"""The portfolio engine: what stop means, order ids, part fills, how orders are carried out, what is really
held, drift corridors, deposits and the tax year."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta

import pytest

from thunderbot import daily
from thunderbot.broker.groww import holdings_reader, read_holdings
from thunderbot.broker.refs import delivery_ref
from thunderbot.clock import IST, MarketClock
from thunderbot.config import Settings
from thunderbot.invest import COMMANDS_KEY, MODE_KEY, STATE_KEY, InvestRunner
from thunderbot.models import Order, OrderStatus
from thunderbot.store import CompositeStore, SQLiteStore

WED = datetime(2026, 10, 21, 15, 12, tzinfo=IST)  # a Wednesday, two minutes after the daily check


class Px:
    """Live prices: one default, with per-symbol exceptions that a test can change."""

    def __init__(self, default: float = 200.0, **px: float) -> None:
        self.default, self.px, self.calls = default, dict(px), []

    def ltp(self, symbols):
        self.calls.append(sorted(symbols))
        return {s: self.px.get(s, self.default) for s in symbols}


def history_for(quotes: Px):
    """Daily closes that drift up gently and end at each symbol's live price, so no price check trips."""
    def history(symbols, start, end):
        days, d = [], start
        while d <= end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        n = len(days)
        return {s: {d: quotes.px.get(s, quotes.default) * 1.001 ** (i - n + 1) for i, d in enumerate(days)} for s in symbols}
    return history


def make(tmp_path, now=WED, quotes: Px | None = None, start=True, **kw):
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    clock = [now]
    quotes = quotes or Px()
    r = InvestRunner(store, quotes, MarketClock(), capital=kw.pop("capital", 300_000), history=history_for(quotes),
                     now_fn=lambda: clock[0], sleep_fn=lambda s: None, run_at=time(15, 10), **kw)
    if start:
        store.set_control("trading_enabled", True)
    return store, r, clock, quotes


def command(store, cmd: str, **fields) -> None:
    items = (store.get_control().get(COMMANDS_KEY) or {}).get("items") or []
    store.set_control(COMMANDS_KEY, {"items": [*items, {"id": len(items) + 1, "cmd": cmd, **fields}]})


def portfolio(store) -> dict:
    return store.get_control()["heartbeat"]["portfolio"]


def state(store) -> dict:
    return store.get_control()[STATE_KEY]


# 1. Stop keeps the holdings; selling everything is its own command


def test_stop_never_sells_and_sell_all_does(tmp_path):
    store, r, clock, _ = make(tmp_path)
    r.tick()
    held = {s: lot["qty"] for s, lot in state(store)["lots"].items()}
    assert set(held) == {"NIFTYBEES", "JUNIORBEES", "GOLDBEES"}

    store.set_control("trading_enabled", False)
    clock[0] = WED + timedelta(days=1)
    assert r.tick()["did"] == "stopped (holdings kept)"
    assert {s: lot["qty"] for s, lot in state(store)["lots"].items()} == held
    assert not [o for o in store.local.rows("orders") if o["side"] == "SELL"]

    command(store, "sell_all")
    clock[0] = WED + timedelta(days=1, minutes=5)
    assert r.tick()["did"] == "sold everything (at your request)"
    st = state(store)
    assert st["lots"] == {} and st["cash"] > 299_000 and "sell_all" not in st
    assert {t["exit_reason"] for t in store.local.rows("trades")} == {"sell_all"}
    assert r.tick()["did"] == "stopped (holdings kept)"  # the command ran once; nothing more happens


# 2. Order reference ids


@pytest.mark.parametrize("symbol", ["M&M", "BAJAJ-AUTO", "ITC", "NAM-INDIA", "L&TFH"])
def test_delivery_reference_ids_are_letters_and_digits_whatever_the_symbol(symbol):
    ref = delivery_ref(date(2026, 10, 21), "2026-10-21:rebalance", symbol, "BUY")
    assert re.fullmatch(r"[a-z0-9]{8,20}", ref) and len(ref) == 18 and ref.startswith("tb261021")
    assert ref == delivery_ref(date(2026, 10, 21), "2026-10-21:rebalance", symbol, "buy")  # the same order, the same id
    others = {delivery_ref(date(2026, 10, 21), "2026-10-21:rebalance", symbol, "SELL"),
              delivery_ref(date(2026, 10, 21), "2026-10-21:rebalance", symbol, "BUY", attempt=1),
              delivery_ref(date(2026, 10, 21), "2026-10-21:deposit", symbol, "BUY"),
              delivery_ref(date(2026, 10, 22), "2026-10-21:rebalance", symbol, "BUY")}
    assert ref not in others and len(others) == 4


# 3. A part-filled live order is booked for the part that filled


class HalfFills:
    """A broker whose orders fill by half and then sit there."""

    name = "fake"

    def __init__(self) -> None:
        self.reqs, self.cancelled = [], []

    def place_order(self, req):
        self.reqs.append(req)
        return Order(f"O{len(self.reqs)}", req, OrderStatus.PENDING)

    def _order(self, oid, status):
        req = self.reqs[int(oid[1:]) - 1]
        return Order(oid, req, status, filled_qty=req.qty // 2, avg_price=200.4)

    def order_status(self, oid):
        return self._order(oid, OrderStatus.PARTIAL)

    def cancel_order(self, oid):
        self.cancelled.append(oid)
        return self._order(oid, OrderStatus.CANCELLED)


def test_a_part_filled_live_order_books_what_filled_and_cancels_the_rest(tmp_path):
    broker = HalfFills()
    store, r, _, _ = make(tmp_path, broker=broker, mode="live")
    assert r.tick()["did"].startswith("rebalanced")
    st = state(store)
    assert len(broker.reqs) == 3 and len(broker.cancelled) == 3
    for req in broker.reqs:
        assert st["lots"][req.symbol]["qty"] == req.qty // 2  # the portfolio holds what filled, no more
        assert re.fullmatch(r"[a-z0-9]{8,20}", req.reference_id)
    assert len({req.reference_id for req in broker.reqs}) == 3
    rows = store.local.rows("orders")
    assert all(o["filled_qty"] == o["qty"] // 2 and o["status"] == "CANCELLED" for o in rows)
    assert len([e for e in store.local.rows("events") if e["kind"] == "partial_fill"]) == 3
    spent = sum(lot["cost"] for lot in st["lots"].values())
    assert st["cash"] == pytest.approx(300_000 - spent, abs=0.01)
    assert store.get_control()["heartbeat"]["mode"] == "live" and portfolio(store)["exec_mode"] == "auto"


# 4. How orders are carried out


class NeverCalled:
    """A broker that must not be touched."""

    name = "boom"

    def __getattr__(self, name):
        raise AssertionError(f"the broker was called ({name})")


ROWS = [{"symbol": "NIFTYBEES", "qty": 100, "avg_price": 180.0, "since": "2024-06-03"},
        {"symbol": "GOLDBEES", "qty": 300, "avg_price": 190.0},
        {"symbol": "RELIANCE", "qty": 10, "avg_price": 1200.0}]


def test_guided_mode_publishes_a_basket_and_sends_nothing_to_the_broker(tmp_path):
    store, r, clock, _ = make(tmp_path, broker=NeverCalled())  # started for paper: real orders are not allowed here
    store.set_control(MODE_KEY, "guided")
    command(store, "import_holdings", rows=ROWS)
    command(store, "deposit", amount=100_000)
    out = r.tick()
    assert out["did"].startswith("basket published") and out["exec"] == "guided"
    p = portfolio(store)
    # The owner arrived with holdings, so the first step sells nothing: it only spends the new money.
    assert p["exec_mode"] == "guided" and p["basket"]["status"] == "open" and p["basket"]["reason"] == "deposit"
    orders = {o["symbol"]: o for o in p["basket"]["orders"]}
    # What is held: Nifty 20,000, gold 60,000, cash 1,00,000. Next 50 is furthest short (60,300), so it is filled
    # first; what is left buys 195 shares of Nifty. The budget allows for every order filling at its limit.
    assert set(orders) == {"NIFTYBEES", "JUNIORBEES"} and all(o["side"] == "BUY" for o in orders.values())
    assert orders["NIFTYBEES"]["qty"] == 195 and orders["NIFTYBEES"]["limit"] == 201.0 and "target" in orders["NIFTYBEES"]["why"]
    assert sum(o["value"] for o in orders.values()) <= 100_000
    assert store.local.rows("orders") == []  # nothing placed, on paper or anywhere else
    assert {h["symbol"] for h in p["holdings"]} == {"NIFTYBEES", "GOLDBEES"}  # the plan's part of what is really held
    outside = [h for h in p["actual"]["holdings"] if not h["in_plan"]]
    assert [h["symbol"] for h in outside] == ["RELIANCE"] and p["actual"]["outside_plan_value"] == 12_000
    assert p["actual"]["source"] == "manual"

    # The owner places it and says so. The typed-in list is updated; the stock outside the plan is untouched.
    command(store, "basket_done", basket=p["basket"]["id"])
    clock[0] = WED + timedelta(days=1)
    r.tick()
    p = portfolio(store)
    assert p["basket"]["status"] == "reconciled" and p["basket"]["reconciled_at"]
    rows = {x["symbol"]: x for x in state(store)["actual"]["rows"]}
    assert rows["NIFTYBEES"]["qty"] == 295 and rows["JUNIORBEES"]["qty"] == orders["JUNIORBEES"]["qty"]
    assert rows["GOLDBEES"]["qty"] == 300 and rows["RELIANCE"]["qty"] == 10
    booked = store.local.rows("orders")
    assert {o["broker"] for o in booked} == {"manual"} and {o["mode"] for o in booked} == {"live"}
    assert p["cash"] < 5_000 and p["last_plan"]["orders"]


def test_holdings_the_owner_brought_are_not_sold_on_day_one(tmp_path):
    """Far over target in one fund: the first check records the target and proposes no sale."""
    store, r, clock, _ = make(tmp_path, broker=NeverCalled())
    store.set_control(MODE_KEY, "guided")
    command(store, "import_holdings", rows=[{"symbol": "NIFTYBEES", "qty": 1000, "avg_price": 150.0, "since": "2024-06-03"},
                                            {"symbol": "GOLDBEES", "qty": 100, "avg_price": 190.0}])
    r.tick()
    p = portfolio(store)
    assert not p.get("basket") or all(o["side"] == "BUY" for o in p["basket"]["orders"])
    assert any(row["symbol"] == "NIFTYBEES" and row["out"] for row in p["drift"])  # it is over its band, and shown as such
    assert any("Nothing is sold now" in e["message"] for e in store.local.rows("events"))


def test_guided_mode_reconciles_against_holdings_read_from_the_broker(tmp_path):
    actual = [{"symbol": "NIFTYBEES", "qty": 500, "avg_price": 150.0}, {"symbol": "TCS", "qty": 5, "avg_price": 3000.0}]
    store, r, clock, quotes = make(tmp_path, holdings_source=lambda: [dict(x) for x in actual], strategy="index_trend",
                                   params={"liquid": 0})
    store.set_control(MODE_KEY, "guided")
    command(store, "deposit", amount=40_000)
    assert r.tick()["did"].startswith("basket published")
    p = portfolio(store)
    assert p["actual"]["source"] == "groww" and p["value"] == 500 * 200 + 40_000
    (order,) = p["basket"]["orders"]
    assert (order["symbol"], order["side"], order["qty"]) == ("NIFTYBEES", "BUY", 198)  # 40,000 budgeted for a fill at the limit, plus charges

    command(store, "basket_done", basket=p["basket"]["id"])
    clock[0] = WED + timedelta(days=1)
    r.tick()  # holdings unchanged: the basket stays open and says what is missing
    p = portfolio(store)
    assert p["basket"]["status"] == "open" and "198 to buy" in p["basket"]["mismatch"][0]

    actual[0]["qty"] = 698
    command(store, "sync_holdings")
    clock[0] = WED + timedelta(days=1, minutes=10)
    r.tick()
    p = portfolio(store)
    assert p["basket"]["status"] == "reconciled" and "mismatch" not in p["basket"]
    assert p["holdings"][0]["qty"] == 698 and p["cash"] < 1_000
    assert [h["symbol"] for h in p["actual"]["holdings"] if not h["in_plan"]] == ["TCS"]


def test_nothing_the_dashboard_writes_can_make_a_paper_worker_place_orders(tmp_path):
    store, r, clock, _ = make(tmp_path, broker=NeverCalled())
    store.set_control(MODE_KEY, "auto")  # asked for from the dashboard
    store.set_control("settings_overrides", {"live_trading_enabled": True})
    command(store, "deposit", amount=50_000)
    out = r.tick()
    p = portfolio(store)
    assert out["exec"] == "guided" and p["exec_mode"] == "guided" and "by hand" in p["exec_note"]
    assert store.get_control()["heartbeat"]["mode"] == "paper"
    command(store, "sell_all")
    command(store, "harvest", confirm=True)
    clock[0] = WED + timedelta(days=1)
    r.tick()  # NeverCalled raises if any of this reached the broker
    assert not [o for o in store.local.rows("orders") if o["broker"] not in ("paper", "manual")]

    _, rejected = Settings().with_overrides({"live_trading_enabled": True, "invest_mode": "auto", "expected_static_ip": "1.2.3.4"})
    assert set(rejected) == {"live_trading_enabled", "invest_mode", "expected_static_ip"}


def test_a_live_worker_can_be_told_to_list_orders_instead_of_placing_them(tmp_path):
    store, r, _, _ = make(tmp_path, broker=NeverCalled(), mode="live")
    store.set_control(MODE_KEY, "guided")
    command(store, "deposit", amount=90_000)
    assert r.tick()["did"].startswith("basket published")


def test_holdings_are_read_only_and_parsed_leniently():
    class Client:
        def get_holdings_for_user(self):
            return {"holdings": [{"trading_symbol": "niftybees", "quantity": 12, "average_price": 250.5},
                                 {"trading_symbol": "SOLD", "quantity": 0, "average_price": 10},
                                 {"symbol": "GOLDBEES", "net_quantity": "3", "avg_price": "99"}]}

    assert read_holdings(Client()) == [{"symbol": "NIFTYBEES", "qty": 12, "avg_price": 250.5},
                                       {"symbol": "GOLDBEES", "qty": 3, "avg_price": 99.0}]
    assert holdings_reader(None) is None and holdings_reader("key") is None  # no login configured: nothing to read


def test_a_failed_holdings_read_is_reported_once_and_never_stops_the_run(tmp_path):
    def broken():
        raise RuntimeError("Groww is down")

    store, r, clock, _ = make(tmp_path, holdings_source=broken)
    assert r.tick()["did"].startswith("rebalanced")
    clock[0] = WED + timedelta(minutes=5)
    r.tick()
    assert len([e for e in store.local.rows("events") if e["kind"] == "holdings_sync_failed"]) == 1


# 5. Drift corridors


def test_corridor_is_five_points_or_a_fifth_of_the_target_whichever_is_narrower():
    assert daily.corridor(1 / 3) == pytest.approx((1 / 3 - 0.05, 1 / 3 + 0.05))
    assert daily.corridor(0.10) == pytest.approx((0.08, 0.12))
    target = {"A": 0.5, "B": 0.4, "C": 0.1}
    assert daily.out_of_band({"A": 0.52, "B": 0.39, "C": 0.09}, target) == []
    assert daily.out_of_band({"A": 0.56, "B": 0.36, "C": 0.08}, target) == ["A", "C"]
    assert daily.out_of_band({"A": 0.5, "B": 0.4}, target) == ["C"]  # a target that is not held at all


def test_the_band_option_rebalances_on_drift_and_not_on_the_calendar():
    mix = daily.build_daily("core_mix", {"band": 1})
    assert mix.band is True and daily.build_daily("core_mix").band is False  # off unless asked for
    hist = {s: [100.0] for s in mix.weights}
    on_target = {"NIFTYBEES": 0.34, "JUNIORBEES": 0.32, "GOLDBEES": 0.34}
    drifted = {"NIFTYBEES": 0.30, "JUNIORBEES": 0.31, "GOLDBEES": 0.39}
    assert mix.target(date(2026, 3, 31), hist, on_target) == daily.KEEP  # March means nothing to the band rule
    assert isinstance(mix.target(date(2026, 7, 31), hist, drifted), dict)
    march = daily.build_daily("core_mix")
    assert march.target(date(2026, 7, 31), hist, drifted) == daily.KEEP  # the default still waits for March
    assert isinstance(march.target(date(2026, 3, 31), hist, on_target), dict)


def synthetic_prices(start: date, days: int, growth: dict[str, float]) -> daily.Prices:
    out: daily.Prices = {s: {} for s in [daily.INDEX, *growth]}
    d, i = start, 0
    while i < days:
        if d.weekday() < 5:
            out[daily.INDEX][d] = 20_000 * 1.0003 ** i
            for s, g in growth.items():
                out[s][d] = 100 * (1 + g) ** i
            i += 1
        d += timedelta(days=1)
    return out


def test_the_band_plan_can_be_backtested_against_the_march_rule():
    prices = synthetic_prices(date(2025, 4, 1), 220, {"NIFTYBEES": 0.0004, "JUNIORBEES": 0.0003, "GOLDBEES": 0.004})
    end = max(prices["NIFTYBEES"])  # ends in February: the March rule never gets its turn
    band = daily.backtest(daily.build_daily("core_mix", {"band": 1}), prices, date(2025, 4, 1), end)
    march = daily.backtest(daily.build_daily("core_mix"), prices, date(2025, 4, 1), end)
    assert march.rebalances == 1 and band.rebalances > 1  # gold's run pushes it out of its corridor
    assert max(w["GOLDBEES"] for _, w in band.weights[1:]) < 0.36


def test_drift_and_the_next_deposit_are_published_every_pass(tmp_path):
    store, r, clock, quotes = make(tmp_path)
    r.tick()
    p = portfolio(store)
    assert p["band"] == {"abs_pct": 5.0, "rel_pct": 20.0}
    assert [d["symbol"] for d in p["drift"]] == ["NIFTYBEES", "JUNIORBEES", "GOLDBEES"] and not any(d["out"] for d in p["drift"])
    gold = next(d for d in p["drift"] if d["symbol"] == "GOLDBEES")
    assert (gold["target"], gold["lo"], gold["hi"]) == (33.0, 28.0, 38.0)

    quotes.px["GOLDBEES"] = 150.0  # gold falls a quarter: its share drops out of the corridor
    clock[0] = WED + timedelta(days=1, hours=-5)
    r.tick()
    p = portfolio(store)
    gold = next(d for d in p["drift"] if d["symbol"] == "GOLDBEES")
    assert gold["out"] and gold["weight"] < 28 and p["next_deposit"]["symbol"] == "GOLDBEES" and p["next_deposit"]["short_inr"] > 10_000


# 6. Deposits: buys only


def test_a_deposit_buys_what_is_furthest_below_target_and_sells_nothing(tmp_path):
    store, r, clock, quotes = make(tmp_path)
    r.tick()
    before = {s: lot["qty"] for s, lot in state(store)["lots"].items()}
    quotes.px["GOLDBEES"] = 180.0  # gold is now the holding furthest below its share
    command(store, "deposit", amount=30_000)
    clock[0] = WED + timedelta(days=1, hours=-5)  # 10:12 the next morning: recorded, not yet invested
    r.tick()
    p = portfolio(store)
    assert p["pending_deposit"] == 30_000 and p["capital"] == 330_000 and p["cash"] > 30_000
    assert {s: lot["qty"] for s, lot in state(store)["lots"].items()} == before

    clock[0] = WED + timedelta(days=1)  # the daily check: not a rebalance day, so the deposit is all that trades
    out = r.tick()
    assert out["did"].startswith("deposit invested")
    after = {s: lot["qty"] for s, lot in state(store)["lots"].items()}
    assert all(after[s] >= before[s] for s in before) and after["GOLDBEES"] > before["GOLDBEES"]
    todays = [o for o in store.local.rows("orders") if o["purpose"] == "invest:deposit"]
    assert todays and all(o["side"] == "BUY" for o in todays)
    assert max(todays, key=lambda o: o["qty"] * o["price"])["symbol"] == "GOLDBEES"  # most of it goes where the gap is
    assert store.local.rows("trades") == []  # no sale, so no gain was realised
    p = portfolio(store)
    assert p["pending_deposit"] == 0 and p["cash"] < 2_000
    assert len(state(store)["lots"]["GOLDBEES"]["tranches"]) == 2  # each purchase keeps its own date for tax


def test_route_cash_fills_the_biggest_shortfall_first_in_whole_shares():
    values = {"A": 50_000.0, "B": 30_000.0, "C": 10_000.0}
    target = {"A": 0.4, "B": 0.4, "C": 0.2}
    buys = daily.route_cash(10_000.0, values, target, {"A": 100.0, "B": 100.0, "C": 250.0}, total=100_000.0)
    assert buys[0] == ("B", 99) and dict(buys).get("A") is None  # B is 10,000 short; A is already over its share
    assert all(isinstance(q, int) and q > 0 for _, q in buys)
    assert daily.route_cash(50.0, values, target, {"A": 100.0, "B": 100.0, "C": 250.0}, total=90_050.0) == []


def test_the_backtester_can_run_a_plan_on_deposits_alone():
    prices = synthetic_prices(date(2023, 1, 2), 520, {"NIFTYBEES": 0.0005, "JUNIORBEES": 0.0002, "GOLDBEES": 0.0009})
    start, end = date(2023, 1, 2), max(prices["NIFTYBEES"])
    sides: list[bool] = []

    class Recording(daily.DeliveryCosts):
        def order(self, value, buy, symbol=""):
            sides.append(buy)
            return super().order(value, buy, symbol)

    plan = daily.build_daily("core_mix", {"monthly_deposit": 10_000, "no_sells": 1})
    r = daily.backtest(plan, prices, start, end, capital=100_000, costs=Recording())
    months = len({(d.year, d.month) for d in prices["NIFTYBEES"]}) - 1
    dep = r.metrics()["deposits"]
    assert dep["contributed"] == 100_000 + 10_000 * months and dep["no_sells"] is True
    assert sides and all(sides)  # every order was a buy
    assert dep["final_value"] > dep["contributed"] and 5 < dep["xirr_pct"] < 40
    assert dep["benchmark_final_value"] and dep["benchmark_xirr_pct"] is not None
    # The equity line is a time-weighted index, so its growth is the assets', not the deposits'.
    assert 1.0 < r.equity[-1][1] / r.equity[0][1] < 1.6

    with_sells = daily.backtest(daily.build_daily("core_mix", {"monthly_deposit": 10_000}), prices, start, end, capital=100_000)
    assert with_sells.metrics()["deposits"]["no_sells"] is False
    assert "deposits" not in daily.backtest(daily.build_daily("core_mix"), prices, start, end, capital=100_000).metrics()


def test_xirr_matches_a_known_rate():
    flows = [(date(2024, 1, 1), -100_000.0), (date(2025, 1, 1), 110_000.0)]
    assert daily.xirr(flows) == pytest.approx(10.0, abs=0.05)
    assert daily.xirr([(date(2024, 1, 1), -1.0)]) is None


# 7. The tax year


def old_holding(store, qty=500, cost_per_share=150.0, cash=1_000.0) -> None:
    """A Nifty ETF holding bought long ago, decided and checked yesterday."""
    since = "2025-01-06T15:10:00+05:30"
    store.set_control(STATE_KEY, {
        "cash": cash, "capital": qty * cost_per_share + cash, "realized": 0.0, "decided": True, "last_run": "2026-10-20",
        "target": {"NIFTYBEES": 1.0},
        "lots": {"NIFTYBEES": {"qty": qty, "cost": qty * cost_per_share, "since": since,
                               "tranches": [{"qty": qty, "cost": qty * cost_per_share, "since": since}]}},
        "marks": {"at": "2026-10-20T15:30:00+05:30", "px": {"NIFTYBEES": 200.0}},
    })


def orders_by_day(store) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    for o in store.local.rows("orders"):
        out.setdefault(o["order_id"].split("-")[2][:8], []).append((o["symbol"], o["side"]))
    return out


def test_the_tax_year_shows_what_can_still_be_booked_tax_free(tmp_path):
    store, r, clock, _ = make(tmp_path, now=WED.replace(hour=10, minute=0), strategy="index_trend", params={"liquid": 0})
    old_holding(store)
    r.tick()
    t = portfolio(store)["tax_year"]
    assert t["fy"] == "2026-27" and t["exempt"] == 125_000 and t["remaining"] == 125_000 and t["realized_ltcg"] == 0
    assert t["harvestable_gain"] == 25_000 and t["days_left"] == (date(2027, 3, 31) - date(2026, 10, 21)).days
    (lot,) = t["lots"]
    assert (lot["symbol"], lot["qty"], lot["gain"], lot["via"]) == ("NIFTYBEES", 500, 25_000, "t_plus_1") and lot["held_days"] > 365
    assert "chartered accountant" in t["note"]


def test_a_harvest_is_capped_at_the_allowance_and_skips_short_term_purchases(tmp_path):
    store, r, _, _ = make(tmp_path, now=WED.replace(hour=10, minute=0), strategy="index_trend", params={"liquid": 0})
    old_holding(store, qty=2_000, cost_per_share=100.0)
    st = state(store)
    st["lots"]["NIFTYBEES"]["tranches"].append({"qty": 100, "cost": 100 * 120.0, "since": "2026-09-01T15:10:00+05:30"})
    st["lots"]["NIFTYBEES"]["qty"] += 100
    st["lots"]["NIFTYBEES"]["cost"] += 100 * 120.0
    store.set_control(STATE_KEY, st)
    r.tick()
    t = portfolio(store)["tax_year"]
    (lot,) = t["lots"]
    assert lot["qty"] == 1_250 and lot["gain"] == 125_000  # Rs 100 a share: 1,250 shares fill the allowance
    assert t["harvestable_gain"] == 200_000  # the recent purchase is short-term and is not counted


def test_a_harvest_sells_one_day_and_buys_back_the_next_never_both_on_one(tmp_path):
    store, r, clock, _ = make(tmp_path, now=WED.replace(hour=10, minute=0), strategy="index_trend", params={"liquid": 0})
    old_holding(store)
    command(store, "harvest")  # without confirm: refused
    r.tick()
    assert state(store)["lots"]["NIFTYBEES"]["qty"] == 500 and not store.local.rows("orders")

    command(store, "harvest", confirm=True)
    clock[0] = WED.replace(hour=10, minute=30)
    assert r.tick()["did"].startswith("harvest: sold")
    st = state(store)
    assert "NIFTYBEES" not in st["lots"] and st["harvest"]["rebuy"] == [{"symbol": "NIFTYBEES", "qty": 500}]
    fy = st["fy_gains"]["2026"]
    assert 24_800 < fy["ltcg"] < 25_000 and fy["stcg"] == 0  # the gain, less the sale's charges
    assert portfolio(store)["tax_year"]["remaining"] == pytest.approx(125_000 - fy["ltcg"], abs=0.01)

    clock[0] = WED  # 15:12 the same day: the daily check must not buy the ticker back
    assert r.tick()["did"] == "postponed: a harvest order was booked today"
    clock[0] = WED + timedelta(days=1, hours=-5)
    assert r.tick()["did"] == "harvest: bought back"
    st = state(store)
    lot = st["lots"]["NIFTYBEES"]
    assert 495 <= lot["qty"] <= 500 and "harvest" not in st
    assert lot["cost"] / lot["qty"] > 199  # the cost basis has stepped up from 150 to today's price
    assert lot["tranches"][0]["since"].startswith("2026-10-22")
    clock[0] = WED + timedelta(days=1)
    r.tick()  # the daily check the day after: also kept clear of the buy-back
    for day, legs in orders_by_day(store).items():
        for symbol in {s for s, _ in legs}:
            assert len({side for s, side in legs if s == symbol}) == 1, f"{symbol} was bought and sold on {day}"


def test_a_twin_harvest_swaps_funds_on_the_day_and_counts_the_twin_toward_the_plan(tmp_path):
    store, r, clock, _ = make(tmp_path, now=WED.replace(hour=10, minute=0), strategy="index_trend", params={"liquid": 0},
                              harvest_via="twin")
    old_holding(store)
    r.tick()
    (lot,) = portfolio(store)["tax_year"]["lots"]
    assert lot["via"] == "twin" and lot["twin"] == daily.HARVEST_TWINS["NIFTYBEES"] == "SETFNIF50"
    command(store, "harvest", confirm=True)
    clock[0] = WED.replace(hour=10, minute=30)
    r.tick()
    st = state(store)
    assert set(st["lots"]) == {"SETFNIF50"} and st["aliases"] == {"SETFNIF50": "NIFTYBEES"} and "harvest" not in st
    assert sorted(orders_by_day(store)["20261021"]) == [("NIFTYBEES", "SELL"), ("SETFNIF50", "BUY")]  # never the same ticker
    # The next check sees the Nifty share as full: it neither sells the twin nor buys the original.
    clock[0] = WED + timedelta(days=1)
    r.tick()
    assert set(state(store)["lots"]) == {"SETFNIF50"}
    assert len(store.local.rows("orders")) == 2
    p = portfolio(store)
    assert p["drift"][0]["symbol"] == "NIFTYBEES" and p["drift"][0]["weight"] > 98  # the twin counts toward the Nifty share


def test_in_guided_mode_a_harvest_is_a_basket_and_the_buy_back_waits_for_it(tmp_path):
    store, r, clock, _ = make(tmp_path, now=WED.replace(hour=10, minute=0), strategy="index_trend", params={"liquid": 0})
    store.set_control(MODE_KEY, "guided")
    command(store, "import_holdings", rows=[{"symbol": "NIFTYBEES", "qty": 500, "avg_price": 150.0, "since": "2025-01-06"}])
    r.tick()
    assert portfolio(store)["tax_year"]["lots"][0]["qty"] == 500
    command(store, "harvest", confirm=True)
    clock[0] = WED.replace(hour=10, minute=30)
    r.tick()
    b = portfolio(store)["basket"]
    assert b["reason"] == "harvest" and [(o["symbol"], o["side"]) for o in b["orders"]] == [("NIFTYBEES", "SELL")]
    clock[0] = WED + timedelta(days=1, hours=-5)
    r.tick()  # the sale has not been placed: no buy-back basket yet
    assert portfolio(store)["basket"]["id"] == b["id"]
    command(store, "basket_done", basket=b["id"])
    clock[0] = WED + timedelta(days=1, hours=-4)
    r.tick()
    b2 = portfolio(store)["basket"]
    assert b2["reason"] == "harvest_rebuy" and [(o["symbol"], o["side"]) for o in b2["orders"]] == [("NIFTYBEES", "BUY")]
    assert state(store)["guided"]["fy_gains"]["2026"]["ltcg"] > 24_000


def test_commands_can_be_queued_from_the_command_line(tmp_path, monkeypatch, capsys):
    from thunderbot.cli import main
    from thunderbot.store import build_store

    monkeypatch.setenv("TB_DATA_DIR", str(tmp_path / "var"))
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert main(["deposit", "25000"]) == 0 and main(["mode", "guided"]) == 0 and main(["sell-all"]) == 0
    assert main(["deposit", "0"]) == 2
    capsys.readouterr()
    control = build_store(tmp_path / "var", None, None).get_control()
    items = control[COMMANDS_KEY]["items"]
    assert [(c["cmd"], c.get("amount")) for c in items] == [("deposit", 25_000.0), ("sell_all", None)]
    assert items[0]["id"] < items[1]["id"] and control[MODE_KEY] == "guided" and control["trading_enabled"] is False
