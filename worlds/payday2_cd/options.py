from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle, DefaultOnToggle


class ScoreLocations(Range):
    """
    How many checks are gained from score.
    """

    display_name = "Score Checks"

    range_start = 50
    range_end = 1000
    default = 100

class StartingTime(Range):
    """
    How many minutes you start with before time bonuses.
    """

    display_name = "Starting Time (minutes)"

    range_start = 1
    range_end = 100
    default = 10

class TimeUpgrades(Range):
    """
    Number of time bonuses the multiworld will try to generate.
    If the max time would be below 60 minutes or above 100 minutes this will be adjusted to fit.
    The world will assume you can win when you have at least 60 minutes available (~10 per heist).
    """

    display_name = "Time Bonuses"

    range_start = 0
    range_end = 99
    default = 5

class TimeUpgradeStrength(Range):
    """
    How many minutes you gain from each time bonus.
    """

    display_name = "Minutes Per Time Bonus"

    range_start = 1
    range_end = 99
    default = 10

class BotCount(Range):
    """
    How many bots will be in the item pool.
    More than 3 requires BigLobby and may make the game less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "Max Bots"

    range_start = 0
    range_end = 21
    default = 3

class AdditionalSaw(Range):
    """
    How many OVE9000 saws are in the item pool.
    """

    display_name = "Saws"

    range_start = 0
    range_end = 2

    default = 2

class NineLives(Range):
    """
    How many Nine Lives upgrades are available.
    Nine Lives Lv1: +1 extra down.
    Nine Lives Lv2: +3 extra downs.
    """

    display_name = "Nine Lives"

    range_start = 0
    range_end = 2

    default = 2

class PrimaryCount(Range):
    """
    How many primary weapons are guaranteed to generate in the multiworld.
    Additional primaries may be created randomly.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Primary Weapons"

    range_start = 0
    range_end = 72
    default = 10

class AkimboCount(Range):
    """
    How many akimbos are guaranteed to generate in the multiworld.
    Additional akimbos may be created randomly.
    44 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Akimbos"

    range_start = 0
    range_end = 57
    default = 10

class SecondaryCount(Range):
    """
    How many secondary weapons are guaranteed to generate in the multiworld.
    Additional secondaries may be created randomly.
    23 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Secondary Weapons"

    range_start = 0
    range_end = 66
    default = 10

class MeleeCount(Range):
    """
    How many melee weapons are guaranteed to generate in the multiworld.
    Additional melees may be created randomly.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Melee Weapons"

    range_start = 0
    range_end = 86
    default = 5

class ThrowableCount(Range):
    """
    How many throwables are guaranteed to generate in the multiworld.
    Additional throwables may be created randomly.
    5 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Throwables"

    range_start = 0
    range_end = 9
    default = 5

class ArmorCount(Range):
    """
    How many armor unlocks are guaranteed to generate in the multiworld.
    Additional armor unlocks may be created randomly.
    """

    display_name = "Armors"

    range_start = 0
    range_end = 6
    default = 6

class DeployablesCount(Range):
    """
    How many non-progression deployables are guaranteed to generate in the multiworld.
    Additional deployables may be created randomly.
    This item also gives a deployable upgrade when collected that gets rerolled at the start of every run.
    ECMs and trip mines will always generate somewhere in the multiworld.
    """

    display_name = "Deployables"

    range_start = 0
    range_end = 7
    default = 7

class MaxDiff(Choice):
    """
    The highest difficulty your run can reach.
    Higher difficulties give a bigger score multiplier,
    so lowering this can slow late game progression.
    """

    display_name = "Final Difficulty"

    option_overkill = 4
    option_mayhem = 5
    option_death_wish = 6
    option_death_sentence = 7

    default = 6

class DiffTraps(DefaultOnToggle):
    """
    Difficulty traps permanently increase the difficulty by 1 per trap collected,
    but also grant a score multiplier.
    Difficulty traps will not bypass your final difficulty.
    """

    display_name = "Difficulty Traps"

class MutatorTraps(Range):
    """
    Mutator traps cause all future heists to roll an additional mutator,
    but also grant a score multiplier.
    """

    display_name = "Mutator Traps"

    range_start = 0
    range_end = 5
    default = 5

class DeathLink(Toggle):
    """
    Death links are sent every time a heist is failed.
    After receiving a death link you will lose a down the next time you take damage.
    In a multiplayer session only the lobby host can send death links to avoid spam.
    """

    display_name = "Death Link"

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class PAYDAY2Options(PerGameCommonOptions):
    score_checks: ScoreLocations
    starting_time: StartingTime
    time_upgrades: TimeUpgrades
    time_bonus: TimeUpgradeStrength
    bots: BotCount
    armor_unlocks: ArmorCount
    deployables: DeployablesCount
    saws: AdditionalSaw
    primary_weapons: PrimaryCount
    akimbo: AkimboCount
    secondary_weapons: SecondaryCount
    melee_weapons: MeleeCount
    throwables: ThrowableCount
    final_difficulty: MaxDiff
    difficulty_traps: DiffTraps
    mutator_traps: MutatorTraps
    death_link: DeathLink