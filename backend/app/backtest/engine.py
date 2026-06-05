from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from ..strategies.base import BaseStrategy, Signal, SignalType


@dataclass
class TradeRecord:
    timestamp: str
    action: str
    price: float
    quantity: int
    amount: float
    commission: float
    profit: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "price": self.price,
            "quantity": self.quantity,
            "amount": round(self.amount, 2),
            "commission": round(self.commission, 2),
            "profit": round(self.profit, 2),
        }


@dataclass
class DailyRecord:
    timestamp: str
    cash: float
    position_value: float
    total_value: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "cash": round(self.cash, 2),
            "position_value": round(self.position_value, 2),
            "total_value": round(self.total_value, 2),
        }


class BacktestEngine:
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.00025,
        slippage: float = 0.01,
    ):
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage = slippage

    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        self.strategy.init(data)

        cash = self.initial_cash
        position = 0
        position_cost = 0.0
        trades: List[TradeRecord] = []
        daily_records: List[DailyRecord] = []

        for idx in range(len(data)):
            row = data.iloc[idx]
            bar = {
                "index": idx,
                "timestamp": str(row["timestamp"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }

            portfolio = {
                "cash": cash,
                "position": position,
                "has_position": position > 0,
            }

            signal = self.strategy.next(bar, portfolio)
            current_price = bar["close"]

            if signal.signal_type == SignalType.BUY and position == 0:
                exec_price = current_price + self.slippage
                max_shares = int(cash / (exec_price * 100))
                if max_shares > 0:
                    shares = max_shares * 100
                    amount = shares * exec_price
                    commission = amount * self.commission_rate
                    total_cost = amount + commission

                    if total_cost <= cash:
                        cash -= total_cost
                        position = shares
                        position_cost = amount
                        trades.append(
                            TradeRecord(
                                timestamp=bar["timestamp"],
                                action="BUY",
                                price=round(exec_price, 2),
                                quantity=shares,
                                amount=amount,
                                commission=commission,
                            )
                        )

            elif signal.signal_type == SignalType.SELL and position > 0:
                exec_price = current_price - self.slippage
                amount = position * exec_price
                commission = amount * self.commission_rate
                profit = amount - position_cost - commission
                cash += amount - commission

                trades.append(
                    TradeRecord(
                        timestamp=bar["timestamp"],
                        action="SELL",
                        price=round(exec_price, 2),
                        quantity=position,
                        amount=amount,
                        commission=commission,
                        profit=profit,
                    )
                )
                position = 0
                position_cost = 0.0

            position_value = position * current_price
            total_value = cash + position_value

            daily_records.append(
                DailyRecord(
                    timestamp=bar["timestamp"],
                    cash=cash,
                    position_value=position_value,
                    total_value=total_value,
                )
            )

        return self._calc_results(trades, daily_records)

    def _calc_results(
        self, trades: List[TradeRecord], daily_records: List[DailyRecord]
    ) -> Dict[str, Any]:
        if not daily_records:
            return {"error": "No data to backtest"}

        final_value = daily_records[-1].total_value
        total_return = (final_value - self.initial_cash) / self.initial_cash

        daily_values = pd.Series([r.total_value for r in daily_records])
        daily_returns = daily_values.pct_change().dropna()

        annualized_return = 0.0
        trading_days = len(daily_records)
        if trading_days > 1:
            annualized_return = (1 + total_return) ** (252 / trading_days) - 1

        max_drawdown = 0.0
        peak = daily_values.iloc[0]
        for val in daily_values:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_drawdown:
                max_drawdown = dd

        sharpe_ratio = 0.0
        if len(daily_returns) > 1 and daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

        win_trades = [t for t in trades if t.action == "SELL" and t.profit > 0]
        lose_trades = [t for t in trades if t.action == "SELL" and t.profit <= 0]
        total_sell_trades = len(win_trades) + len(lose_trades)
        win_rate = len(win_trades) / total_sell_trades if total_sell_trades > 0 else 0.0

        return {
            "total_return": round(total_return * 100, 2),
            "annualized_return": round(annualized_return * 100, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "win_rate": round(win_rate * 100, 2),
            "initial_cash": self.initial_cash,
            "final_value": round(final_value, 2),
            "total_trades": len(trades),
            "trades": [t.to_dict() for t in trades],
            "equity_curve": [r.to_dict() for r in daily_records],
        }
