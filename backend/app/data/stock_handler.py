import os
from typing import Optional
import pandas as pd
import numpy as np
from .base_handler import BaseDataHandler


class StockDataHandler(BaseDataHandler):
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        csv_path = os.path.join(self.data_dir, f"{symbol}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = self.validate_ohlcv(df)
            mask = (df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)
            df = df.loc[mask].reset_index(drop=True)
            if len(df) > 0:
                return df

        return self._generate_sample_data(symbol, start_date, end_date)

    def _generate_sample_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        dates = pd.bdate_range(start=start_date, end=end_date)
        n = len(dates)
        np.random.seed(hash(symbol) % 2**31)
        price = 10.0
        close_prices = [price]
        for _ in range(1, n):
            ret = np.random.normal(0.0005, 0.02)
            price = price * (1 + ret)
            close_prices.append(round(price, 2))

        df = pd.DataFrame({"timestamp": dates})
        df["close"] = close_prices
        df["open"] = df["close"] * (1 + np.random.uniform(-0.01, 0.01, n))
        df["high"] = df[["open", "close"]].max(axis=1) * (
            1 + np.random.uniform(0, 0.015, n)
        )
        df["low"] = df[["open", "close"]].min(axis=1) * (
            1 - np.random.uniform(0, 0.015, n)
        )
        df["volume"] = np.random.randint(100000, 5000000, n)

        df["open"] = df["open"].round(2)
        df["high"] = df["high"].round(2)
        df["low"] = df["low"].round(2)
        df["volume"] = df["volume"].astype(int)

        return self.validate_ohlcv(df)

    def list_symbols(self) -> list:
        symbols = []
        if os.path.exists(self.data_dir):
            for f in os.listdir(self.data_dir):
                if f.endswith(".csv"):
                    symbols.append(f.replace(".csv", ""))
        return symbols

    def save_csv(self, symbol: str, df: pd.DataFrame) -> str:
        df = self.validate_ohlcv(df)
        csv_path = os.path.join(self.data_dir, f"{symbol}.csv")
        df.to_csv(csv_path, index=False)
        return csv_path
