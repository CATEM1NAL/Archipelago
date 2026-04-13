from __future__ import annotations
from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .data_structs import itemData

if TYPE_CHECKING:
    from .world import CrimDawnWorld

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 0, "Time Bonus", 100),
    2: itemData(IC.progression, 2, "Drill Sawgeant", 100),
    3: itemData(IC.progression, 3, "Extra Bot", 100),
    4: itemData(IC.progression, 2, "Nine Lives", 100),
    5: itemData(IC.progression, 7, "Perma-Perk", 100),
    6: itemData(IC.progression, 7, "Perma-Skill", 100)
}

usefulItemDict: dict[int, itemData] = {
    200: itemData(IC.progression_deprioritized_skip_balancing, 0, "Coins", 100),
    201: itemData(IC.useful, 2, "OVE9000 Saw", 100),
    202: itemData(IC.useful, 13, "Skill", 100),
    203: itemData(IC.useful, 13, "Perk", 100),
    204: itemData(IC.useful, 6, "Armor", 100),
    205: itemData(IC.useful, 9, "Deployable", 100),
    206: itemData(IC.filler, 5, "Throwable", 100),
}

fillerItemDict: dict[int, itemData] = {
    300: itemData(IC.useful, 5, "Primary Weapon", 25),
    301: itemData(IC.filler, 5, "Akimbo", 15),
    302: itemData(IC.useful, 5, "Secondary Weapon", 25),
    303: itemData(IC.filler, 5, "Melee Weapon", 5),
    304: itemData(IC.filler, 7, "Stat Boost", 30),
}

fillerLimitDict: dict[int, int] = {
    300: 20,
    301: 44,
    302: 31,
    303: 19,
    304: 0,
}

fillerItems = [fillerItemDict[i] for i in range(300, 305)]
fillerWeights = [fillerItemDict[i].weight for i in range(300, 305)]

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(usefulItemDict)
itemDict.update(fillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class CrimDawnItem(Item):
    game = "PAYDAY 2: Criminal Dawn"

def update_items(world: CrimDawnWorld) -> None:
    if world.options.progression_pacing == "glacial":
        progressionItemDict[1] = itemData(itemDict[1][0], world.itemsForGoal - 1, *itemDict[1][2:])
    else:
        progressionItemDict[1] = itemData(itemDict[1][0], world.itemsForGoal, *itemDict[1][2:])
    world.logger.info(f"{world.player_name} has {world.itemsForGoal} Time Bonuses.")
    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])

    maxCoins = math.ceil(23/3 * world.safehouseTiers)
    usefulItemDict[200] = itemData(itemDict[200][0], maxCoins, *itemDict[200][2:])

def get_random_filler_item_name(world: CrimDawnWorld) -> str:
    item = world.random.choices(fillerItems, weights=fillerWeights, k=1)[0]
    itemId = ITEM_NAME_TO_ID[item.name]

    # Avoid generating too many weapons for non-DLC players
    if fillerLimitDict[itemId] > 0:
        fillerLimitDict[itemId] -= 1
    else: # Generate stat boosts instead
        item = fillerItemDict[304]

    return item.name

def create_all_items(world: CrimDawnWorld) -> None:
    #Create progression items
    itemPool: list[CrimDawnItem] = []

    if world.options.progression_pacing == "glacial":
        world.push_precollected(world.create_item("Time Bonus"))

    for itemId, item in progressionItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in usefulItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in fillerItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    world.multiworld.local_early_items[world.player]["Armor"] = 1

    if world.options.early_bot:
        world.multiworld.local_early_items[world.player]["Extra Bot"] = 1

    #Make sure filler doesn't go over number of locations
    """maxItemCount = 0
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
            print(world.multiworld.get_unfilled_locations(world.player))
            world.logger.warning(f"WARNING: {world.player_name} attempted generation of too many items!")
            break

    for itemId, item in fillerItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))"""

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])

    """fillerItems = [fillerItemDict[i] for i in range(300, 305)]
    fillerWeights = [fillerItemDict[i].weight for i in range(300, 305)]

    items = world.random.choices(fillerItems, weights=fillerWeights, k=fillerCount)
    for item in items:
        itemPool += world.create_item(item.name)"""

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool