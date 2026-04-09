from collections.abc import Mapping
from typing import Any, ClassVar
import settings, logging
from BaseClasses import ItemClassification as IC

from worlds.AutoWorld import World, WebWorld

from . import items, locations
from . import options as crimdawn_options
from .data_structs import gameModeData

class CrimDawnWebWorld(WebWorld):
    game = "PAYDAY 2: Criminal Dawn"
    option_groups = crimdawn_options.option_groups

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
            gameModeDict = { # runLength, scoreChecks
                "Short Day": gameModeData(4, 90),
                "Long Day": gameModeData(6, 130),
                "Pointless Day": gameModeData(0, 80),
                "Moving Day": gameModeData(0, 130),
                "Texan Day": gameModeData(4, 100)
            }
            self.goal = self.options.game_mode.get_option_name(self.options.game_mode.value)
            print(self.options.game_mode.value)
            print(self.goal)
            self.runLength = gameModeDict[self.goal].runLength
            self.scoreChecks = gameModeDict[self.goal].scoreChecks

            self.yaml_overrides()

        elif self.game in self.multiworld.re_gen_passthrough:
            slot_data: dict[str, Any] = self.multiworld.re_gen_passthrough[self.game]
            self.options.progression_pacing.value = slot_data["progression_pacing"]
            self.runLength = slot_data["run_length"]
            self.options.score_checks.value = slot_data["score_checks"]
            self.botCount = slot_data["diff_scale_count"] - 42

        self.item_name_groups.update({"Perma-Upgrades": set()})
        self.item_name_groups["Perma-Upgrades"].add("Perma-Perk")
        self.item_name_groups["Perma-Upgrades"].add("Perma-Skill")

        if self.runLength > 0:
            self.itemsForGoal = round((self.runLength * 15) / self.options.progression_pacing.value - 1)
        else:
            self.itemsForGoal = round(100 / self.options.progression_pacing.value - 1)


    def yaml_overrides(self):
        if self.options.progression_pacing == "glacial":
            self.scoreChecks += 25

        if self.options.biglobby == 0:
            self.botCount = 3
        else:
            self.botCount = self.random.randint(7, 21)
            self.scoreChecks += 20

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
            "final_difficulty",
            "death_link"
        )
        args["server_version"] = self.world_version.as_simple_string()
        args["seed_name"] = f"cd_{self.multiworld.seed_name}"
        args["score_caps"] = self.locationToScoreCap
        args["diff_scale_count"] = self.botCount + 42
        args["run_length"] = self.runLength
        args["score_checks"] = self.scoreChecks
        args["goal"] = self.goal

        return args