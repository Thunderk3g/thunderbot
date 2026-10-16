from __future__ import annotations

import abc
from collections.abc import Sequence

from ..models import Candle, Signal


class Strategy(abc.ABC):
    """A deterministic signal generator.

    ``on_bar`` is called after each completed bar with *only* the bars that had
    closed by then (today's session so far, plus optional prior-day history).
    Implementations must never look at data beyond what they are given. That
    rule is what keeps backtests honest.
    """

    name: str = "base"

    @abc.abstractmethod
    def on_bar(
        self,
        symbol: str,
        session_bars: Sequence[Candle],
        prior_bars: Sequence[Candle] = (),
    ) -> Signal | None:
        """Return a new entry signal, or None."""

    def reset_day(self) -> None:  # noqa: B027 - optional hook, deliberately not abstract
        """Called at the start of each session to clear per-day state."""
