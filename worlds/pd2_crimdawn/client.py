tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as CommonContext
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext
from CommonClient import ClientCommandProcessor, server_loop, get_base_parser, handle_url_arg, logger
import Utils, asyncio, colorama, logging, json, os, math, time, random
from . import CrimDawnWorld
from . import items
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

class CrimDawnCommandProcessor(ClientCommandProcessor):

    def _score(self):
        """Displays your current score."""
        if isinstance(self.ctx, CrimDawnContext):
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

    async def watch(self):
        modSave = load_json_file(self.path)
        prevScore = 0
        prevHeistsWon = 0
        prevRun = -1
        lastChatTime = math.floor(time.time())
        lastModTime = 0
        deathMsgs = ["left their favourite cassette in the escape car.",
                     "needs to get their head examined.",
                     "learned that crime doesn't pay.",
                     "watched dawn turn to dusk.",
                     "doesn't have a razor mind.",
                     "got caught up in that Kataru business."]

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

                            if score > prevScore:
                                await self.context.score_check(score)
                                prevScore = score

                            if heistsWon > prevHeistsWon:
                                for i in range (1, heistsWon + 1):
                                    print(f"Heist {i} Completed")
                                    heist = LOCATION_NAME_TO_ID[f"Heist {i} Completed"]
                                    await self.context.check_locations([heist])
                                if heistsWon > self.context.runLength - 1:
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
                break
            except Exception as e:
                print(e)

class CrimDawnContext(CommonContext):
    game = "PAYDAY 2: Criminal Dawn"
    tags = {"AP"}
    command_processor = CrimDawnCommandProcessor
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.score = 0
        self.scrungle_task = None
        self.deathLinkPending = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(CrimDawnContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == 'Connected':
            self.on_connected(args)
        elif cmd == "ReceivedItems":
            self.on_received_items(args)
        elif cmd == "Bounced":
            if "tags" in args:
                if "DeathLink" in args["tags"]:
                    self.on_deathlink(args["data"])

    def on_connected(self, args: dict):
        version = CrimDawnWorld.world_version.as_simple_string()
        self.timeBonusReceived = 0

        # Error checking
        if version != args['slot_data']['server_version']:
            logger.info(f"WARNING: Server ({args['slot_data']['server_version']}) and client ({version}) are using different versions of the APWorld!")

        self.path = os.path.dirname(CrimDawnWorld.settings.payday2_path) + "/mods/saves/"
        self.scribble = scribble(self.path + "crimdawn_client.txt")

        if not os.path.isfile(CrimDawnWorld.settings.payday2_path):
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
        self.timerStrength = args['slot_data']['progression_pacing']
        self.runLength = args['slot_data']['run_length']
        self.finalDifficulty = args['slot_data']['final_difficulty']
        self.diffScale = args['slot_data']['diff_scale_count']

        self.scribble.writeVariable("timer_strength", self.timerStrength)
        self.scribble.writeVariable("run_length", self.runLength)
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
                #print(f"{self.timeBonusReceived}: {self.scoreCaps}")
                self.timeBonusReceived += 1
                if self.timeBonusReceived < len(self.scoreCaps):
                    self.scribble.writeVariable("score_cap", self.scoreCaps[self.timeBonusReceived])
                    logger.info(f"Score cap increased to {self.scoreCaps[self.timeBonusReceived]}!")
                else:
                    self.scribble.writeVariable("score_cap", self.scoreCaps[-1])

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
                    Id = LOCATION_NAME_TO_ID[f"{safehouseIdToName[key]} (Tier {i})"]
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

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = f"{self.game} Client"
        return ui

def launch_client(*args: Sequence[str]):
    Utils.init_logging('CrimDawnClient')
    logging.getLogger().setLevel(logging.INFO)

    async def main(args):
        ctx = CrimDawnContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name='ServerLoop')

        if tracker_loaded:
            ctx.run_generator()
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