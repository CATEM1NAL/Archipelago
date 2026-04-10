from typing import NamedTuple
from BaseClasses import ItemClassification

class itemData(NamedTuple):
    classification: ItemClassification
    count: int
    name: str

class safeHouseData(NamedTuple):
    name: str
    descId: str

class gameModeData(NamedTuple):
    runLength: int
    scoreChecks: int
    safehouseTiers: int
    campaign: bool