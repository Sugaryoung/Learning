from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
from .base import BaseStrategy, Signal, SignalType


class BollingerBandStrategy(BaseStrategy):
    name = "布林带策略"
    description = "价格突破布林带下轨买入，突破上轨卖出"
    params = {"period": 20, "std_dev": 2.0}

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params)
        self.upper_band = None
        self.middle_band = None
        self.lower_band = None

    def init(self, data: pd.DataFrame) -> None:
        self._data = data
        period = self.get_param("period")
        std_dev = self.get_param("std_dev")
        self.middle_band = data["close"].rolling(window=period).mean()
        std = data["close"].rolling(window=period).std()
        self.upper_band = self.middle_band + std_dev * std
        self.lower_band = self.middle_band - std_dev * std

    def next(self, bar: Dict[str, Any], portfolio: Dict[str, Any]) -> Signal:
        idx = bar.get("index", 0)
        period = self.get_param("period")

        if idx < period:
            return Signal(SignalType.HOLD, reason="数据不足，等待布林带计算")

        current_price = bar.get("close", 0)
        has_position = portfolio.get("has_position", False)
        upper = self.upper_band.iloc[idx]
        lower = self.lower_band.iloc[idx]
        middle = self.middle_band.iloc[idx]

        if not has_position and current_price < lower:
            return Signal(
                SignalType.BUY,
                price=current_price,
                reason=f"触及下轨买入: price={current_price:.2f} < lower={lower:.2f}",
                timestamp=bar.get("timestamp", ""),
            )

        if has_position and current_price > upper:
            return Signal(
                SignalType.SELL,
                price=current_price,
                reason=f"触及上轨卖出: price={current_price:.2f} > upper={upper:.2f}",
                timestamp=bar.get("timestamp", ""),
            )

        return Signal(SignalType.HOLD, reason="价格在布林带内，无信号")
