"""Walk-forward training of the setup model, with a report that says plainly whether it found an edge.

The model is always judged on days it had not seen: it is fitted on all days before a block of five,
scores that block, then moves on. Only those out-of-sample scores feed the report. The model that is
saved is then fitted on every day.

Sixty days of 5-minute bars is little data and markets change, so a good report here is a reason to
keep paper trading, not proof. The report carries a verdict in words for that reason.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from ..clock import now_ist
from ..config import Settings
from ..models import Candle
from . import INDEX, features, gbm
from .dataset import Sample, build_samples

MODEL_NAME = "intraday_setups"
TOP_SHARES = (1.0, 0.5, 0.3, 0.2, 0.1)  # the report shows the best-scored half, 30%, 20% and 10% of setups
LEARN_SHARE = 0.3  # paper learning trades the best-scored 30%
MIN_DAYS, MIN_SAMPLES, STEP_DAYS = 20, 300, 5
DEFAULT_MIN_STOP_PCT = 0.8
# Deliberately small and heavily regularised: a few thousand noisy examples cannot support more, and a
# larger model scored worse than chance out of sample when this was first run (12 Nov 2026).
FIT = {"n_trees": 60, "depth": 2, "lr": 0.05, "l2": 20.0, "colsample": 0.6}


class TrainError(ValueError):
    pass


def _stats(r: list[float]) -> dict[str, Any]:
    n = len(r)
    if n == 0:
        return {"n": 0, "win_pct": None, "avg_r": None, "total_r": 0.0, "t": None}
    mean = sum(r) / n
    var = sum((x - mean) ** 2 for x in r) / (n - 1) if n > 1 else 0.0
    t = mean / math.sqrt(var / n) if var > 0 else None
    return {"n": n, "win_pct": round(sum(1 for x in r if x > 0) / n * 100, 1), "avg_r": round(mean, 3),
            "total_r": round(sum(r), 2), "t": None if t is None else round(t, 2)}


def _verdict(best: dict[str, Any], everything: dict[str, Any], auc: float | None, strict: float | None) -> tuple[str, str]:
    n, avg, t = best["n"], best["avg_r"], best["t"]
    rank = ("it cannot tell good setups from bad ones better than chance" if auc is None or auc < 0.52
            else f"it ranks setups slightly better than chance (AUC {auc:.2f})")
    if n < 30 or avg is None:
        return "too_few", (f"Only {n} out-of-sample setups in the best-scored group, too few to judge. "
                           "Keep paper trading and retrain as days accumulate.")
    if avg > 0 and t is not None and t >= 2:
        return "edge_supported", (f"The best-scored 30% of setups made {avg:+.2f}R each after costs on days the model had "
                                  f"not seen ({n} trades, t = {t}); {rank}. Encouraging on 60 days of data, not proof.")
    if avg > 0:
        return "weak_positive", (f"The best-scored 30% of setups made {avg:+.2f}R each after costs out of sample ({n} trades), "
                                 f"but that is within what luck produces (t = {t}); {rank}.")
    tail = ("No score level has been profitable, so strict mode would not trade." if strict is None
            else f"Only setups scored {strict:.2f} or higher are expected to break even.")
    return "no_edge", (f"The best-scored 30% of setups lost {avg:+.2f}R each after costs out of sample ({n} trades); every "
                       f"setup taken blindly lost {everything['avg_r']:+.2f}R. So far the model has not found a profitable group: "
                       f"{rank}. {tail}")


def train(samples: list[Sample], progress: Callable[[float], Any] = lambda p: None,
          fit_kwargs: dict[str, Any] | None = None, min_stop_pct: float = DEFAULT_MIN_STOP_PCT) -> tuple[dict[str, Any], dict[str, Any]]:
    """Returns (model, report). Raises TrainError when there is not enough history to learn from."""
    import numpy as np

    days = sorted({s.day for s in samples})
    if len(days) < MIN_DAYS or len(samples) < MIN_SAMPLES:
        raise TrainError(f"need at least {MIN_DAYS} trading days and {MIN_SAMPLES} setups to train; "
                         f"got {len(days)} days and {len(samples)} setups")
    kw = {**FIT, "min_leaf": max(40, len(samples) // 25), **(fit_kwargs or {})}
    X = np.array([s.x for s in samples], dtype=float)
    y = np.array([s.y for s in samples], dtype=float)
    r = np.array([s.r_net for s in samples], dtype=float)
    day_index = {d: i for i, d in enumerate(days)}
    day_of = np.array([day_index[s.day] for s in samples])

    start = max(15, int(len(days) * 0.4))
    blocks = list(range(start, len(days), STEP_DAYS))
    oos_z = np.full(len(samples), np.nan)
    for b, k in enumerate(blocks):
        tr, te = day_of < k, (day_of >= k) & (day_of < k + STEP_DAYS)
        if te.any() and tr.sum() >= 100:
            fold = gbm.fit(X[tr], y[tr], features=features.FEATURES, **kw)
            oos_z[te] = gbm.raw_scores(fold, X[te])
        progress(0.9 * (b + 1) / len(blocks))
    seen = ~np.isnan(oos_z)
    if seen.sum() < 50:
        raise TrainError("too few out-of-sample setups to evaluate the model")

    calib = gbm.platt(oos_z[seen], y[seen])
    oos_p = 1.0 / (1.0 + np.exp(-(calib[0] * oos_z[seen] + calib[1])))
    oos_y, oos_r = y[seen], r[seen]
    oos = [s for s, ok in zip(samples, seen, strict=True) if ok]

    # Expected result as a straight line in the score, fitted on out-of-sample trades only. Strict
    # mode trades above the score where that line crosses zero, if it ever does within the scores seen.
    slope, intercept = (float(v) for v in np.polyfit(oos_p, oos_r, 1)) if np.ptp(oos_p) > 1e-6 else (0.0, float(oos_r.mean()))
    strict = -intercept / slope if slope > 0 else None
    if strict is not None and not (0.0 < strict <= float(oos_p.max())):
        strict = None if strict > float(oos_p.max()) else max(strict, 0.0)
    learn = float(np.quantile(oos_p, 1 - LEARN_SHARE))

    everything = _stats(oos_r.tolist())
    by_share = {}
    for share in TOP_SHARES:
        cut = float(np.quantile(oos_p, 1 - share)) if share < 1 else 0.0
        by_share[f"{int(share * 100)}"] = {"floor": round(cut, 3), **_stats(oos_r[oos_p >= cut].tolist())}
    auc = gbm.auc(oos_y, oos_p)
    code, text = _verdict(by_share[f"{int(LEARN_SHARE * 100)}"], everything, auc, strict)

    by_gen: dict[str, list[float]] = defaultdict(list)
    for s in oos:
        by_gen[s.generator].append(s.r_net)
    buckets = []
    for chunk in np.array_split(np.argsort(oos_p), 5):
        if len(chunk):
            buckets.append({"p": round(float(oos_p[chunk].mean()), 3), "win_pct": round(float(oos_y[chunk].mean()) * 100, 1),
                            "avg_r": round(float(oos_r[chunk].mean()), 3), "n": int(len(chunk))})
    curve_all: dict[str, float] = defaultdict(float)
    curve_model: dict[str, float] = defaultdict(float)
    for s, p in zip(oos, oos_p, strict=True):
        curve_all[s.day.isoformat()] += s.r_net
        curve_model[s.day.isoformat()] += s.r_net if p >= learn else 0.0
    run_all = run_model = 0.0
    curve = []
    for d in sorted(curve_all):
        run_all += curve_all[d]
        run_model += curve_model[d]
        curve.append([d, round(run_model, 2), round(run_all, 2)])

    base_rate = float(oos_y.mean())
    model = gbm.fit(X, y, features=features.FEATURES, **kw)
    model["calib"] = calib
    model["setup"] = {"min_stop_pct": min_stop_pct}
    model["policy"] = {"learn": round(learn, 4), "strict": None if strict is None else round(strict, 4),
                       "ev": [round(intercept, 4), round(slope, 4)]}
    progress(1.0)
    top = sorted(model["importance"].items(), key=lambda kv: -kv[1])[:12]
    report = {
        "trained_at": now_ist().isoformat(), "days": len(days), "first_day": days[0].isoformat(), "last_day": days[-1].isoformat(),
        "setups": len(samples), "symbols": len({s.symbol for s in samples}), "min_stop_pct": min_stop_pct,
        "policy": model["policy"],
        "oos": {
            "from": days[start].isoformat(), "setups": int(seen.sum()), "auc": _round(auc),
            "brier": round(float(((oos_p - oos_y) ** 2).mean()), 4),
            "brier_base": round(float(((base_rate - oos_y) ** 2).mean()), 4),
            "base_win_pct": round(base_rate * 100, 1), "all": everything, "by_share": by_share,
            "by_generator": {g: _stats(v) for g, v in sorted(by_gen.items())}, "buckets": buckets, "curve": curve,
        },
        "verdict": code, "verdict_text": text, "importance": [[k, v] for k, v in top],
    }
    return model, report


def _round(x: float | None, nd: int = 3) -> float | None:
    return None if x is None else round(x, nd)


# Storage


def save_model(store: Any, model: dict[str, Any], report: dict[str, Any]) -> str:
    """Insert the model; the newest row for a name is the active one. Returns the new row's id."""
    from ..store import new_id

    model_id = new_id()
    store.insert("models", {"id": model_id, "name": MODEL_NAME, "report": report, "model": model})
    summary = {k: report[k] for k in ("trained_at", "days", "setups", "symbols", "policy", "min_stop_pct", "verdict", "verdict_text")}
    summary.update(id=model_id, auc=report["oos"]["auc"], best=report["oos"]["by_share"][f"{int(LEARN_SHARE * 100)}"],
                   all=report["oos"]["all"])
    store.set_control("ai_model", summary)
    return model_id


