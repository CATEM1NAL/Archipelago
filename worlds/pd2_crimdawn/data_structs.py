from typing import NamedTuple
from BaseClasses import ItemClassification

class itemData(NamedTuple):
    classification: ItemClassification
    count: int
    name: str
    weight: int

class safeHouseData(NamedTuple):
    name: str
    descId: str