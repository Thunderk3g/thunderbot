"""The AI desk: intraday setups scored by an ML model and decided by an LLM, under the hard risk limits.

- ``features``  point-in-time numbers describing a setup at the bar it fired on
- ``gbm``       a small gradient-boosted-tree classifier (numpy to train, plain Python to predict)
- ``dataset``   replays the setup generators over history and labels each setup with its real outcome
- ``train``     walk-forward training and an out-of-sample report
- ``runner``    the paper desk as a function that is woken once per bar (no process to keep alive)
- ``reflect``   an end-of-day review whose lessons are shown to the LLM the next day

The order of authority never changes: generators propose, the model scores, the LLM takes or skips and
may shrink, and ``RiskManager`` has the final say on size and limits. Nothing here sets a price.
"""

INDEX = "^NSEI"  # the Nifty 50 on Yahoo; used only as market context, never traded

__all__ = ["INDEX"]
