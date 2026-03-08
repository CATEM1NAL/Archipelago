from __future__ import annotations
from rule_builder.rules import Has, HasAllCounts
from worlds.generic.Rules import forbid_item

from typing import TYPE_CHECKING
from BaseClasses import ItemClassification, Location, Region
from . import items

if TYPE_CHECKING:
    from .world import PAYDAY2World

def triangle(n: int) -> int:
    return n * (n + 1) // 2

LOCATION_NAME_TO_ID = { f"{triangle(i)} Crime Points" : i for i in range(1, 1001) }

safehouseRooms = ["Scarface's Room", "Dallas' Office", "Hoxton's Files", "Clover's Surveillance Center",
                 "Duke's Gallery", "Houston's Workshop", "Sydney's Studio", "Rust's Corner", "Joy's Van",
                     "h3h3", "Bonnie's Gambling Den", "Jiro's Lounge", "Common Rooms", "Jimmy's Bar",
               "Sangres' Cave", "Chains' Weapons Workshop", "Bodhi's Surfboard Workshop", "Jacket's Hangout",
                 "Sokol's Hockey Gym", "Dragan's Gym", "Vault", "Wolf's Workshop", "Wick's Shooting Range"]

LOCATION_NAME_TO_ID.update({f"{room} - Tier 2": key+1001 for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} - Tier 3": key+1001+len(safehouseRooms) for key, room in enumerate(safehouseRooms)})

class PAYDAY2Location(Location):
    game = "PAYDAY 2: Criminal Dawn"

def create_and_connect_regions(world: PAYDAY2World) -> None:
    world.multiworld.regions.append(Region("Crime.net", world.player, world.multiworld))
    world.multiworld.regions.append(Region("Safe House Tier 2", world.player, world.multiworld))
    world.multiworld.regions.append(Region("Safe House Tier 3", world.player, world.multiworld))

    crimenet = world.get_region("Crime.net")
    safehouseT2 = world.get_region("Safe House Tier 2")
    safehouseT3 = world.get_region("Safe House Tier 3")
    itemsForGoal = (60 - world.options.starting_time) / world.options.time_bonus

    world.create_entrance(crimenet, safehouseT2, HasAllCounts({"24 Coins": 12, "Time Bonus": itemsForGoal // 3}), "276 Coins")
    world.create_entrance(crimenet, safehouseT3, HasAllCounts({"24 Coins": 35, "Time Bonus": 2 * itemsForGoal // 3}), "828 Coins")

def create_all_locations(world: PAYDAY2World) -> None:
    create_score_locations(world)

def create_score_locations(world: PAYDAY2World) -> None:
    # Create regions, assign a location to each region, chain entrances together
    itemsForGoal = (60 - world.options.starting_time) / world.options.time_bonus

    for i in range(2,4):
        safehouse = world.get_region(f"Safe House Tier {i}")
        for room in safehouseRooms:
            locName = f"{room} - Tier {i}"
            locId = world.location_name_to_id[locName]
            location = PAYDAY2Location(world.player, locName, locId, safehouse)
            safehouse.locations.append(location)
            forbid_item(location, "24 Coins", world.player)
            forbid_item(location, "6 Coins", world.player)

    crimenet = world.get_region("Crime.net")

    requiredTimeBonuses = {}
    for i in range(1, world.options.score_checks+1):
        locName = f"{triangle(i)} Crime Points"
        locId = world.location_name_to_id[locName]

        region = Region(locName, world.player, world.multiworld)
        world.multiworld.regions.append(region)

        location = PAYDAY2Location(world.player, locName, locId, region)
        region.locations.append(location)

        diffTraps = 0
        mutatorTraps = 0
        bots = 0

        if world.options.difficulty_traps:
            diffTraps = i // (world.options.score_checks // (world.options.difficulty_traps * world.options.final_difficulty - 1))
        if world.options.mutator_traps > 0:
            mutatorTraps = i // (world.options.score_checks // world.options.mutator_traps)
        if world.options.bots > 0:
            bots = i // (world.options.score_checks // world.options.bots)

        if i == 1:
            crimenet.connect(region, "Start run")

        #elif (world.options.score_checks / itemsForGoal) < i:
        #    timeBonuses = i // (world.options.score_checks // itemsForGoal)
        #    world.set_rule(location, Has("Time Bonus", timeBonuses))
        #    print(f"{location}: {timeBonuses}")

        else:
            if 1.5 * (world.options.score_checks / itemsForGoal) <= i < 4 * (world.options.score_checks / itemsForGoal):
                timeBonuses = max(i // (world.options.score_checks // itemsForGoal) - 1, 1)
                requiredTimeBonuses.update({triangle(i): timeBonuses})

            elif 4 * (world.options.score_checks / itemsForGoal) <= i < world.options.score_checks:
                timeBonuses = i * 2 // (world.options.score_checks // itemsForGoal) - 5
                requiredTimeBonuses.update({triangle(i): timeBonuses})

            elif i == world.options.score_checks:
                timeBonuses = 5
                requiredTimeBonuses.update({triangle(i): 5})

            else:
                timeBonuses = 0
                requiredTimeBonuses.update({triangle(i): 0})

            #print(f"{location}: {timeBonuses}")
            #print(f"{location}: \n{timeBonuses}\n{diffTraps}\n{mutatorTraps}\n{bots}\n{i // (world.options.score_checks // 8)}")
            diffTraps = 0
            mutatorTraps = 0
            bots = 0
            locationRule = HasAllCounts({"Time Bonus": timeBonuses,
                                         "Difficulty Increase": diffTraps,
                                         "Additional Mutator": mutatorTraps,
                                         "Extra Bot": bots,
                                         "Perma-Perk": i // (world.options.score_checks // 8)})

            world.set_rule(location, locationRule)

        if i > 1:
            prevRegion.connect(region, f"{i} points")
        prevRegion = region

    #print(requiredTimeBonuses)
    required = 0
    prevScore = 0
    world.locationToScoreCap = []
    for score, timeBonuses in requiredTimeBonuses.items():
        if timeBonuses > required:
            world.locationToScoreCap.append(prevScore)
            required += 1
        prevScore = score
    #print(world.locationToScoreCap)

    locName = "Final Heist Completed"
    region = Region(locName, world.player, world.multiworld)
    location = PAYDAY2Location(world.player, locName, None, region)
    locationRule = HasAllCounts({"Time Bonus": itemsForGoal,
                                 "Difficulty Increase": world.options.difficulty_traps * (world.options.final_difficulty - 1),
                                 "Additional Mutator": world.options.mutator_traps.value,
                                 "Extra Bot": world.options.bots.value,
                                 "Perma-Perk": 8})
    world.set_rule(location, locationRule)
    region.locations.append(location)
    crimenet.connect(region, f"Final Heist")

    victory = items.PAYDAY2Item("Victory", ItemClassification.progression, None, world.player)
    location.place_locked_item(victory)

    world.set_completion_rule(Has("Victory"))