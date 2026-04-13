from __future__ import annotations
from rule_builder.rules import Has, HasGroup, HasAllCounts, CanReachLocation
from worlds.generic.Rules import forbid_item, forbid_items_for_player

from typing import TYPE_CHECKING
from BaseClasses import ItemClassification as IC, Location, Region, LocationProgressType
from . import items
import math

if TYPE_CHECKING:
    from .world import CrimDawnWorld

def triangle(n: int) -> int:
    return n * (n + 1) // 2

maxScoreLocations = (178) + 1
LOCATION_NAME_TO_ID = { f"{triangle(i)} Points" : i for i in range(1, maxScoreLocations) }

safehouseRooms = ["Scarface's Room", "Dallas' Office", "Hoxton's Files", "Clover's Surveillance Center",
                 "Duke's Gallery", "Houston's Workshop", "Sydney's Studio", "Rust's Corner", "Joy's Van",
                     "h3h3", "Bonnie's Gambling Den", "Jiro's Lounge", "Common Rooms", "Jimmy's Bar",
               "Sangres' Cave", "Chains' Weapons Workshop", "Bodhi's Surfboard Workshop", "Jacket's Hangout",
                 "Sokol's Hockey Gym", "Dragan's Gym", "Vault", "Wolf's Workshop", "Wick's Shooting Range"]

LOCATION_NAME_TO_ID.update({f"{room} (Tier 1)": key + maxScoreLocations for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} (Tier 2)": key + maxScoreLocations + len(safehouseRooms) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} (Tier 3)": key + maxScoreLocations + (len(safehouseRooms) * 2) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} (Tier 4)": key + maxScoreLocations + (len(safehouseRooms) * 3) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} (Tier 5)": key + maxScoreLocations + (len(safehouseRooms) * 4) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} (Tier 6)": key + maxScoreLocations + (len(safehouseRooms) * 5) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"Heist {i} Completed": i + maxScoreLocations + (len(safehouseRooms) * 6) for i in range(1, 7)})
LOCATION_NAME_TO_ID.update({"Safehouse Completed": maxScoreLocations + (len(safehouseRooms) * 6) + 7})

class CrimDawnLocation(Location):
    game = "PAYDAY 2: Criminal Dawn"

def createAllLocations(world: CrimDawnWorld) -> None:
    world.multiworld.regions.append(Region("Crime.net", world.player, world.multiworld))
    if world.runLength > 0:
        createHeistCompletionLocations(world)
    createScoreLocations(world)
    createSafeHouseLocations(world)
    world.set_completion_rule(Has("Victory"))

def createHeistCompletionLocations(world: CrimDawnWorld) -> None:
    crimenet = world.get_region("Crime.net")

    # Heist completion checks
    for i in range(1, world.runLength + 1):
        world.multiworld.regions.append(Region(f"Heist {i}", world.player, world.multiworld))
        heistRegion = world.get_region(f"Heist {i}")
        locName = f"Heist {i} Completed"
        locId = world.location_name_to_id[locName]
        if i == world.runLength:
            locId = None
        location = CrimDawnLocation(world.player, locName, locId, heistRegion)
        location.progress_type = LocationProgressType.PRIORITY
        heistRegion.locations.append(location)

        if i == 1:
            if world.runLength < 6 or world.isCampaign:
                itemsForConnection = math.floor(15 / world.options.progression_pacing.value - 0.5)
            else:
                itemsForConnection = math.floor(10 / world.options.progression_pacing.value - 0.5)
            world.create_entrance(crimenet, heistRegion, Has("Time Bonus", itemsForConnection),"Start Run")
            #world.create_entrance(crimenet, heistRegion, None, "Start Run")
        else: #Create Entrance connecting the heist region to the previous heist region
            #itemsForConnection = math.floor(world.itemsForGoal / world.options.run_length.value * i)
            itemsForConnection = math.ceil(((i * 15) / world.options.progression_pacing) - 1)
            entranceRule = Has("Time Bonus", itemsForConnection)

            itemsForGlitchLogic = math.ceil(((i * 10) / world.options.progression_pacing) - 1)
            entranceRule = entranceRule | (Has("Time Bonus", itemsForGlitchLogic) & Has("Glitch Logic"))

            world.create_entrance(world.get_region(f"Heist {i - 1}"), heistRegion, entranceRule, f"Heist {i} Requirements")

        print(f"Heist {i}: {itemsForConnection} time bonuses ({world.options.progression_pacing.value * (itemsForConnection + 1)} minutes)")