_CACHE: dict[str, dict[str, Any]] = {}


def load_active_model(store: Any, known_id: str | None = None) -> dict[str, Any] | None:
    """The active model row ({id, model, report}). A warm process reuses the copy it already has."""
    if known_id and known_id in _CACHE:
        return _CACHE[known_id]
    rows = store.select("models", {"name": MODEL_NAME}, limit=1)
    if not rows:
        return None
    row = rows[0]
    _CACHE.clear()
    _CACHE[row["id"]] = row
    return row


def run_training(settings: Settings, store: Any, symbols: list[str],
                 progress: Callable[[float], Any] = lambda p: None,
                 data: dict[str, list[Candle]] | None = None, min_stop_pct: float = DEFAULT_MIN_STOP_PCT) -> dict[str, Any]:
    """Fetch history, build the examples, train, save. Returns the report (with the model id)."""
    from .market import HISTORY_DAYS, fetch_many

    note = ""
    if data is None:
        data, _, errors = fetch_many(list(symbols) + [INDEX], settings.interval_minutes, HISTORY_DAYS, now_ist(), workers=6)
        if errors:
            note = "No history from Yahoo for: " + ", ".join(sorted(errors)) + "."
        if not any(k != INDEX for k in data):
            raise TrainError("Yahoo returned no intraday history; try again later")
    progress(0.1)
    samples = build_samples(data, settings, progress=lambda p: progress(0.1 + 0.5 * p), min_stop_pct=min_stop_pct)
    model, report = train(samples, progress=lambda p: progress(0.6 + 0.4 * p), min_stop_pct=min_stop_pct)
    report["note"] = note
    report["id"] = save_model(store, model, report)
    return report
