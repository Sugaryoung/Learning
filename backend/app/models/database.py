import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'quant.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    params = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BacktestRecord(Base):
    __tablename__ = "backtest_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), unique=True, nullable=False)
    strategy_type = Column(String(50), nullable=False)
    symbol = Column(String(50), nullable=False)
    start_date = Column(String(20))
    end_date = Column(String(20))
    initial_cash = Column(Float, default=100000.0)
    total_return = Column(Float, default=0.0)
    annualized_return = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.now)


class TradeLog(Base):
    __tablename__ = "trade_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(Integer)
    timestamp = Column(String(50))
    action = Column(String(10))
    price = Column(Float)
    quantity = Column(Integer)
    amount = Column(Float)
    commission = Column(Float)
    profit = Column(Float, default=0.0)


class LivePosition(Base):
    __tablename__ = "live_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50))
    quantity = Column(Integer, default=0)
    avg_cost = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
