from collections.abc import Mapping
from typing import Any, ClassVar
import settings

from worlds.AutoWorld import World

from . import items, locations
from . import options as payday2_options

class PAYDAY2Settings(settings.Group):
    class PAYDAY2Path(settings.LocalFilePath):
        description = "payday2_win32_release.exe (.../steamapps/common/PAYDAY 2)"
        is_exe = True

    payday2_path: PAYDAY2Path = PAYDAY2Path("C:/Program Files (x86)/Steam/steamapps/common/PAYDAY 2/payday2_win32_release.exe")

class PAYDAY2World(World):
    """
    PAYDAY 2 is a shooty bang bang game.
    """
    game = "PAYDAY 2: Criminal Dawn"
    topology_present = False

    options_dataclass = payday2_options.PAYDAY2Options
    options: payday2_options.PAYDAY2Options
    settings: ClassVar[PAYDAY2Settings]

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Crime.net"

    def create_regions(self) -> None:
        locations.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def create_items(self) -> None:
        items.update_items(self)
        items.create_all_items(self)

    def create_item(self, name: str) -> items.PAYDAY2Item:
        itemId: int = items.ITEM_NAME_TO_ID[name]
        return items.PAYDAY2Item(name, items.itemDict[itemId].classification, itemId, player=self.player)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        args = self.options.as_dict(
            "starting_time",
            "time_bonus",
            "final_difficulty",
            "death_link"
        )
        args["server_version"] = self.world_version.as_simple_string()
        args["seed_name"] = f"cd_{self.multiworld.seed_name}"

        return args