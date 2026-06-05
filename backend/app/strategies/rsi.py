from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
from .base import BaseStrategy, Signal, SignalType


class RSIStrategy(BaseStrategy):
    name = "RSI策略"
    description = "RSI超买超卖策略，低于超卖线买入，高于超买线卖出"
    params = {"rsi_period": 14, "oversold": 30, "overbought": 70}

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        super().__init__(params)
        self.rsi_values = None

    def _calc_rsi(self, data: pd.Series, period: int) -> pd.Series:
        delta = data.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def init(self, data: pd.DataFrame) -> None:
        self._data = data
        period = self.get_param("rsi_period")
        self.rsi_values = self._calc_rsi(data["close"], period)

    def next(self, bar: Dict[str, Any], portfolio: Dict[str, Any]) -> Signal:
        idx = bar.get("index", 0)
        period = self.get_param("rsi_period")

        if idx < period + 1:
            return Signal(SignalType.HOLD, reason="数据不足，等待RSI计算")

        rsi_val = self.rsi_values.iloc[idx]
        oversold = self.get_param("oversold")
        overbought = self.get_param("overbought")
        has_position = portfolio.get("has_position", False)
        current_price = bar.get("close", 0)

        if not has_position and rsi_val < oversold:
            return Signal(
                SignalType.BUY,
                price=current_price,
                reason=f"RSI超卖买入: RSI={rsi_val:.2f} < {oversold}",
                timestamp=bar.get("timestamp", ""),
            )

        if has_position and rsi_val > overbought:
            return Signal(
                SignalType.SELL,
                price=current_price,
                reason=f"RSI超买卖出: RSI={rsi_val:.2f} > {overbought}",
                timestamp=bar.get("timestamp", ""),
            )

        return Signal(SignalType.HOLD, reason=f"RSI={rsi_val:.2f}, 无信号")
