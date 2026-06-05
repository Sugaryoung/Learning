from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..models.database import get_db, StrategyConfig
from ..strategies import list_strategies as list_builtin_strategies, get_strategy_class

router = APIRouter(prefix="/strategies", tags=["策略管理"])


class StrategyCreateRequest(BaseModel):
    name: str
    strategy_type: str
    params: Optional[dict] = {}


class StrategyUpdateRequest(BaseModel):
    name: Optional[str] = None
    params: Optional[dict] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    strategy_type: str
    params: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@router.get("/builtin")
def get_builtin_strategies():
    return list_builtin_strategies()


@router.get("/code/{strategy_type}")
def get_strategy_code(strategy_type: str):
    cls = get_strategy_class(strategy_type)
    if not cls:
        raise HTTPException(status_code=404, detail="Strategy not found")
    import inspect
    return {
        "strategy_type": strategy_type,
        "name": cls.name,
        "description": cls.description,
        "code": inspect.getsource(cls),
    }


@router.get("", response_model=List[StrategyResponse])
def list_strategies(db: Session = Depends(get_db)):
    return db.query(StrategyConfig).order_by(StrategyConfig.created_at.desc()).all()


@router.post("", response_model=StrategyResponse)
def create_strategy(req: StrategyCreateRequest, db: Session = Depends(get_db)):
    cls = get_strategy_class(req.strategy_type)
    if not cls:
        raise HTTPException(status_code=400, detail=f"Unknown strategy type: {req.strategy_type}")

    import json
    config = StrategyConfig(
        name=req.name,
        strategy_type=req.strategy_type,
        params=json.dumps(req.params, ensure_ascii=False),
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    config = db.query(StrategyConfig).filter(StrategyConfig.id == strategy_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return config


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, req: StrategyUpdateRequest, db: Session = Depends(get_db)):
    config = db.query(StrategyConfig).filter(StrategyConfig.id == strategy_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if req.name is not None:
        config.name = req.name
    if req.params is not None:
        import json
        config.params = json.dumps(req.params, ensure_ascii=False)
    config.updated_at = datetime.now()

    db.commit()
    db.refresh(config)
    return config


@router.delete("/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    config = db.query(StrategyConfig).filter(StrategyConfig.id == strategy_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy not found")
    db.delete(config)
    db.commit()
    return {"message": "Strategy deleted"}
