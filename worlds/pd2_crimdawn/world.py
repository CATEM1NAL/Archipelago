from collections.abc import Mapping
from typing import Any, ClassVar
import settings, logging

from worlds.AutoWorld import World, WebWorld

from . import items, locations
from . import options as crimdawn_options

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

    def generate_early(self) -> None:
        self.itemsForGoal = round((self.options.run_length.value * 15) / self.options.progression_pacing.value - 1)

        if self.options.biglobby == 0:
            self.botCount = 3
        else:
            self.botCount = self.random.randint(7,21)

    def create_regions(self) -> None:
        locations.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def create_items(self) -> None:
        items.update_items(self)
        items.create_all_items(self)

    def create_item(self, name: str) -> items.CrimDawnItem:
        itemId: int = items.ITEM_NAME_TO_ID[name]
        return items.CrimDawnItem(name, items.itemDict[itemId].classification, itemId, player=self.player)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        args = self.options.as_dict(
            "progression_pacing",
            "run_length",
            "final_difficulty",
            "death_link"
        )
        args["server_version"] = self.world_version.as_simple_string()
        args["seed_name"] = f"cd_{self.multiworld.seed_name}"
        args["score_caps"] = self.locationToScoreCap
        args["diff_scale_count"] = self.botCount + 42
        args["player_name"] = self.player_name

        return args