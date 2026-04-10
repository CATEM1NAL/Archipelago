tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as CommonContext
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext
from CommonClient import ClientCommandProcessor, server_loop, get_base_parser, handle_url_arg, logger
import Utils, asyncio, colorama, logging, json, os, shutil, math, time, random
from . import CrimDawnWorld, items
from .data_structs import safeHouseData
from collections.abc import Sequence
from .locations import LOCATION_NAME_TO_ID, triangle, safehouseRooms

from BaseClasses import ItemClassification as IC
from NetUtils import ClientStatus

path = "."

def load_json_file(fileName: str) -> dict:
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

class CrimDawnCommandProcessor(ClientCommandProcessor):
    def _cmd_score(self):
        """See your current score and progress to next check."""
        if isinstance(self.ctx, CrimDawnContext):
            nextScoreCheck = triangle(self.ctx.n + 1)
            logger.info(f"Current score: {self.ctx.score}/{self.ctx.scoreCaps[self.ctx.timeBonusReceived]}. "
                        f"Next check at {nextScoreCheck} points ({nextScoreCheck - self.ctx.score} more).\n"
                        f"Sent {100 * (self.ctx.score / self.ctx.scoreCaps[-1]):.2f}% of total score checks.")

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
        slotName = self.context.player_names[self.context.slot]
        funnyWeapons = ["HRL-7", "Heavy Crossbow", "SG Versteckt 51D Light Machine Gun", "Two Handed Great Ruler",
                        "Cash Blaster", "Inspector Gadget Character Pack", "backing of an entire nation state"]
        deathMsgs = [f"{slotName} left their favourite cassette in the escape car.",
                     f"{slotName} needs to get their head examined.",
                     f"{slotName} learned that crime doesn't pay.",
                     f"{slotName} watched dawn turn to dusk.",
                     f"{slotName} doesn't have a razor mind.",
                     f"{slotName} got caught up in that Kataru business.",
                     f"The escape van left {slotName} behind.",
                     f"{slotName} was overwhelmed by DLC.",
                     f"Scrungle found {slotName}. Nobody escapes Scrungle.",
                     f"It's not {slotName}'s fault, they just had a bad build.",
                     f"If {slotName} had the {random.choice(funnyWeapons)}, that wouldn't have happened."]

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

                            if prevHeistsWon < heistsWon:
                                prevHeistsWon = heistsWon
                                if heistsWon > self.context.runLength:
                                    heistsWon = self.context.runLength
                                for i in range (1, heistsWon + 1):
                                    print(f"Heist {i} Completed")
                                    heist = LOCATION_NAME_TO_ID[f"Heist {i} Completed"]
                                    await self.context.check_locations([heist])
                                if 0 < self.context.runLength == heistsWon:
                                    await self.context.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

                            if prevRun == -1: prevRun = run

                            # Send deathlink
                            if prevRun < run:
                                prevRun = run
                                await self.context.send_death(random.choice(deathMsgs))

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
        self.n = 0
        self.scrungle_task = None
        self.deathLinkPending = False
        self.createRoomLoc = False

        self.safehouseIdToName = {
            "terry": safeHouseData("Scarface's Room", "menu_cs_help_terry"),
            "russian": safeHouseData("Dallas' Office", "menu_cs_help_dallas"),
            "old_hoxton": safeHouseData("Hoxton's Files", "menu_cs_help_hoxton"),
            "clover": safeHouseData("Clover's Surveillance Center", "menu_cs_help_clover"),
            "myh": safeHouseData("Duke's Gallery", "menu_cs_help_myh"),
            "sydney": safeHouseData("Sydney's Studio", "menu_cs_help_sydney"),
            "american": safeHouseData("Houston's Workshop", "menu_cs_help_houston"),
            "wild": safeHouseData("Rust's Corner", "menu_cs_help_rust"),
            "ecp": safeHouseData("h3h3", "menu_cs_help_ecp"),
            "joy": safeHouseData("Joy's Van", "menu_cs_help_joy"),
            "bonnie": safeHouseData("Bonnie's Gambling Den", "menu_cs_help_bonnie"),
            "dragon": safeHouseData("Jiro's Lounge", "menu_cs_help_dragon"),
            "dragan": safeHouseData("Dragan's Gym", "menu_cs_help_dragan"),
            "jimmy": safeHouseData("Jimmy's Bar", "menu_cs_help_jimmy"),
            "livingroom": safeHouseData("Common Rooms", "menu_cs_help_common_room"),
            "max": safeHouseData("Sangres' Cave", "menu_cs_help_max"),
            "spanish": safeHouseData("Chains' Weapons Workshop", "menu_cs_help_chains"),
            "bodhi": safeHouseData("Bodhi's Surfboard Workshop", "menu_cs_help_bodhi"),
            "jacket": safeHouseData("Jacket's Hangout", "menu_cs_help_jacket"),
            "sokol": safeHouseData("Sokol's Hockey Gym", "menu_cs_help_sokol"),
            "vault": safeHouseData("Vault", "menu_cs_help_vault"),
            "german": safeHouseData("Wolf's Workshop", "menu_cs_help_wolf"),
            "jowi": safeHouseData("Wick's Shooting Range", "menu_cs_help_jowi")
        }

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(CrimDawnContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args) # THIS IS FOR UNIVERSAL TRACKER, DIPSHIT.

        if cmd == 'Connected':
            self.on_connected(args)

        if cmd == "ReceivedItems":
            self.on_received_items(args)

        if cmd == "LocationInfo":
            if self.createRoomLoc:
                self.createRoomLoc = False

                keys = list(self.safehouseIdToName)
                tier = 1
                count = 0

                itemTypeLookup = {
                    0: "Boring.",
                    1: "This seems important!",
                    2: "This seems useful!",
                    3: "This seems very important!",
                    4: "This seems dangerous...",
                    5: "This seems important, but also dangerous.",
                    6: "This seems useful, but also dangerous.",
                    7: "This seems very important, but also dangerous.",
                }
                rooms = {}
                for NetworkItem in args["locations"]:
                    playerName = self.player_names[NetworkItem.player]
                    itemName = self.item_names.lookup_in_slot(NetworkItem.item, NetworkItem.player)
                    itemHint = f"{playerName}'s ##{itemName}##.\n{itemTypeLookup[NetworkItem.flags]}"

                    rooms[f"{self.safehouseIdToName[keys[count]].descId}_{tier}"] = itemHint
                    count += 1
                    if count == 23:
                        tier += 1
                        count = 0
                with open(self.path + "crimdawn_rooms.txt", "w+") as f:
                    json.dump(rooms, f)
                return

            super().on_package(cmd, args)

        if cmd == "Bounced":
            if "tags" in args:
                if "DeathLink" in args["tags"]:
                    self.on_deathlink(args["data"])

    def on_connected(self, args: dict):
        if self.scrungle_task:
            self.scrungle_task.cancel()
            self.scrungle_task = None

        version = CrimDawnWorld.world_version.as_simple_string()
        self.timeBonusReceived = 0

        # Error checking
        if version != args['slot_data']['server_version']:
            logger.info(f"WARNING: Server ({args['slot_data']['server_version']}) and client ({version}) are using different versions of the APWorld!")

        self.path = os.path.dirname(CrimDawnWorld.settings.payday2_path) + "/mods/saves/"
        self.scribble = scribble(self.path + "crimdawn_client.txt")

        if not os.path.isfile(CrimDawnWorld.settings.payday2_path):
            raise Exception('ERROR: Scrungle no find payday2_win32_release.exe.\nScrungle kindly requests that you remove payday2_path from host.yaml')

        elif not os.path.exists(self.path):
            raise Exception('ERROR: Scrungle no find /mods/saves.\nScrungle want you to check that you have SuperBLT installed.')

        # Check seed
        self.scribble.writeVariable("seed", args['slot_data']['seed_name'])
        print("Wrote seed to client file")

        modSeed, modSlot = False, False

        try:
            modSave = load_json_file(self.path + "crimdawn_save.txt")

            try:
                modSeed = modSave["game"]["seed"]
            except KeyError:
                pass

            try:
                modSlot = modSave["game"]["slot"]
            except KeyError:
                pass

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"Couldn't load crimdawn_save.txt: {e}")

        # Switch saves automatically if the seed/slot names don't match
        if (modSeed and modSeed != args['slot_data']['seed_name']) or (modSlot and modSlot != self.player_names[self.slot]):
            try:
                os.mkdir(self.path + "crimdawn_saves")
            except FileExistsError:
                pass

            try:
                saveName = f"{modSeed}_{modSlot}"
                targetSave = f"{args['slot_data']['seed_name']}_{self.player_names[self.slot]}"

                shutil.copy2(self.path + "crimdawn_save.txt", self.path + "crimdawn_saves/" + saveName)
                os.remove(self.path + "crimdawn_save.txt")
                os.remove(self.path + "crimdawn_rooms.txt")

                msg = "No pre-existing save found for this slot."
                for save in os.listdir(self.path + "crimdawn_saves"):
                    if save == targetSave:
                        shutil.copy2(self.path + "crimdawn_saves/" + targetSave, self.path + "crimdawn_save.txt")
                        msg = "Successfully found and restored old save!"
                        break

                logger.info(f"{msg}\nPrevious save was moved to 'PAYDAY 2/mods/saves/crimdawn_saves' - you should clear this folder out from time to time!\n"
                                "If the game is currently open, you will need to restart it.")

            except Exception as e: # If save handler fails, fallback to old error
                logger.error(e)
                raise Exception("ERROR: Your Criminal Dawn save was made on a different seed.\n\n"
                             "Delete your save with the following steps:\n"
                             "1) Launch PAYDAY 2.\n"
                             "2) Click 'OPTIONS'.\n"
                             "3) Click 'ADVANCED'.\n"
                             "4) Click 'RESET ACCOUNT PROGRESSION'.\n"
                             "5) Click 'YES' and wait for the game to reload.\n\n"
                             "You can reconnect after the game finishes reloading.")
            # If you see this error then something has gone horribly wrong. Tell me about it!

        if not self.scrungle_task:
            self.scrungle = scrungle(self.path + "crimdawn_save.txt", self)
            self.scrungle_task = asyncio.create_task(self.scrungle.watch(), name='scrungle')

        self.itemDict = items.itemDict

        self.goal = args['slot_data']['goal']
        self.runLength = args['slot_data']['run_length']
        self.scoreCaps = args['slot_data']["score_caps"]
        self.campaign = args['slot_data']["campaign"]


        self.scribble.writeVariable("goal", self.goal)
        self.scribble.writeVariable("timer_strength", args['slot_data']['progression_pacing'])
        self.scribble.writeVariable("run_length", self.runLength)
        self.scribble.writeVariable("max_diff", args['slot_data']['final_difficulty'])
        self.scribble.writeVariable("score_cap", self.scoreCaps[self.timeBonusReceived])
        self.scribble.writeVariable("max_diff_items", args['slot_data']['diff_scale_count'])
        self.scribble.writeVariable("slot", self.player_names[self.slot])
        self.scribble.writeVariable("campaign", self.campaign)

        self.deathLinkEnabled = args['slot_data']["death_link"]
        if self.deathLinkEnabled:
            asyncio.create_task(self.update_death_link(True))

        keys = list(self.safehouseIdToName)
        self.safehouseRooms = []

        for i in range(1, self.runLength + 1):
            for j in range(23):
                self.safehouseRooms.append(LOCATION_NAME_TO_ID[f"{self.safehouseIdToName[keys[j]].name} (Tier {i})"])
                #print(f"{self.safehouseIdToName[keys[j]].name} (Tier {i})")

        if not os.path.isfile(self.path + "crimdawn_rooms.txt"):
            self.createRoomLoc = True
            asyncio.create_task(self.send_msgs([{
                "cmd": "LocationScouts",
                "locations": self.safehouseRooms,
                "create_as_hint": 0
            }]))

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
                logger.error(e)
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
        return math.floor((math.sqrt(1 + 8 * score) - 1) / 2)

    async def score_check(self, score):
        try:
            # Solve triangular number
            self.n = self.getN(score)
            for i in range(1, self.n + 1):
                if i in self.missing_locations:
                    await self.check_locations([i])

            self.score = score

        except KeyError as e:
            logger.error(f"Score Key Error: {e}")

    async def safehouse_check(self, safehouseDict):
        try:
            for key, tier in safehouseDict.items():
                for i in range(1, tier):
                    id = LOCATION_NAME_TO_ID[f"{self.safehouseIdToName[key].name} (Tier {i})"]
                    if id in self.missing_locations:
                        await self.check_locations([id])

            if self.goal == "Moving Day":
                flag = True
                for location in self.safehouseLocations:
                    id = LOCATION_NAME_TO_ID[location]
                    if id in self.missing_locations:
                        flag = False
                        break
                if flag:
                    await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

        except KeyError as e:
            logger.error(f"Safehouse Key Error: {e}")

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