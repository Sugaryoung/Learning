import uuid
import threading
from typing import Dict, Optional
from ..data.stock_handler import StockDataHandler
from ..strategies import get_strategy_class
from .engine import BacktestEngine


class BacktestTaskManager:
    def __init__(self):
        self._tasks: Dict[str, dict] = {}
        self._data_handler = StockDataHandler()

    def submit_task(self, config: dict) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "status": "pending",
            "result": None,
            "config": config,
        }
        thread = threading.Thread(
            target=self._run_backtest, args=(task_id, config), daemon=True
        )
        thread.start()
        return task_id

    def _run_backtest(self, task_id: str, config: dict):
        try:
            self._tasks[task_id]["status"] = "running"

            strategy_type = config["strategy_type"]
            strategy_params = config.get("params", {})
            symbol = config["symbol"]
            start_date = config["start_date"]
            end_date = config["end_date"]
            initial_cash = config.get("initial_cash", 100000.0)
            commission_rate = config.get("commission_rate", 0.00025)
            slippage = config.get("slippage", 0.01)

            strategy_cls = get_strategy_class(strategy_type)
            if not strategy_cls:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["result"] = {"error": f"Unknown strategy: {strategy_type}"}
                return

            strategy = strategy_cls(params=strategy_params)
            data = self._data_handler.fetch_data(symbol, start_date, end_date)

            if data.empty:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["result"] = {"error": "No data available"}
                return

            engine = BacktestEngine(
                strategy=strategy,
                initial_cash=initial_cash,
                commission_rate=commission_rate,
                slippage=slippage,
            )
            result = engine.run(data)

            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["result"] = result

        except Exception as e:
            self._tasks[task_id]["status"] = "failed"
            self._tasks[task_id]["result"] = {"error": str(e)}

    def get_task(self, task_id: str) -> Optional[dict]:
        return self._tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[str]:
        task = self._tasks.get(task_id)
        return task["status"] if task else None


backtest_manager = BacktestTaskManager()
