import dataclasses
from typing import Set

@dataclasses.dataclass
class Bond:
    identifier: str
    pricing_date: str  # YYYYMMDD format
    price_quote: float

@dataclasses.dataclass 
class AnalyticEquation:
    field: str
    formula: str
    dependencies: Set[str]
    api_calls: Set[str]

class APICall:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"API({self.name})" 