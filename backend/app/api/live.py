from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..live.simulator import live_simulator

router = APIRouter(prefix="/live", tags=["实盘模拟"])


class LiveStartRequest(BaseModel):
    strategy_type: str
    symbol: str = "000001.SZ"
    params: Optional[dict] = {}
    initial_cash: float = 100000.0
    interval_seconds: int = 30


@router.post("/start")
def start_live(req: LiveStartRequest):
    result = live_simulator.start(
        strategy_type=req.strategy_type,
        symbol=req.symbol,
        params=req.params or {},
        initial_cash=req.initial_cash,
        interval_seconds=req.interval_seconds,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/stop")
def stop_live():
    result = live_simulator.stop()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/status")
def get_live_status():
    return live_simulator.get_status()
