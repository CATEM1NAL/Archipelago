import math
from collections.abc import Mapping
from typing import Any, ClassVar
import settings, logging
from BaseClasses import ItemClassification as IC

from worlds.AutoWorld import World, WebWorld

from . import items, locations
from . import options as crimdawn_options

class CrimDawnWebWorld(WebWorld):
    game = "PAYDAY 2: Criminal Dawn"

    options_presets = crimdawn_options.presets

class CrimDawnSettings(settings.Group):
    class PAYDAY2Path(settings.LocalFilePath):
        description = "payday2_win32_release.exe (.../steamapps/common/PAYDAY 2)"
        is_exe = True

    payday2_path: PAYDAY2Path = PAYDAY2Path("C:/Program Files (x86)/Steam/steamapps/common/PAYDAY 2/payday2_win32_release.exe")

class CrimDawnWorld(World):
    """
    PAYDAY 2: Criminal Dawn is a roguelite conversion for PAYDAY 2 that was built to support Archipelago.
    """
    game = "PAYDAY 2: Criminal Dawn"
    topology_present = False

    options_dataclass = crimdawn_options.CrimDawnOptions
    options: crimdawn_options.CrimDawnOptions
    settings: ClassVar[CrimDawnSettings]

    web = CrimDawnWebWorld()

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID
    locationToScoreCap = []
    logger = logging.getLogger("Criminal Dawn")

    origin_region_name = "Crime.net"
    glitches_item_name: str = "Glitch Logic"

    ut_can_gen_without_yaml = True

    def generate_early(self) -> None:
        if not hasattr(self.multiworld, "re_gen_passthrough"):
            self.campaignLengthDict = {
                "Return Of The Rat": 4,
                "Murky Day": 4,
                "I Need My Payday Too": 5,
                "Greatest Heist Of All": 6,
                "Silk Road" : 4,
                "City Of Gold": 3,
                "Texas Heat": 3,
                "Night Of Frights": 4,
                "Christmas Special": 4,
                "Classics": 6,
            }
            self.goal = self.options.goal.get_option_name(self.options.goal.value)
            self.isCampaign = self.goal == "Campaign"
            self.runLength = self.options.run_length.value
            if self.goal == "Score":
                self.runLength = 0
            self.scoreChecks = self.options.score_checks.value
            self.safehouseTiers = self.options.safehouse_tiers.value

            """self.goal = self.options.game_mode.get_option_name(self.options.game_mode.value)
            if self.goal == "Campaign":
                self.goal = self.options.campaign.get_option_name(self.options.campaign.value)
            print(self.goal)
            self.runLength = gameModeDict[self.goal].runLength
            self.scoreChecks = gameModeDict[self.goal].scoreChecks
            self.safehouseTiers = gameModeDict[self.goal].safehouseTiers
            self.isCampaign = gameModeDict[self.goal].campaign"""

            self.yaml_overrides()

        # YAML-less tracker generation
        elif self.game in self.multiworld.re_gen_passthrough:
            slot_data: dict[str, Any] = self.multiworld.re_gen_passthrough[self.game]
            self.options.progression_pacing.value = slot_data["progression_pacing"]
            self.runLength = slot_data["run_length"]
            self.scoreChecks = slot_data["score_checks"]
            self.botCount = slot_data["diff_scale_count"] - 42
            self.goal = slot_data["goal"]
            self.safehouseTiers = slot_data["safehouse_tiers"]
            self.isCampaign = slot_data["campaign"]
            self.items_for_goal()

        self.item_name_groups.update({"Perma-Upgrades": set()})
        self.item_name_groups["Perma-Upgrades"].add("Perma-Perk")
        self.item_name_groups["Perma-Upgrades"].add("Perma-Skill")

    def items_for_goal(self):
        if self.runLength > 0:
            self.itemsForGoal = math.floor((self.runLength * 15) / self.options.progression_pacing.value - 0.5)
        else:
            self.itemsForGoal = math.floor(100 / self.options.progression_pacing.value - 0.5)
            self.options.run_length.visibility = 0

    def yaml_overrides(self):
        if self.goal == "Campaign":
            self.goal = self.options.campaign.get_option_name(self.options.campaign.value)
            self.runLength = self.campaignLengthDict[self.goal]
            self.options.run_length.value = self.runLength

        if not self.isCampaign:
            self.options.campaign.visibility = 0

        if (self.runLength > 0) and (self.safehouseTiers > self.runLength):
            self.logger.info(f"{self.player_name} has too many safehouse tiers! "
                             f"Reducing from {self.safehouseTiers} to {self.runLength}.")
            self.safehouseTiers = self.runLength
            self.options.safehouse_tiers.value = self.safehouseTiers

        if self.options.progression_pacing == "glacial":
            self.scoreChecks += 10

        if self.options.biglobby == 0:
            self.botCount = 3
        else:
            self.botCount = 19
            self.scoreChecks += 20

        self.items_for_goal()

        self.scoreChecks += self.safehouseTiers * math.ceil(23/3)

        totalChecks = self.runLength + self.scoreChecks + (self.safehouseTiers * 23)
        totalItems = 98 + self.itemsForGoal + (self.safehouseTiers * math.ceil(23/3))

        if totalChecks < totalItems:
            self.logger.info(f"{self.player_name} doesn't have enough checks ({totalChecks}/{totalItems})! Adjusting...")
            self.scoreChecks += totalItems - totalChecks
            self.options.score_checks.value = self.scoreChecks
        self.logger.info(f"{self.player_name} has {self.scoreChecks} score checks.")

    def create_regions(self) -> None:
        locations.createAllLocations(self)

    def create_items(self) -> None:
        items.update_items(self)
        items.create_all_items(self)

    def create_item(self, name: str) -> items.CrimDawnItem:
        if name == "Glitch Logic":
            return items.CrimDawnItem("Glitch Logic", IC.progression, None, self.player)

        itemId: int = items.ITEM_NAME_TO_ID[name]
        return items.CrimDawnItem(name, items.itemDict[itemId].classification, itemId, self.player)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        args = self.options.as_dict(
            "progression_pacing",
            "death_link"
        )
        args["server_version"] = self.world_version.as_simple_string()
        args["seed_name"] = f"cd_{self.multiworld.seed_name}"
        args["score_caps"] = self.locationToScoreCap
        args["diff_scale_count"] = self.botCount + 42
        args["run_length"] = self.runLength
        args["score_checks"] = self.scoreChecks
        args["goal"] = self.goal
        args["campaign"] = self.isCampaign
        args["safehouse_tiers"] = self.safehouseTiers

        return args