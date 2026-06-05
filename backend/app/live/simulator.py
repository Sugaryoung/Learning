import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from ..data.stock_handler import StockDataHandler
from ..strategies import get_strategy_class
from ..strategies.base import SignalType


class LiveSimulator:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._scheduler = BackgroundScheduler()
        self._running = False
        self._task_id: Optional[str] = None
        self._data_handler = StockDataHandler()
        self._cash = 100000.0
        self._initial_cash = 100000.0
        self._position = 0
        self._position_cost = 0.0
        self._current_symbol = ""
        self._current_strategy = None
        self._signals: List[Dict[str, Any]] = []
        self._orders: List[Dict[str, Any]] = []
        self._commission_rate = 0.00025
        self._slippage = 0.01

    @property
    def is_running(self) -> bool:
        return self._running

    def start(
        self,
        strategy_type: str,
        symbol: str,
        params: dict = None,
        initial_cash: float = 100000.0,
        interval_seconds: int = 30,
    ) -> Dict[str, Any]:
        if self._running:
            return {"error": "Live simulation is already running"}

        strategy_cls = get_strategy_class(strategy_type)
        if not strategy_cls:
            return {"error": f"Unknown strategy: {strategy_type}"}

        self._current_strategy = strategy_cls(params=params or {})
        self._current_symbol = symbol
        self._cash = initial_cash
        self._initial_cash = initial_cash
        self._position = 0
        self._position_cost = 0.0
        self._signals = []
        self._orders = []

        self._scheduler.add_job(
            self._tick,
            "interval",
            seconds=interval_seconds,
            id="live_tick",
            replace_existing=True,
        )
        self._scheduler.start()
        self._running = True

        return {
            "status": "started",
            "strategy": strategy_type,
            "symbol": symbol,
            "interval_seconds": interval_seconds,
        }

    def stop(self) -> Dict[str, Any]:
        if not self._running:
            return {"error": "No running simulation"}

        self._scheduler.remove_all_jobs()
        self._scheduler.shutdown(wait=False)
        self._scheduler = BackgroundScheduler()
        self._running = False

        return {"status": "stopped"}

    def _tick(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            start = "2024-01-01"
            data = self._data_handler.fetch_data(self._current_symbol, start, today)

            if data.empty:
                return

            self._current_strategy.init(data)

            last_idx = len(data) - 1
            row = data.iloc[last_idx]
            bar = {
                "index": last_idx,
                "timestamp": str(row["timestamp"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }

            portfolio = {
                "cash": self._cash,
                "position": self._position,
                "has_position": self._position > 0,
            }

            signal = self._current_strategy.next(bar, portfolio)
            signal_dict = signal.to_dict()
            signal_dict["symbol"] = self._current_symbol
            self._signals.append(signal_dict)

            print(
                f"[{bar['timestamp']}] {self._current_symbol} "
                f"Signal: {signal.signal_type.value} - {signal.reason}"
            )

            if signal.signal_type == SignalType.BUY and self._position == 0:
                exec_price = bar["close"] + self._slippage
                max_shares = int(self._cash / (exec_price * 100))
                if max_shares > 0:
                    shares = max_shares * 100
                    amount = shares * exec_price
                    commission = amount * self._commission_rate
                    total_cost = amount + commission
                    if total_cost <= self._cash:
                        self._cash -= total_cost
                        self._position = shares
                        self._position_cost = amount
                        self._orders.append(
                            {
                                "timestamp": bar["timestamp"],
                                "symbol": self._current_symbol,
                                "action": "BUY",
                                "price": round(exec_price, 2),
                                "quantity": shares,
                                "amount": round(amount, 2),
                                "commission": round(commission, 2),
                                "status": "filled",
                            }
                        )

            elif signal.signal_type == SignalType.SELL and self._position > 0:
                exec_price = bar["close"] - self._slippage
                amount = self._position * exec_price
                commission = amount * self._commission_rate
                profit = amount - self._position_cost - commission
                self._cash += amount - commission
                self._orders.append(
                    {
                        "timestamp": bar["timestamp"],
                        "symbol": self._current_symbol,
                        "action": "SELL",
                        "price": round(exec_price, 2),
                        "quantity": self._position,
                        "amount": round(amount, 2),
                        "commission": round(commission, 2),
                        "profit": round(profit, 2),
                        "status": "filled",
                    }
                )
                self._position = 0
                self._position_cost = 0.0

        except Exception as e:
            print(f"Live tick error: {e}")

    def get_status(self) -> Dict[str, Any]:
        current_price = 0.0
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            data = self._data_handler.fetch_data(self._current_symbol, "2024-01-01", today)
            if not data.empty:
                current_price = float(data.iloc[-1]["close"])
        except Exception:
            pass

        position_value = self._position * current_price
        total_value = self._cash + position_value

        return {
            "running": self._running,
            "symbol": self._current_symbol,
            "initial_cash": self._initial_cash,
            "cash": round(self._cash, 2),
            "position": self._position,
            "position_value": round(position_value, 2),
            "total_value": round(total_value, 2),
            "pnl": round(total_value - self._initial_cash, 2),
            "pnl_pct": round(
                (total_value - self._initial_cash) / self._initial_cash * 100, 2
            ),
            "current_price": current_price,
            "signals": self._signals[-20:],
            "orders": self._orders[-20:],
        }


live_simulator = LiveSimulator()
