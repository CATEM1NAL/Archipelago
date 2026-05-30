from dataclasses import dataclass

from Options import Choice, TextChoice, PerGameCommonOptions, Range, Toggle, OptionGroup, DefaultOnToggle

class Goal(Choice):
    """
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

    CLASSICS: First World Bank, Heat Street, Panic Room, Green Bridge, Diamond Heist, Slaughterhouse.
    YOU GUYS NO FUN: Four Stores, Mallcrasher, Nightclub, Aftershock, Meltdown.
    RETURN OF THE RAT: Watchdogs, Firestarter day 1, Rats, Hoxton Breakout day 2, Hoxton Revenge.
    DEATH OF DEMOCRACY: Framing Frame day 3, Election Day bank, Big Oil day 2.
    MURKY DAY: Shadow Raid, Meltdown, Beneath the Mountain (DLC), Henry's Rock.
    I NEED MY PAYDAY TOO: Big Bank (DLC), The Diamond (DLC), Hotline Miami (DLC), Hoxton Breakout day 1, Golden Grin Casino (DLC).
    GREATEST HEIST OF ALL: Reservoir Dogs (DLC), Brooklyn Bank, Shacklethorne Auction, Breakin' Feds, Hell's Island, White House.
    SILK ROAD: Border Crossing (DLC), San Martín Bank (DLC), Breakfast in Tijuana (DLC), Buluc's Mansion (DLC).
    CITY OF GOLD: Dragon Heist (DLC), Black Cat (DLC), Mountain Master (DLC).
    TEXAS HEAT: Midland Ranch (DLC), Hostile Takeover (DLC), Crude Awakening (DLC).
    FOLLOW THE MONEY: Bank Heist: Cash, GO Bank, Brooklyn Bank, San Martín Bank (DLC), First World Bank, Big Bank (DLC).
    GUN RUNNERS: Firestarter day 1, Aftershock, Brooklyn 10-10 (DLC), Bomb: Dockyard (DLC), Midland Ranch (DLC), Border Crossing (DLC).
    STEALTH MISSION: Breakin' Feds, Yacht Heist (DLC), Murky Station (licensed), Shadow Raid, Car Shop.
    """

    display_name = "Campaign"

    option_classics = 1
    option_you_guys_no_fun = 2
    option_return_of_the_rat = 3
    option_death_of_democracy = 4
    option_murky_day = 5
    option_i_need_my_payday_too = 6
    option_greatest_heist_of_all = 7
    option_silk_road = 8
    option_city_of_gold = 9
    option_texas_heat = 10
    option_follow_the_money = 11
    option_gun_runners = 12
    option_stealth_mission = 100

    default = option_classics

class RunLength(Range):
    """
    Only used if 'Original' is selected as the goal.

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
    The 'Score' goal can fail to generate if this is too high.
    """

    display_name = "Safe House Tiers"

    range_start = 0
    range_end = 6

    default = 4

class ScoreChecks(Range):
    """
    Base number of score checks. Each check requires one more point than the last, so this scales quite fast!
    This is increased by other options, so the actual number of score checks will often be higher.
    Solo worlds will fail to generate if this is set too low. 60 is a good starting point!
    """

    display_name = "Score Checks"

    range_start = 0
    range_end = 100

    default = 68

class EarlyBot(DefaultOnToggle):
    """
    Force a bot to generate in sphere 1, guaranteeing that you get an early bot.
    This can make the early game significantly easier. If you are playing alone, keeping this on is recommended!
    """

    display_name = "Early Bot"

class BotCount(Toggle):
    """
    Whether BigLobby is installed. Adds 20 extra score checks when enabled.
    Enabling this increases the number of extra bots from 3 all the way up to 21, however the game may become less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "BigLobby"

@dataclass
class CrimDawnOptions(PerGameCommonOptions):
    goal: Goal
    campaign: Campaign
    run_length: RunLength
    score_checks: ScoreChecks
    safehouse_tiers: SafehouseTiers
    early_bot: EarlyBot
    biglobby: BotCount

presets = {
    "4 Heists (~5 hours)": {
        "goal": 1,
        "run_length": 4,
        "safehouse_tiers": 4,
        "score_checks": 68,
    },
    "4 Heists Turbo (~4 hours)": {
        "goal": 1,
        "run_length": 4,
        "safehouse_tiers": 2,
        "score_checks": 54,
    },
    "6 Heists (~8 hours)": {
        "goal": 1,
        "run_length": 6,
        "safehouse_tiers": 6,
        "score_checks": 72,
    },
    "6 Heists Turbo (~4 hours)": {
        "goal": 1,
        "run_length": 6,
        "safehouse_tiers": 3,
        "score_checks": 66,
    },
    "3240 Points (~3 hours)": {
        "goal": 3,
        "safehouse_tiers": 2,
        "score_checks": 64,
    },
    "Campaign (~4 hours)": {
        "goal": 2,
        "safehouse_tiers": 1,
        "score_checks": 77,
    },
}