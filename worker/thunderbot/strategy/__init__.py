from .base import Strategy
from .orb import OpeningRangeBreakout

STRATEGIES: dict[str, type[Strategy]] = {
    OpeningRangeBreakout.name: OpeningRangeBreakout,
}

__all__ = ["Strategy", "OpeningRangeBreakout", "STRATEGIES"]
