from __future__ import annotations
from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .data_structs import itemData

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
    200: itemData(IC.progression_deprioritized_skip_balancing, 0, "Coins"),
    201: itemData(IC.useful, 2, "OVE9000 Saw"),
    202: itemData(IC.useful, 13, "Skill"),
    203: itemData(IC.useful, 13, "Perk"),
}

fillerItemDict: dict[int, itemData] = {
    300: itemData(IC.useful, 5, "Primary Weapon"),
    301: itemData(IC.filler, 5, "Akimbo"),
    302: itemData(IC.useful, 5, "Secondary Weapon"),
    303: itemData(IC.filler, 5, "Melee Weapon"),
    304: itemData(IC.filler, 5, "Throwable"),
    305: itemData(IC.useful, 6, "Armor"),
    306: itemData(IC.useful, 9, "Deployable"),
    307: itemData(IC.filler, 13, "Stat Boost")
}

fillerLimitDict: dict[int, int] = {
    300: 20,
    301: 44,
    302: 31,
    303: 19,
    304: 5,
    305: 6,
    306: 9,
    307: 0,
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(trapItemDict)
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
    progressionItemDict[4] = itemData(itemDict[4][0], world.options.saws, *itemDict[4][2:])

    maxCoins = math.ceil(2 * (23/3))
    if world.runLength > 0:
        maxCoins = math.ceil(23/3 * world.runLength)
    elif world.goal == "Moving Day":
        maxCoins = math.ceil(23/3 * 6)

    usefulItemDict[200] = itemData(itemDict[200][0], maxCoins, *itemDict[200][2:])

    #optList = [world.options.primary_weapons, #300
    #           world.options.akimbo, #301
    #           world.options.secondary_weapons, #302
    #           world.options.melee_weapons, #303
    #           world.options.throwables] #304

    #for i, opt in enumerate(optList):
    #    fillerItemDict[300+i] = itemData(itemDict[300+i][0], opt.value, *itemDict[300+i][2:])
    #    fillerLimitDict[300+i] -= opt

def get_random_filler_item_name(world: CrimDawnWorld) -> str:
    fillerType = world.random.random()

    if fillerType < 0.75: # 75% chance for weapon
        item = fillerItemDict[world.random.randint(300, 303)]
    else: # 25% chance for stat boost
        item = fillerItemDict[307]

    itemId = ITEM_NAME_TO_ID[item.name]

    if fillerLimitDict[itemId] > 0: # Avoid generating too many weapons for non-DLC players
        fillerLimitDict[itemId] -= 1
    else: # Generate stat boosts instead
        item = fillerItemDict[307]

    return item.name

def create_all_items(world: CrimDawnWorld) -> None:
    #Create progression items
    itemPool: list[CrimDawnItem] = []

    if world.options.progression_pacing == "glacial":
        world.push_precollected(world.create_item("Time Bonus"))

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

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool