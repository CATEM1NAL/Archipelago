from dataclasses import dataclass

from Options import Choice, TextChoice, PerGameCommonOptions, Range, Toggle, OptionGroup, DefaultOnToggle

class GamePace(Choice):
    """
    QUICK: Start with 20 minutes, gain 20 with each time bonus.
    Score caps are higher and less likely to get hard stuck.

    STANDARD: Start with 10 minutes, gain 10 with each time bonus.

    GLACIAL: Start with 10 minutes, gain 5 with each time bonus.
    Adds 25 score checks, leads to more spheres and takes longer to goal.
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
    75 score checks, 4 safe house tiers. Timer caps at 60 minutes.
    Can take around ?? hours to goal (8 hours on Glacial).

    LONG DAY: 6 heists per run, with the first two being smaller scale.
    120 score checks, 6 safe house tiers. Timer caps at 90 minutes (100 on Quick).
    Can take around 12 hours to goal (?? hours on Glacial).

    POINTLESS DAY: Random heists. Win after maxing out your score.
    85 score checks, 2 safe house tiers. Timer caps at 100 minutes.
    Can take around ?? hours to goal (?? hours on Glacial).

    MOVING DAY: Random heists. Win after fully upgrading the safe house.
    130 score checks, 6 safe house tiers. Timer caps at 100 minutes.
    Can take around ?? hours to goal (?? hours on Glacial).

    The following modes are campaigns. They have 80 score checks, a single
    safe house tier, and the heists are fixed. Some of them require DLC to play,
    so check that you own the required heists before enabling them!

    RETURN OF THE RAT: Watch Dogs, Firestarter, Rats, Hoxton Revenge.

    MURKY DAY: Shadow Raid, Meltdown, Beneath the Mountain (DLC), Henry's Rock.

    I NEED MY PAYDAY TOO: Big Bank (DLC), The Diamond (DLC), Hotline Miami (DLC),
    Hoxton Breakout, Golden Grin Casino (DLC).

    GREATEST HEIST OF ALL: Reservoir Dogs (licensed), Brooklyn Bank,
    Shacklethorne Auction, Breakin' Feds, Hell's Island, White House.

    SILK ROAD: Border Crossing (DLC), San Martín Bank (DLC),
    Breakfast in Tijuana (DLC), Buluc's Mansion (DLC).

    CITY OF GOLD: Dragon Heist (DLC), Black Cat (DLC), Mountain Master (DLC).

    TEXAS HEAT: Midland Ranch (DLC), Hostile Takeover (DLC), Crude Awakening (DLC).

    CLASSICS: First World Bank, Heat Street, Panic Room, Green Bridge,
    Diamond Heist, Slaughterhouse.
    """

    display_name = "Game Mode"

    option_short_day = 1
    option_long_day = 2
    option_pointless_day = 3
    option_moving_day = 4
    option_return_of_the_rat = 100
    option_murky_day = 101
    option_i_need_my_payday_too = 102
    option_greatest_heist_of_all = 103
    option_silk_road = 104
    option_city_of_gold = 105
    option_texas_heat = 106
    option_classics = 107

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
    infinite_time: InfiniteTime
    game_mode: GameMode
    final_difficulty: MaxDiff
    death_link: DeathLink
    biglobby: BotCount