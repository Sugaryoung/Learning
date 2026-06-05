from fastapi import APIRouter
from .strategies import router as strategies_router
from .backtest import router as backtest_router
from .live import router as live_router
from .markets import router as markets_router

api_router = APIRouter()
api_router.include_router(strategies_router)
api_router.include_router(backtest_router)
api_router.include_router(live_router)
api_router.include_router(markets_router)
