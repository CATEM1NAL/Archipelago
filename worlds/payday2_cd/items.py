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
    7: itemData(IC.progression_deprioritized_skip_balancing, 40, "24 Coins", itemType.progression),
    8: itemData(IC.progression, 2, "Nine Lives", itemType.progression),
    9: itemData(IC.progression, 8, "Perma-Perk", itemType.progression),
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
    207: itemData(IC.useful, 5, "Skill", itemType.filler),
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
    207: 115,
    208: 179,
    209: 150
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
    itemsForGoal = (60 - world.options.starting_time) / world.options.time_bonus
    timeItemCap = (100 - world.options.starting_time) // world.options.time_bonus
    numExtraTime = world.options.time_upgrades

    if numExtraTime < itemsForGoal:
        numExtraTime = math.ceil(itemsForGoal)
        print(f"Increased {world.player_name}'s Extra Time items from {world.options.time_upgrades} to {numExtraTime} for world to be playable.")
    elif numExtraTime > timeItemCap:
        numExtraTime = timeItemCap
        print(f"Reduced {world.player_name}'s Extra Time items from {world.options.time_upgrades} to {numExtraTime} to not exceed 100 minutes.")

    progressionItemDict[1] = itemData(itemDict[1][0], numExtraTime, *itemDict[1][2:])
    progressionItemDict[3] = itemData(itemDict[3][0], world.options.bots, *itemDict[3][2:])
    progressionItemDict[4] = itemData(itemDict[4][0], world.options.saws, *itemDict[4][2:])

    progressionItemDict[100] = itemData(IC.trap, world.options.difficulty_traps * (world.options.final_difficulty - 1), *itemDict[100][2:])
    progressionItemDict[101] = itemData(IC.trap, world.options.mutator_traps, *itemDict[101][2:])
    itemDict[100] = itemData(IC.progression | IC.trap, *itemDict[100][1:])
    itemDict[101] = itemData(IC.progression | IC.trap, *itemDict[101][1:])

    optList = [world.options.primary_weapons, #200
               world.options.akimbo, #201
               world.options.secondary_weapons, #202
               world.options.melee_weapons, #203
               world.options.throwables, #204
               world.options.armor_unlocks, #205
               world.options.deployables] #206

    for i, opt in enumerate(optList):
        usefulItemDict[200+i] = itemData(itemDict[200+i][0], opt.value, *itemDict[200+i][2:])
        fillerLimitDict[200+i] -= opt

"""    usefulItemDict[200] = itemData(itemDict[200][0], world.options.primary_weapons, *itemDict[200][2:])
    fillerLimitDict[200] -= world.options.primary_weapons

    usefulItemDict[201] = itemData(itemDict[201][0], world.options.akimbo, *itemDict[201][2:])
    fillerLimitDict[201] -= world.options.akimbo

    usefulItemDict[202] = itemData(itemDict[202][0], world.options.secondary_weapons, *itemDict[202][2:])
    fillerLimitDict[202] -= world.options.secondary_weapons

    usefulItemDict[203] = itemData(itemDict[203][0], world.options.melee_weapons, *itemDict[203][2:])
    fillerLimitDict[203] -= world.options.melee_weapons

    usefulItemDict[204] = itemData(itemDict[204][0], world.options.throwables, *itemDict[204][2:])
    fillerLimitDict[204] -= world.options.throwables

    usefulItemDict[205] = itemData(itemDict[205][0], world.options.armor_unlocks, *itemDict[205][2:])
    fillerLimitDict[205] -= world.options.armor_unlocks

    usefulItemDict[206] = itemData(itemDict[206][0], world.options.deployables, *itemDict[206][2:])
    fillerLimitDict[206] -= world.options.deployables"""

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