from .base import BaseStrategy, Signal, SignalType
from .sma_cross import SMACrossStrategy
from .rsi import RSIStrategy
from .bollinger import BollingerBandStrategy

STRATEGY_REGISTRY = {
    "sma_cross": SMACrossStrategy,
    "rsi": RSIStrategy,
    "bollinger": BollingerBandStrategy,
}


def get_strategy_class(strategy_type: str):
    return STRATEGY_REGISTRY.get(strategy_type)


def list_strategies():
    result = []
    for key, cls in STRATEGY_REGISTRY.items():
        result.append(
            {
                "type": key,
                "name": cls.name,
                "description": cls.description,
                "default_params": cls.get_default_params(),
            }
        )
    return result


__all__ = [
    "BaseStrategy",
    "Signal",
    "SignalType",
    "SMACrossStrategy",
    "RSIStrategy",
    "BollingerBandStrategy",
    "STRATEGY_REGISTRY",
    "get_strategy_class",
    "list_strategies",
]
