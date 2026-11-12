"""A small gradient-boosted-tree classifier.

Training needs numpy. Prediction is plain Python over a JSON-serialisable model, so the trading path
carries no numeric dependencies and a model can be stored in a database row and read anywhere.

Model format::

    {"kind": "gbm", "features": [...], "base": log-odds, "trees": [node, ...], "calib": [a, b]}

where a node is either a leaf value (float, already scaled by the learning rate) or
``[feature_index, threshold, left, right]`` with "go left when x < threshold".
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def raw_score(model: dict[str, Any], x: Sequence[float]) -> float:
    """Log-odds before calibration."""
    z = model["base"]
    for node in model["trees"]:
        while isinstance(node, list):
            node = node[2] if x[node[0]] < node[1] else node[3]
        z += node
    return z


def predict_one(model: dict[str, Any], x: Sequence[float]) -> float:
    """Probability that the setup ends in profit after costs."""
    a, b = model.get("calib") or (1.0, 0.0)
    return _sigmoid(a * raw_score(model, x) + b)


# Training (numpy)


def _bin_edges(col, bins: int):
    import numpy as np

    qs = np.quantile(col, np.linspace(0, 1, bins + 1)[1:-1])
    return np.unique(qs)


def fit(X, y, *, n_trees: int = 120, depth: int = 3, lr: float = 0.05, min_leaf: int | None = None, l2: float = 5.0,
        subsample: float = 0.8, colsample: float = 0.8, bins: int = 24, seed: int = 7,
        features: Sequence[str] | None = None) -> dict[str, Any]:
    """Fit on a float matrix ``X`` (n, d) and 0/1 labels ``y``. Deterministic for a given seed."""
    import numpy as np

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    if n < 20:
        raise ValueError("need at least 20 rows to fit")
    min_leaf = min_leaf or max(20, n // 60)
    rng = np.random.default_rng(seed)
    edges = [_bin_edges(X[:, j], bins) for j in range(d)]
    B = np.column_stack([np.searchsorted(edges[j], X[:, j], side="right") for j in range(d)]).astype(np.int64)
    nb = [len(e) + 1 for e in edges]

    p0 = min(max(float(y.mean()), 1e-3), 1 - 1e-3)
    base = math.log(p0 / (1 - p0))
    F = np.full(n, base)
    importance = np.zeros(d)
    trees: list[Any] = []

    def build(idx, g, h, level: int, cols):
        G, H = g[idx].sum(), h[idx].sum()
        leaf = float(-G / (H + l2) * lr)
        if level >= depth or len(idx) < 2 * min_leaf:
            return leaf
        parent = G * G / (H + l2)
        best = (1e-9, -1, -1)
        for j in cols:
            if nb[j] < 2:
                continue
            bj = B[idx, j]
            gc = np.cumsum(np.bincount(bj, weights=g[idx], minlength=nb[j]))[:-1]
            hc = np.cumsum(np.bincount(bj, weights=h[idx], minlength=nb[j]))[:-1]
            cc = np.cumsum(np.bincount(bj, minlength=nb[j]))[:-1]
            ok = (cc >= min_leaf) & (len(idx) - cc >= min_leaf)
            if not ok.any():
                continue
            gain = gc * gc / (hc + l2) + (G - gc) ** 2 / (H - hc + l2) - parent
            gain[~ok] = -np.inf
            k = int(gain.argmax())
            if gain[k] > best[0]:
                best = (float(gain[k]), j, k)
        gain, j, k = best
        if j < 0:
            return leaf
        importance[j] += gain
        left = B[idx, j] <= k
        return [int(j), float(edges[j][k]), build(idx[left], g, h, level + 1, cols),
                build(idx[~left], g, h, level + 1, cols)]

    def apply(node, idx):
        out = np.empty(len(idx))
        stack = [(node, np.arange(len(idx)))]
        while stack:
            nd, where = stack.pop()
            if not isinstance(nd, list):
                out[where] = nd
                continue
            go_left = X[idx[where], nd[0]] < nd[1]
            stack.append((nd[2], where[go_left]))
            stack.append((nd[3], where[~go_left]))
        return out

    everything = np.arange(n)
    for _ in range(n_trees):
        p = 1.0 / (1.0 + np.exp(-F))
        g, h = p - y, np.maximum(p * (1 - p), 1e-6)
        rows = np.sort(rng.choice(n, size=max(2 * min_leaf, int(n * subsample)), replace=False)) if subsample < 1 else everything
        cols = np.sort(rng.choice(d, size=max(1, int(round(d * colsample))), replace=False)) if colsample < 1 else np.arange(d)
        tree = build(rows, g, h, 0, cols)
        trees.append(tree)
        F += apply(tree, everything)

    total = importance.sum()
    names = list(features) if features is not None else [f"f{j}" for j in range(d)]
    return {
        "kind": "gbm", "features": names, "base": base, "trees": trees, "calib": [1.0, 0.0],
        "importance": {names[j]: round(float(importance[j] / total), 4) if total > 0 else 0.0 for j in range(d)},
        "params": {"n_trees": n_trees, "depth": depth, "lr": lr, "min_leaf": int(min_leaf), "l2": l2},
    }


def raw_scores(model: dict[str, Any], X):
    import numpy as np

    X = np.asarray(X, dtype=float)
    out = np.full(len(X), model["base"])
    for tree in model["trees"]:
        stack = [(tree, np.arange(len(X)))]
        while stack:
            nd, where = stack.pop()
            if not isinstance(nd, list):
                out[where] += nd
                continue
            go_left = X[where, nd[0]] < nd[1]
            stack.append((nd[2], where[go_left]))
            stack.append((nd[3], where[~go_left]))
    return out


def platt(z, y, iters: int = 30) -> list[float]:
    """Fit p = sigmoid(a*z + b) by Newton's method; corrects a model that is over- or under-confident."""
    import numpy as np

    z, y = np.asarray(z, dtype=float), np.asarray(y, dtype=float)
    a, b = 1.0, 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(a * z + b)))
        w = np.maximum(p * (1 - p), 1e-6)
        ga, gb = ((p - y) * z).sum(), (p - y).sum()
        haa, hab, hbb = (w * z * z).sum() + 1e-6, (w * z).sum(), w.sum() + 1e-6
        det = haa * hbb - hab * hab
        if abs(det) < 1e-12:
            break
        da, db = (hbb * ga - hab * gb) / det, (haa * gb - hab * ga) / det
        a, b = a - da, b - db
        if abs(da) + abs(db) < 1e-8:
            break
    if not (math.isfinite(a) and math.isfinite(b)) or a <= 0:
        return [1.0, 0.0]
    return [float(a), float(b)]


def auc(y, score) -> float | None:
    """Area under the ROC curve (0.5 = no better than chance). None when only one class is present."""
    import numpy as np

    y, score = np.asarray(y, dtype=float), np.asarray(score, dtype=float)
    pos, neg = int(y.sum()), int(len(y) - y.sum())
    if pos == 0 or neg == 0:
        return None
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score))
    sorted_scores = score[order]
    i = 0
    while i < len(score):  # average ranks over ties
        j = i
        while j + 1 < len(score) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((ranks[y == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))
