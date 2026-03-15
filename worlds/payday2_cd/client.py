from CommonClient import CommonContext, ClientCommandProcessor, server_loop, get_base_parser, handle_url_arg, logger
import Utils, asyncio, colorama, logging, json, os, math, time, random
from . import PAYDAY2World
from . import items
from .item_types import itemType, itemData
from collections.abc import Sequence
from .locations import LOCATION_NAME_TO_ID

from BaseClasses import ItemClassification as IC
from NetUtils import ClientStatus

path = "."

def load_json_file(fileName: str) -> dict:
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        return {}

class PAYDAY2CommandProcessor(ClientCommandProcessor):

    def _score(self):
        """Displays your current score."""
        if isinstance(self.ctx, PAYDAY2Context):
            logger.info(f"Current score: {1}")

# scribble likes to write
class scribble:
    def __init__(self, path):
        self.data = {}
        self.path = path
        print(f"Scribble is scribing {self.path}...")

    def run(self, key):
        try:
            self.data[key] += 1
        except KeyError:
            self.data[key] = 1
        with open(self.path, "w+") as f:
            json.dump(self.data, f)

    def writeVariable(self, key, value):
        self.data[key] = value
        with open(self.path, "w+") as f:
            json.dump(self.data, f)

# scrungle likes to watch
class scrungle:
    def __init__(self, path, context):
        self.context = context
        self.path = path

    # function derived from Project Diva APWorld
    async def watch(self):
        modSave = load_json_file(self.path)
        prevScore = 0
        prevHeistsWon = 0
        prevRun = -1
        lastChatTime = None
        lastModTime = os.path.getmtime(self.path) if os.path.isfile(self.path) else 0.0
        lastModTime = 0
        deathMsgs = ["left their favourite cassette in the escape car.",
                     "will never hear those songs again.",
                     "needs to get their head examined.",
                     "learned that crime doesn't pay.",
                     "watched dawn turn to dusk.",
                     "doesn't have a razor mind.",
                     "got caught up in that Kataru business.",
                     "was foiled at the hands of Commissioner Garrett."]

        print(f"Scrungle is watching {self.path}...")

        while True:
            try:
                if os.path.isfile(self.path):
                    modTime = os.path.getmtime(self.path)

                    if modTime > lastModTime:
                        lastModTime = modTime

                        try:
                            modSave = load_json_file(self.path)
                            score = modSave["game"]["score"]
                            run = modSave["game"]["run"]
                            heistsWon = modSave["game"]["heists_won"]

                            # Not in the except so people that play without autorelease can continue getting checks
                            if score > prevScore:
                                await self.context.score_check(score)
                                prevScore = score

                            if heistsWon > prevHeistsWon:
                                for i in range (1, heistsWon + 1):
                                    print(f"Heist {i} Completed")
                                    heist = LOCATION_NAME_TO_ID[f"Heist {i} Completed"]
                                    await self.context.check_locations([heist])
                                if heistsWon > 5:
                                    await self.context.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                                prevHeistsWon = heistsWon

                            if prevRun == -1: prevRun = run
                            # Send deathlink
                            if prevRun < run:
                                prevRun = run
                                await self.context.send_death(f"{self.context.player_names[self.context.slot]} {random.choice(deathMsgs)}")

                        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
                            print(f"Couldn't load crimdawn_save.txt: {e}")

                        try:
                            safehouseDict = modSave["safehouse"]
                            if safehouseDict != []:
                                await self.context.safehouse_check(safehouseDict)
                        except Exception as e:
                            print(f"Couldn't find crimdawn_save.txt: {e}")

                        try:
                            commandprocessor = self.context.command_processor(self.context)
                            chatMessage = modSave["chat"]["message"]
                            chatTimestamp = modSave["chat"]["timestamp"]
                            if not lastChatTime:
                                lastChatTime = chatTimestamp

                            if chatMessage != "" and chatTimestamp > lastChatTime:
                                print("Sending chat message!")
                                commandprocessor(chatMessage)
                                lastChatTime = chatTimestamp
                        except Exception as e:
                            print(f"Couldn't find crimdawn_save.txt: {e}")
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                print("Scrungle stopped watching. Scrungle bored.")
            except Exception as e:
                print(e)

