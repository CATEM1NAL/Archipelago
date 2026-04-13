from dataclasses import dataclass

from Options import Choice, TextChoice, PerGameCommonOptions, Range, Toggle, OptionGroup, DefaultOnToggle

class GamePace(Choice):
    """
    QUICK: Start with 20 minutes, gain 20 with each time bonus.
    Score caps are higher and less likely to get hard stuck.

    STANDARD: Start with 10 minutes, gain 10 with each time bonus.

    GLACIAL: Start with 10 minutes, gain 5 with each time bonus.
    Adds 10 score checks. Leads to more spheres and takes longer to goal.
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

    This has no effect with the 'Score' goal.
    """

    display_name = "Infinite Time"

class Goal(Choice):
    """
    What you need to do to complete the world.

    ORIGINAL: Finish a run consisting of random tiered heists.
    CAMPAIGN: Finish a preset run with a fixed set of heists.
    SCORE: Send every score check. Heists are completely random.
    """

    display_name = "Goal"

    option_original = 1
    option_campaign = 2
    option_score = 3

    default = option_original

class Campaign(Choice):
    """
    Only used if 'Campaign' is selected as the goal.

    You need to own all the DLC in a campaign to be able to play it!
    If you don't own one of the heists, the game will crash.

    CLASSICS:
    First World Bank, Heat Street, Panic Room, Green Bridge, Diamond Heist, Slaughterhouse.

    RETURN OF THE RAT:
    Watchdogs, Firestarter Day 1, Rats, Hoxton Revenge.

    MURKY DAY:
    Shadow Raid, Meltdown, Beneath the Mountain (DLC), Henry's Rock.

    I NEED MY PAYDAY TOO:
    Big Bank (DLC), The Diamond (DLC), Hotline Miami (DLC), Hoxton Breakout, Golden Grin Casino (DLC).

    GREATEST HEIST OF ALL:
    Reservoir Dogs (DLC), Brooklyn Bank, Shacklethorne Auction, Breakin' Feds, Hell's Island, White House.

    SILK ROAD:
    Border Crossing (DLC), San Martín Bank (DLC), Breakfast in Tijuana (DLC), Buluc's Mansion (DLC).

    CITY OF GOLD:
    Dragon Heist (DLC), Black Cat (DLC), Mountain Master (DLC).

    TEXAS HEAT:
    Midland Ranch (DLC), Hostile Takeover (DLC), Crude Awakening (DLC).
    """

    display_name = "Campaign"

    option_classics = 1
    option_return_of_the_rat = 2
    option_murky_day = 3
    option_i_need_my_payday_too = 4
    option_greatest_heist_of_all = 5
    option_silk_road = 6
    option_city_of_gold = 7
    option_texas_heat = 8

    default = option_classics

class RunLength(Range):
    """
    Only used if 'Heist' is selected as the goal.

    How many heists you need to finish to win.
    The final heist is always White House or Crude Awakening (if you own it).
    """

    display_name = "Run Length"

    range_start = 1
    range_end = 6

    default = 4

class SafehouseTiers(Range):
    """
    How many times you can upgrade the safe house. Adds 8 score checks per tier.
    Solo worlds can fail to generate if this is too high and there aren't enough score checks.
    """

    display_name = "Safe House Tiers"

    range_start = 0
    range_end = 6

    default = 4

class ScoreChecks(Range):
    """
    Base number of score checks. Each check requires one more point than the last, so this scales quite fast!
    This is increased by other options, so the actual number of score checks will often be higher.
    Solo worlds will fail to generate if this is set too low. 60 is a good starting point.
    """

    display_name = "Score Checks"

    range_start = 0
    range_end = 100

    default = 43

class EarlyBot(DefaultOnToggle):
    """
    Forces an extra bot to generate in sphere 1, guaranteeing that you get an early bot.
    This can make the early game significantly easier. If you are playing alone, turning this on is recommended.
    """

    display_name = "Early Bot"

class BotCount(Toggle):
    """
    Whether BigLobby is installed. Adds 20 extra score checks when enabled.
    Enabling this increases the number of extra bots from 3 all the way up to 21, however the game may become less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "BigLobby"

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
    goal: Goal
    campaign: Campaign
    run_length: RunLength
    safehouse_tiers: SafehouseTiers
    score_checks: ScoreChecks
    death_link: DeathLink
    early_bot: EarlyBot
    biglobby: BotCount

presets = {
    "4 Heists (~8 hours)": {
        "goal": 1,
        "run_length": 4,
        "safehouse_tiers": 4,
        "score_checks": 68,
    },
    "6 Heists (~12 hours)": {
        "goal": 1,
        "run_length": 6,
        "safehouse_tiers": 6,
        "score_checks": 72,
    },
    "3240 Points (~? hours)": {
        "goal": 3,
        "safehouse_tiers": 2,
        "score_checks": 64,
    },
    "Campaign": {
        "goal": 2,
        "safehouse_tiers": 1,
        "score_checks": 77,
    },
}