def createSafeHouseLocations(world: CrimDawnWorld) -> None:
    # Safehouse checks
    for i in range(1, world.safehouseTiers + 1):
        currentTier = Region(f"Safe House Tier {i}", world.player, world.multiworld)
        world.multiworld.regions.append(currentTier)

        safehouseAccess = Has("Coins", math.ceil(23/3 * i)) | (Has("Coins", math.ceil(23/3 * (i - 1) + 1)) & Has("Glitch Logic"))

        if i == world.safehouseTiers:
            safehouseAccess = Has("Coins", math.ceil(23 / 3 * (i - 1) + 1)) | (Has("Coins", math.ceil(23 / 3 * (i - 1) + 1)) & Has("Glitch Logic"))

        #if i == 1:
        #    safehouseAccess = safehouseAccess & CanReachLocation(f"{triangle(12)} Points")
        if world.runLength > 0:
            world.create_entrance(world.get_region(f"Heist {i}"), currentTier, safehouseAccess, f"{23 * i} Coins")
        else:
            if i == 1:
                world.create_entrance(world.get_region(f"Crime.net"), currentTier, safehouseAccess, f"{23 * i} Coins")
            else:
                world.create_entrance(world.get_region(f"Safe House Tier {i-1}"), currentTier, safehouseAccess, f"{23 * i} Coins")

    for i in range(1, world.safehouseTiers + 1):
        safehouse = world.get_region(f"Safe House Tier {i}")
        for room in safehouseRooms:
            locName = f"{room} (Tier {i})"
            locId = world.location_name_to_id[locName]
            location = CrimDawnLocation(world.player, locName, locId, safehouse)
            safehouse.locations.append(location)
            forbid_item(location, "Coins", world.player)
            if i == 1:
                forbid_item(location, "Time Bonus", world.player)

def createScoreLocations(world: CrimDawnWorld) -> None:
    # Create regions, assign a location to each region, chain entrances together
    firstHeist = world.get_region("Crime.net")

    requiredTimeBonuses = {}

    for i in range(1, world.scoreChecks + 1):
        locName = f"{triangle(i)} Points"
        locId = world.location_name_to_id[locName]

        region = Region(locName, world.player, world.multiworld)
        world.multiworld.regions.append(region)

        location = CrimDawnLocation(world.player, locName, locId, region)

        bots = (i // (world.scoreChecks // world.botCount))

        if i == 1:
            firstHeist.connect(region, "1 point")

        else:
            #if i < 4 * (world.scoreChecks / max(world.itemsForGoal - 1, 1)):
            if i < world.scoreChecks:
                timeBonuses = round(i / (world.scoreChecks / max(world.itemsForGoal - 1, 1)))

            #elif 4 * (world.scoreChecks / max(world.itemsForGoal - 1, 1)) <= i < world.scoreChecks:
            #    timeBonuses =  round(i / (world.scoreChecks / max(world.itemsForGoal - 1, 1)))

            elif i == world.scoreChecks:
                timeBonuses = round(world.itemsForGoal)
                if world.goal == "Score":
                    victory = items.CrimDawnItem("Victory", IC.progression, None, world.player)
                    location = CrimDawnLocation(world.player, locName, None, region)
                    location.place_locked_item(victory)

                elif world.options.infinite_time:
                    location.place_locked_item(world.create_item("Time Bonus"))


            else:
                timeBonuses = 0

            requiredTimeBonuses.update({triangle(i): timeBonuses})
            locationRule = (HasAllCounts({"Time Bonus": timeBonuses,
                                          "Extra Bot": bots}) &
                            HasGroup("Perma-Upgrades", (i * 14) // world.scoreChecks))
            locationRule = locationRule | (Has("Time Bonus", timeBonuses) & Has("Glitch Logic"))
            #print(f"{locName}: {locationRule}")

            world.set_rule(location, locationRule)

        region.locations.append(location)
        if i > 1:
            prevRegion.connect(region, f"{i} points")
        prevRegion = region

    required = 0
    prevScore = 0
    world.locationToScoreCap = []
    for score, timeBonuses in requiredTimeBonuses.items():
        if timeBonuses > required:
            world.locationToScoreCap.append(prevScore)
            required += 1
        prevScore = score
    world.locationToScoreCap.append(triangle(world.scoreChecks))

    if world.runLength > 0:
        location = world.get_location(f"Heist {world.runLength} Completed")
        locationRule = HasAllCounts({"Time Bonus": world.itemsForGoal,
                                     "Extra Bot": world.botCount,
                                     "Perma-Perk": 7,
                                     "Perma-Skill": 7})

        world.set_rule(location, locationRule)

        victory = items.CrimDawnItem("Victory", IC.progression, None, world.player)
        location.place_locked_item(victory)