class PAYDAY2Context(CommonContext):
    game = "PAYDAY 2: Criminal Dawn"
    command_processor = PAYDAY2CommandProcessor
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.initialized = False
        self.score = 0
        self.scrungle_task = None
        self.deathLinkPending = False
        self.timeBonusReceived = 0

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(PAYDAY2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == 'Connected':
            self.on_connected(args)
        elif cmd == "ReceivedItems":
            self.on_received_items(args)
        elif cmd == "Bounced":
            if "tags" in args:
                if "DeathLink" in args["tags"]:
                    self.on_deathlink(args["data"])

    def on_connected(self, args: dict):
        version = PAYDAY2World.world_version.as_simple_string()

        # Error checking
        if version != args['slot_data']['server_version']:
            logger.info(f"WARNING: Server ({args['slot_data']['server_version']}) and client ({version}) are using different versions of the APWorld!")

        self.path = os.path.dirname(PAYDAY2World.settings.payday2_path) + "/mods/saves/"
        self.scribble = scribble(self.path + "crimdawn_client.txt")

        if not os.path.isfile(PAYDAY2World.settings.payday2_path):
            logger.error('ERROR: Scrungle no find payday2_win32_release.exe.\nScrungle kindly requests that you remove payday2_path from host.yaml')
            Utils.async_start(self.disconnect())

        elif not os.path.exists(self.path):
            logger.error('ERROR: Scrungle no find /mods/saves.\nScrungle want you to check that you have SuperBLT installed.')
            Utils.async_start(self.disconnect())

        # Check seed
        self.scribble.writeVariable("seed", args['slot_data']['seed_name'])
        print(f"Wrote seed to client file")

        try:
            modSave = load_json_file(self.path + "crimdawn_save.txt")

            try:
                modSeed = modSave["game"]["seed"]
            except (KeyError):
                modSeed = False

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"Couldn't load crimdawn_save.txt: {e}")

        try:
            if modSeed != args['slot_data']['seed_name'] and modSeed != False:
                logger.error("ERROR: Your Criminal Dawn save was made on a different seed.\n"
                             "Only one multiworld can currently be played at a time.\n\n"
                             "Delete your save with the following steps:\n"
                             "1) Launch PAYDAY 2.\n"
                             "2) Click 'OPTIONS'.\n"
                             "3) Click 'ADVANCED'.\n"
                             "4) Click 'RESET ACCOUNT PROGRESSION'.\n"
                             "5) Click 'YES' and wait for the game to reload.\n\n"
                             "You can reconnect after the game finishes reloading.")
                Utils.async_start(self.disconnect())

        except:
            pass

        if not self.scrungle_task:
            self.scrungle = scrungle(self.path + "crimdawn_save.txt", self)
            self.scrungle_task = asyncio.create_task(self.scrungle.watch(), name='scrungle')

        self.itemDict = items.itemDict

        self.scoreCaps = args['slot_data']["score_caps"]
        self.timerStrength = args['slot_data']['timer_strength']
        self.finalDifficulty = args['slot_data']['final_difficulty']
        self.diffScale = args['slot_data']['scaling_count']

        self.scribble.writeVariable("timer_strength", self.timerStrength)
        self.scribble.writeVariable("max_diff", self.finalDifficulty)
        self.scribble.writeVariable("score_cap", self.scoreCaps[self.timeBonusReceived])
        self.scribble.writeVariable("scaling_count", self.diffScale)

        self.deathLinkEnabled = args['slot_data']["death_link"]
        if self.deathLinkEnabled:
            asyncio.create_task(self.update_death_link(True))

    def on_received_items(self, args: dict):
        # for entry in self.items_received:
        for entry in args["items"]:
            try:
                item = self.itemDict[entry.item]
            except KeyError as e:
                logger.error(e)
                logger.error(f"KEY ERROR: {entry.item}")
                continue
            except Exception as e:
                logger.error(f"FATAL ERROR: {entry.item}")
                continue

            self.scribble.run(item.name)

            if item.name == "Time Bonus":
                self.timeBonusReceived += 1
                self.scribble.writeVariable("score_cap", self.scoreCaps[self.timeBonusReceived])

    def getN(self, score):
        return math.floor((math.sqrt(1 + 8 * (score)) - 1) / 2)

    async def score_check(self, score):
        try:
            # Solve triangular number
            n = self.getN(score)
            for i in range(1, n + 1):
                await self.check_locations([i])

            self.score = score
                
        except KeyError as e:
            logger.error(e)

    async def safehouse_check(self, safehouseDict):
        try:
            safehouseIdToName = {
                "terry": "Scarface's Room",
                "russian": "Dallas' Office",
                "old_hoxton": "Hoxton's Files",
                "clover": "Clover's Surveillance Center",
                "myh": "Duke's Gallery",
                "sydney": "Sydney's Studio",
                "american": "Houston's Workshop",
                "wild": "Rust's Corner",
                "ecp": "h3h3",
                "joy": "Joy's Van",
                "bonnie": "Bonnie's Gambling Den",
                "dragon": "Jiro's Lounge",
                "dragan": "Dragan's Gym",
                "jimmy": "Jimmy's Bar",
                "livingroom": "Common Rooms",
                "max": "Sangres' Cave",
                "spanish": "Chains' Weapons Workshop",
                "bodhi": "Bodhi's Surfboard Workshop",
                "jacket": "Jacket's Hangout",
                "sokol": "Sokol's Hockey Gym",
                "vault": "Vault",
                "german": "Wolf's Workshop",
                "jowi": "Wick's Shooting Range"
            }

            for key, tier in safehouseDict.items():
                for i in range(2,tier+1):
                    Id = LOCATION_NAME_TO_ID[f"{safehouseIdToName[key]} - Tier {i}"]
                    await self.check_locations([Id])

        except KeyError as e:
            logger.error(e)

    # Deathlink handlers
    def on_deathlink(self, data: dict):
        if self.deathLinkPending:
            return
        self.scribble.writeVariable("deathlink", math.floor(time.time()))
        super().on_deathlink(data)
        asyncio.create_task(self.resetDeathLinkFlag())

    async def send_death(self, death_text: str = ""):
        if self.deathLinkPending:
            return
        if self.deathLinkEnabled:
            self.deathLinkPending = True
            asyncio.create_task(super().send_death(death_text))
            asyncio.create_task(self.resetDeathLinkFlag())

    async def resetDeathLinkFlag(self):
        await asyncio.sleep(3)
        self.deathLinkPending = False

    def run_gui(self):
        from kvui import GameManager

        class PAYDAY2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = self.game + " Client"

        self.ui = PAYDAY2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

def launch_client(*args: Sequence[str]):
    Utils.init_logging('PAYDAY2Client')
    logging.getLogger().setLevel(logging.INFO)

    async def main(args):
        ctx = PAYDAY2Context(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name='ServerLoop')

        if Utils.gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    parser = get_base_parser()
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()