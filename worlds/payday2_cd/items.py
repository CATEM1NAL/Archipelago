from __future__ import annotations

from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData, itemType

if TYPE_CHECKING:
    from .world import PAYDAY2World

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 5, "Time Bonus", itemType.progression),
    2: itemData(IC.progression, 2, "Drill Sawgeant", itemType.progression),
    3: itemData(IC.progression, 3, "Extra Bot", itemType.progression),
    4: itemData(IC.progression, 2, "OVE9000 Saw", itemType.progression),
    5: itemData(IC.progression, 1, "ECM", itemType.progression),
    6: itemData(IC.progression, 1, "Trip Mines", itemType.progression),
    7: itemData(IC.progression_deprioritized_skip_balancing, 35, "24 Coins", itemType.progression),
    8: itemData(IC.progression, 2, "Nine Lives", itemType.progression),
}

trapItemDict: dict[int, itemData] = {
    100: itemData(IC.trap, 5, "Difficulty Increase", itemType.trap),
    101: itemData(IC.trap, 5, "Additional Mutator", itemType.trap),
}

usefulItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 18, "Primary Weapon", itemType.weapon),
    201: itemData(IC.useful, 41, "Akimbo", itemType.weapon),
    202: itemData(IC.useful, 23, "Secondary Weapon", itemType.weapon),
    203: itemData(IC.filler, 18, "Melee Weapon", itemType.weapon),
    204: itemData(IC.filler, 5, "Throwable", itemType.weapon),
    205: itemData(IC.useful, 6, "Armor", itemType.unlock),
    206: itemData(IC.useful, 7, "Deployable", itemType.unlock),
    207: itemData(IC.useful, 10, "Skill", itemType.filler),
    208: itemData(IC.useful, 9, "Perk", itemType.filler),
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
    207: 115,
    208: 179,
    209: 150
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(trapItemDict)
itemDict.update(usefulItemDict)
itemDict.update(fillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class PAYDAY2Item(Item):
    game = "PAYDAY 2: Criminal Dawn"

def update_items(world: PAYDAY2World) -> None:
    itemsForGoal = (60 - world.options.starting_time) / world.options.time_bonus
    timeItemCap = (100 - world.options.starting_time) // world.options.time_bonus
    numExtraTime = world.options.time_upgrades

    if numExtraTime < itemsForGoal:
        numExtraTime = math.ceil(itemsForGoal)
        print(f"Increased {world.player_name}'s Extra Time items from {world.options.time_upgrades} to {numExtraTime} for world to be playable.")
    elif numExtraTime > timeItemCap:
        numExtraTime = timeItemCap
        print(f"Reduced {world.player_name}'s Extra Time items from {world.options.time_upgrades} to {numExtraTime} to not exceed 100 minutes.")

    progressionItemDict[1] = itemData(IC.progression, numExtraTime, "Time Bonus", itemType.progression)
    progressionItemDict[3] = itemData(IC.progression, world.options.bots, "Extra Bot", itemType.progression)
    progressionItemDict[4] = itemData(IC.progression, world.options.saws, "OVE9000 Saw", itemType.progression)

    trapItemDict[100] = itemData(IC.trap, world.options.difficulty_traps * (world.options.final_difficulty - world.options.starting_difficulty), "Difficulty Increase", itemType.trap)
    trapItemDict[101] = itemData(IC.trap, world.options.mutator_traps, "Additional Mutator", itemType.trap)

    usefulItemDict[200] = itemData(IC.useful, world.options.primary_weapons, "Primary Weapon", itemType.weapon)
    fillerLimitDict[200] -= world.options.primary_weapons

    usefulItemDict[201] = itemData(IC.useful, world.options.akimbo, "Akimbo", itemType.weapon)
    fillerLimitDict[201] -= world.options.akimbo

    usefulItemDict[202] = itemData(IC.useful, world.options.secondary_weapons, "Secondary Weapon", itemType.weapon)
    fillerLimitDict[202] -= world.options.secondary_weapons

    usefulItemDict[203] = itemData(IC.filler, world.options.melee_weapons, "Melee Weapon", itemType.weapon)
    fillerLimitDict[203] -= world.options.melee_weapons

    usefulItemDict[204] = itemData(IC.filler, world.options.throwables, "Throwable", itemType.weapon)
    fillerLimitDict[204] -= world.options.throwables

    usefulItemDict[205] = itemData(IC.useful, world.options.armor_unlocks, "Armor", itemType.unlock)
    fillerLimitDict[205] -= world.options.armor_unlocks

    usefulItemDict[206] = itemData(IC.useful, world.options.deployables, "Deployable", itemType.unlock)
    fillerLimitDict[206] -= world.options.deployables

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

    for itemId, item in trapItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in usefulItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool

    if world.options.starting_difficulty > 1:
        for i in range(world.options.starting_difficulty):
            world.push_precollected(world.create_item("Difficulty Increase"))