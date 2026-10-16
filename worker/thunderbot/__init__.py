"""Thunderbot: a deterministic trading engine for Groww with an LLM review layer.

The quant engine generates every signal. The LLM may veto a signal or shrink its
size, never create, enlarge, or re-price one. Hard risk limits in
``thunderbot.risk`` always have the final word.
"""

__version__ = "0.1.0"
