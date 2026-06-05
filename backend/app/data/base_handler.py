from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseDataHandler(ABC):
    @abstractmethod
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        pass

    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        df = df[required].copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df
