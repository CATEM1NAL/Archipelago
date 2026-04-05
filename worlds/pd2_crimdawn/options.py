from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle, OptionGroup, DefaultOnToggle


class GamePace(Choice):
    """
    The speed at which the world can be played. Slower speeds are more likely to get stuck.

    QUICK: Start with 20 minutes, gain 20 with each time bonus.
    With 100 score checks and 4 heists this can take around ?? hours to goal.

    STANDARD: Start with 10 minutes, gain 10 with each time bonus.
    With default settings this can take around 12 hours to goal.

    GLACIAL: Start with 10 minutes, gain 5 with each time bonus. Typically leads to more spheres.
    Increasing the number of score checks to at least 150 is recommended!
    With 150 score checks and 6 heists this can take around ?? hours to goal.
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

class RunLength(Choice):
    """
    How many heists you need to complete in a row to reach your goal.

    SHORT: 4 heists per run, jumping straight to the bigger ones.
    Makes spheres larger and decreases how long it takes to goal.

    FULL: 6 heists per run, with the first two being smaller scale.
    """

    display_name = "Run Length"

    option_short = 4
    option_full = 6

    default = option_full

class ScoreLocations(Range):
    """
    How many checks are locked behind score requirements.
    This scales heavily, so be careful about how you set this!
    (5050 points for 100 checks, 7260 points for 120 checks,
    11325 points for 150 checks, 80200 points for 400 checks)
    """

    display_name = "Score Checks"

    range_start = 100
    range_end = 400
    default = 120

class BotCount(Toggle):
    """
    Whether BigLobby is installed. Recommended to increase score checks by about 20.
    Enabling this increases the number of extra bots from 3 to a number between 4 and 21,
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
    19 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Primary Weapons"

    range_start = 0
    range_end = 73
    default = 10

class AkimboCount(Range):
    """
    The base number of akimbos the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    44 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Akimbos"

    range_start = 0
    range_end = 57
    default = 5

class SecondaryCount(Range):
    """
    The base number of secondary weapons the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    24 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Secondary Weapons"

    range_start = 0
    range_end = 67
    default = 10

class MeleeCount(Range):
    """
    The base number of melee weapons the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    19 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Melee Weapons"

    range_start = 0
    range_end = 87
    default = 5

class ThrowableCount(Range):
    """
    The base number of throwables the multiworld will try to generate.
    Actual number may be higher or lower depending on the number of locations available.
    6 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Throwables"

    range_start = 0
    range_end = 10
    default = 5

class MaxDiff(Choice):
    """
    The highest difficulty your run can reach.

    This mod can get quite hard as you aren't guaranteed to have a good build,
    and the total number of upgrades is less than you would normally have.

    If you're unsure of what to set this to, I'd recommend trying the difficulty
    below the highest you can comfortably play normally.
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
    Death links are sent every time a heist is failed.
    After receiving a death link you will lose a down the next time you take damage.
    In a multiplayer session only the lobby host can send death links to avoid spam.
    """

    display_name = "Death Link"

@dataclass
class CrimDawnOptions(PerGameCommonOptions):
    progression_pacing: GamePace
    run_length: RunLength
    infinite_time: InfiniteTime
    score_checks: ScoreLocations
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