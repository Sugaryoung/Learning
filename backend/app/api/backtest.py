import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..models.database import get_db, BacktestRecord, TradeLog
from ..backtest.task_manager import backtest_manager

router = APIRouter(prefix="/backtest", tags=["回测管理"])


class BacktestRunRequest(BaseModel):
    strategy_type: str
    symbol: str = "000001.SZ"
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    initial_cash: float = 100000.0
    commission_rate: float = 0.00025
    slippage: float = 0.01
    params: Optional[dict] = {}


@router.post("/run")
def run_backtest(req: BacktestRunRequest, db: Session = Depends(get_db)):
    config = {
        "strategy_type": req.strategy_type,
        "symbol": req.symbol,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "initial_cash": req.initial_cash,
        "commission_rate": req.commission_rate,
        "slippage": req.slippage,
        "params": req.params or {},
    }

    task_id = backtest_manager.submit_task(config)

    record = BacktestRecord(
        task_id=task_id,
        strategy_type=req.strategy_type,
        symbol=req.symbol,
        start_date=req.start_date,
        end_date=req.end_date,
        initial_cash=req.initial_cash,
        status="pending",
    )
    db.add(record)
    db.commit()

    return {"task_id": task_id, "status": "pending"}


@router.get("/result/{task_id}")
def get_backtest_result(task_id: str, db: Session = Depends(get_db)):
    task = backtest_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    record = db.query(BacktestRecord).filter(BacktestRecord.task_id == task_id).first()

    if task["status"] == "completed":
        result = task["result"]
        if record and record.status != "completed":
            record.status = "completed"
            record.total_return = result.get("total_return", 0)
            record.annualized_return = result.get("annualized_return", 0)
            record.max_drawdown = result.get("max_drawdown", 0)
            record.sharpe_ratio = result.get("sharpe_ratio", 0)
            record.win_rate = result.get("win_rate", 0)
            db.commit()

            for trade in result.get("trades", []):
                log = TradeLog(
                    backtest_id=record.id,
                    timestamp=trade["timestamp"],
                    action=trade["action"],
                    price=trade["price"],
                    quantity=trade["quantity"],
                    amount=trade["amount"],
                    commission=trade["commission"],
                    profit=trade.get("profit", 0),
                )
                db.add(log)
            db.commit()

        return {"task_id": task_id, "status": "completed", "result": result}

    elif task["status"] == "failed":
        if record:
            record.status = "failed"
            db.commit()
        return {"task_id": task_id, "status": "failed", "result": task["result"]}

    return {"task_id": task_id, "status": task["status"]}


@router.get("/history")
def get_backtest_history(db: Session = Depends(get_db)):
    records = (
        db.query(BacktestRecord)
        .order_by(BacktestRecord.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": r.id,
            "task_id": r.task_id,
            "strategy_type": r.strategy_type,
            "symbol": r.symbol,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "initial_cash": r.initial_cash,
            "total_return": r.total_return,
            "annualized_return": r.annualized_return,
            "max_drawdown": r.max_drawdown,
            "sharpe_ratio": r.sharpe_ratio,
            "win_rate": r.win_rate,
            "status": r.status,
            "created_at": str(r.created_at),
        }
        for r in records
    ]
