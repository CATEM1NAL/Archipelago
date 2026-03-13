from __future__ import annotations

from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData, itemType

if TYPE_CHECKING:
    from .world import PAYDAY2World

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 9, "Time Bonus", itemType.progression),
    2: itemData(IC.progression, 2, "Drill Sawgeant", itemType.progression),
    3: itemData(IC.progression, 3, "Extra Bot", itemType.progression),
    4: itemData(IC.progression, 2, "OVE9000 Saw", itemType.progression),
    5: itemData(IC.progression, 1, "ECM", itemType.progression),
    6: itemData(IC.progression, 1, "Trip Mines", itemType.progression),
    7: itemData(IC.progression_deprioritized_skip_balancing, 40, "24 Coins", itemType.progression),
    8: itemData(IC.progression, 2, "Nine Lives", itemType.progression),
    9: itemData(IC.progression, 8, "Perma-Perk", itemType.progression),
    10: itemData(IC.progression, 8, "Perma-Skill", itemType.progression),
    100: itemData(IC.progression | IC.trap, 5, "Difficulty Increase", itemType.trap),
    101: itemData(IC.progression | IC.trap, 5, "Additional Mutator", itemType.trap),
}

usefulItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 18, "Primary Weapon", itemType.weapon),
    201: itemData(IC.useful, 41, "Akimbo", itemType.weapon),
    202: itemData(IC.useful, 23, "Secondary Weapon", itemType.weapon),
    203: itemData(IC.filler, 18, "Melee Weapon", itemType.weapon),
    204: itemData(IC.filler, 5, "Throwable", itemType.weapon),
    205: itemData(IC.useful, 6, "Armor", itemType.unlock),
    206: itemData(IC.useful, 7, "Deployable", itemType.unlock),
    207: itemData(IC.useful, 8, "Skill", itemType.filler),
    208: itemData(IC.useful, 8, "Perk", itemType.filler),
    209: itemData(IC.filler, 10, "Stat Boost", itemType.filler),
}

fillerItemDict: dict[int, itemData] = {
    300: itemData(IC.filler, 0, "6 Coins", itemType.filler),
}

fillerLimitDict: dict[int, int] = {
    200: 18,
    201: 41,
    202: 23,
    203: 18,
    204: 5,
    205: 6,
    206: 7,
    207: 45,
    208: 52,
    209: 100
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(usefulItemDict)
itemDict.update(fillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class PAYDAY2Item(Item):
    game = "PAYDAY 2: Criminal Dawn"

def update_items(world: PAYDAY2World) -> None:
    progressionItemDict[1] = itemData(itemDict[1][0], world.maxTimeBonuses, *itemDict[1][2:])
    print(f"{world.player_name} has {world.maxTimeBonuses} Extra Time items.")
    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])
    progressionItemDict[4] = itemData(itemDict[4][0], world.options.saws, *itemDict[4][2:])

    progressionItemDict[100] = itemData(itemDict[100][0], (world.options.final_difficulty - 1), *itemDict[100][2:])

    optList = [world.options.primary_weapons, #200
               world.options.akimbo, #201
               world.options.secondary_weapons, #202
               world.options.melee_weapons, #203
               world.options.throwables] #206

    for i, opt in enumerate(optList):
        usefulItemDict[200+i] = itemData(itemDict[200+i][0], opt.value, *itemDict[200+i][2:])
        fillerLimitDict[200+i] -= opt

def get_random_filler_item_name(world: PAYDAY2World) -> str:
    fillerType = world.random.choice(["weapon", "upgrade"])
    if fillerType == "weapon":
        item = usefulItemDict[world.random.randint(200, 204)]
    elif fillerType == "upgrade":
        item = usefulItemDict[world.random.randint(205, 209)]
    itemId = ITEM_NAME_TO_ID[item.name]
    if fillerLimitDict[itemId] > 0:
        fillerLimitDict[itemId] -= 1
    else:
        item = world.random.choice(tuple(fillerItemDict.values()))

    return item.name

def create_all_items(world: PAYDAY2World) -> None:
    #Create progression items
    itemPool: list[PAYDAY2Item] = []
    for itemId, item in progressionItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in usefulItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool