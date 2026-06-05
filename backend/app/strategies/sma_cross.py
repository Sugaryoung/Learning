from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
from .base import BaseStrategy, Signal, SignalType


class SMACrossStrategy(BaseStrategy):
    name = "双均线策略"
    description = "当短均线上穿长均线买入，下穿卖出"
    params = {"short_period": 5, "long_period": 20}

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params)
        self.short_ma = None
        self.long_ma = None

    def init(self, data: pd.DataFrame) -> None:
        self._data = data
        short_p = self.get_param("short_period")
        long_p = self.get_param("long_period")
        self.short_ma = data["close"].rolling(window=short_p).mean()
        self.long_ma = data["close"].rolling(window=long_p).mean()

    def next(self, bar: Dict[str, Any], portfolio: Dict[str, Any]) -> Signal:
        idx = bar.get("index", 0)
        long_p = self.get_param("long_period")

        if idx < long_p:
            return Signal(SignalType.HOLD, reason="数据不足，等待均线计算")

        short_val = self.short_ma.iloc[idx]
        long_val = self.long_ma.iloc[idx]
        prev_short = self.short_ma.iloc[idx - 1]
        prev_long = self.long_ma.iloc[idx - 1]

        has_position = portfolio.get("has_position", False)
        current_price = bar.get("close", 0)

        if not has_position and prev_short <= prev_long and short_val > long_val:
            return Signal(
                SignalType.BUY,
                price=current_price,
                reason=f"金叉买入: SHORT={short_val:.2f} > LONG={long_val:.2f}",
                timestamp=bar.get("timestamp", ""),
            )

        if has_position and prev_short >= prev_long and short_val < long_val:
            return Signal(
                SignalType.SELL,
                price=current_price,
                reason=f"死叉卖出: SHORT={short_val:.2f} < LONG={long_val:.2f}",
                timestamp=bar.get("timestamp", ""),
            )

        return Signal(SignalType.HOLD, reason="无信号")
