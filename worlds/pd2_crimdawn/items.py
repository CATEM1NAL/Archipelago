from __future__ import annotations
from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData

if TYPE_CHECKING:
    from .world import CrimDawnWorld

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 0, "Time Bonus"),
    2: itemData(IC.progression, 2, "Drill Sawgeant"),
    3: itemData(IC.progression, 3, "Extra Bot"),
    4: itemData(IC.progression, 2, "Nine Lives"),
    5: itemData(IC.progression, 7, "Perma-Perk"),
    6: itemData(IC.progression, 7, "Perma-Skill")
}

trapItemDict: dict[int, itemData] = {
}

usefulItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 40, "24 Coins"),
    201: itemData(IC.useful, 2, "OVE9000 Saw"),
    202: itemData(IC.useful, 13, "Skill"),
    203: itemData(IC.useful, 13, "Perk"),
}

fillerItemDict: dict[int, itemData] = {
    300: itemData(IC.filler, 18, "Primary Weapon"),
    301: itemData(IC.filler, 41, "Akimbo"),
    302: itemData(IC.filler, 23, "Secondary Weapon"),
    303: itemData(IC.filler, 18, "Melee Weapon"),
    304: itemData(IC.filler, 5, "Throwable"),
    305: itemData(IC.filler, 6, "Armor"),
    306: itemData(IC.filler, 9, "Deployable"),
    307: itemData(IC.filler, 13, "Stat Boost")
}

infFillerItemDict: dict[int, itemData] = {
    400: itemData(IC.filler, 0, "6 Coins")
}

fillerLimitDict: dict[int, int] = {
    300: 18,
    301: 41,
    302: 23,
    303: 18,
    304: 5,
    305: 6,
    306: 7,
    307: 52
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(trapItemDict)
itemDict.update(usefulItemDict)
itemDict.update(fillerItemDict)
itemDict.update(infFillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class CrimDawnItem(Item):
    game = "PAYDAY 2: Criminal Dawn"

def update_items(world: CrimDawnWorld) -> None:
    progressionItemDict[1] = itemData(itemDict[1][0], world.maxTimeBonuses, *itemDict[1][2:])
    world.logger.info(f"{world.player_name} has {world.maxTimeBonuses} Time Bonuses.")
    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])
    progressionItemDict[4] = itemData(itemDict[4][0], world.options.saws, *itemDict[4][2:])

    optList = [world.options.primary_weapons, #300
               world.options.akimbo, #301
               world.options.secondary_weapons, #302
               world.options.melee_weapons, #303
               world.options.throwables] #304

    for i, opt in enumerate(optList):
        fillerItemDict[300+i] = itemData(itemDict[300+i][0], opt.value, *itemDict[300+i][2:])
        fillerLimitDict[300+i] -= opt

def get_random_filler_item_name(world: CrimDawnWorld) -> str:
    fillerType = world.random.choice(["weapon", "upgrade"])
    if fillerType == "weapon": item = fillerItemDict[world.random.randint(300, 304)]
    elif fillerType == "upgrade": item = fillerItemDict[world.random.randint(305, 307)]

    itemId = ITEM_NAME_TO_ID[item.name]

    if fillerLimitDict[itemId] > 0: fillerLimitDict[itemId] -= 1
    else: item = world.random.choice(tuple(infFillerItemDict.values()))

    return item.name

def create_all_items(world: CrimDawnWorld) -> None:
    #Create progression items
    itemPool: list[CrimDawnItem] = []
    for itemId, item in progressionItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in trapItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in usefulItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    #Make sure filler doesn't go over number of locations
    maxItemCount = 0
    for itemId, item in fillerItemDict.items():
        maxItemCount += item.count

    while maxItemCount + len(itemPool) > len(world.multiworld.get_unfilled_locations(world.player)):
        breakCounter = 0
        for itemId, item in fillerItemDict.items():
            if item.count > 7:
                fillerItemDict[itemId] = itemData(itemDict[itemId][0], item.count - 1, *itemDict[itemId][2:])
                maxItemCount -= 1
            else:
                breakCounter += 1
        if breakCounter == 8:
            world.logger.warning(f"WARNING: {world.player_name} attempted generation of too many items!")
            break

    for itemId, item in fillerItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool