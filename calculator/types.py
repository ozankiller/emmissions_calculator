from enum import IntEnum
from typing import NamedTuple, Optional
from typing_extensions import TypedDict

TYPE_CONVERSIONS_DICT = {"miles-kilometres": 1.60934}


class Scope(IntEnum):
    DIRECT = 1
    PURCHASED = 2
    INDIRECT = 3


class Emmission(NamedTuple):
    co2e: float
    scope: Scope
    category: Optional[int]
    activity: str


class EmmissionFactor(NamedTuple):
    activity: str
    lookup_identifier: str
    unit: str
    co2e_factor: float
    scope: int
    category: Optional[int]


class GroupedEmmission(TypedDict):
    total_co2e: float
    scope: Scope
    category: Optional[int]
    activity: str
    count: int


class ClientEmmission(TypedDict):
    co2e: float
    scope: Scope
    category: Optional[int]
    activity: str
