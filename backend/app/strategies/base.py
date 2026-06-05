from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal:
    def __init__(
        self,
        signal_type: SignalType,
        price: float = 0.0,
        quantity: int = 0,
        reason: str = "",
        timestamp: Optional[str] = None,
    ):
        self.signal_type = signal_type
        self.price = price
        self.quantity = quantity
        self.reason = reason
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type.value,
            "price": self.price,
            "quantity": self.quantity,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


class BaseStrategy(ABC):
    name: str = "BaseStrategy"
    description: str = ""
    params: Dict[str, Any] = {}

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        if params:
            self.params = {**self.params, **params}
        self._data = None
        self._indicators = {}

    @abstractmethod
    def init(self, data) -> None:
        pass

    @abstractmethod
    def next(self, bar: Dict[str, Any], portfolio: Dict[str, Any]) -> Signal:
        pass

    def set_data(self, data) -> None:
        self._data = data

    def get_param(self, key: str, default=None):
        return self.params.get(key, default)

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        return dict(cls.params)
