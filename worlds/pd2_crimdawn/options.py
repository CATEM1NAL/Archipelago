from dataclasses import dataclass

from Options import Choice, TextChoice, PerGameCommonOptions, Range, Toggle, OptionGroup, DefaultOnToggle

class GamePace(Choice):
    """
    The speed at which the world can be played. Slower speeds are more likely to get stuck.

    QUICK: Start with 20 minutes, gain 20 with each time bonus.

    STANDARD: Start with 10 minutes, gain 10 with each time bonus.

    GLACIAL: Start with 10 minutes, gain 5 with each time bonus.
    Adds 20 score checks, leading to more spheres and taking longer to goal.
    """

    display_name = "Progression Pacing"

    option_quick = 20
    option_standard = 10
    option_glacial = 5

    default = option_standard

class InfiniteTime(DefaultOnToggle):
    """
    Generate an additional time bonus at the final score check.
    After obtaining every time bonus the timer is disabled.
    """

    display_name = "Infinite Time"

class GameMode(Choice):
    """
    SHORT DAY: 4 heists per run, jumping straight to the bigger ones.
    100 score checks. Timer caps at 60 minutes. Can take around 8 hours to goal.

    LONG DAY: 6 heists per run, with the first two being smaller scale.
    130 score checks. Timer caps at 90 minutes (100 on Quick). Can take around 12 hours to goal.

    POINTLESS DAY: Random heists. Win after maxing out your score.
    80 score checks. Timer caps at 100 minutes. Can take around ?? hours to goal.

    MOVING DAY: Random heists. Win after fully upgrading the safe house.
    130 score checks. Timer caps at 100 minutes. Can take around ?? hours to goal.
    """

    display_name = "Game Mode"

    option_short_day = 1
    option_long_day = 2
    option_pointless_day = 3
    option_moving_day = 4

    default = option_short_day

class BotCount(Toggle):
    """
    Whether BigLobby is installed. Adds 20 extra score checks when enabled.
    Enabling this increases the number of extra bots from 3 to a number between 7 and 21,
    however the game may become less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "BigLobby"

class AdditionalSaw(Range):
    """
    How many OVE9000 saws are in the item pool.
    The first saw will randomly be a primary or secondary.
    """

    display_name = "OVE9000 Saws"

    range_start = 0
    range_end = 2

    default = 2

class PrimaryCount(Range):
    """
    The base number of primary weapons the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    20 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Primary Weapons"

    range_start = 0
    range_end = 77
    default = 10

class AkimboCount(Range):
    """
    The base number of akimbos the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    44 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Akimbos"

    range_start = 0
    range_end = 58
    default = 5

class SecondaryCount(Range):
    """
    The base number of secondary weapons the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    31 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Secondary Weapons"

    range_start = 0
    range_end = 78
    default = 10

class MeleeCount(Range):
    """
    The base number of melee weapons the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    19 is the most you can have without DLC or achievements - extra items will do nothing.
    """

    display_name = "Melee Weapons"

    range_start = 0
    range_end = 94
    default = 5

class ThrowableCount(Range):
    """
    The base number of throwables the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    5 is the most you can have without DLC or achievements - extra items will do nothing.
    """

    display_name = "Throwables"

    range_start = 0
    range_end = 15
    default = 5

class MaxDiff(Choice):
    """
    The highest difficulty your run can reach.

    This mod can be quite hard early-mid game as you aren't guaranteed to have a good build,
    but late game you can get INCREDIBLY powerful builds that make high difficulties trivial.

    If you're unsure of what to set this to, I'd recommend starting with
    the difficulty below the highest you can comfortably play normally.
    """

    display_name = "Final Difficulty"

    option_normal = 1
    option_hard = 2
    option_very_hard = 3
    option_overkill = 4
    option_mayhem = 5
    option_death_wish = 6
    option_death_sentence = 7

    default = 4

class DeathLink(Toggle):
    """
    Death links are sent when a heist is failed.
    After receiving a death link you will lose a down the next time you take damage.
    In a multiplayer session only the lobby host can send death links to prevent spam.
    """

    display_name = "Death Link"

@dataclass
class CrimDawnOptions(PerGameCommonOptions):
    progression_pacing: GamePace
    game_mode: GameMode
    infinite_time: InfiniteTime
    final_difficulty: MaxDiff
    death_link: DeathLink
    saws: AdditionalSaw
    primary_weapons: PrimaryCount
    akimbo: AkimboCount
    secondary_weapons: SecondaryCount
    melee_weapons: MeleeCount
    throwables: ThrowableCount
    biglobby: BotCount

option_groups = [
    OptionGroup(
        "Item Generation",
        [AdditionalSaw,
         PrimaryCount,
         AkimboCount,
         SecondaryCount,
         MeleeCount,
         ThrowableCount,
         BotCount],
    ),
]