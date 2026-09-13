from javascript import require, On, Once, AsyncTask, once, off
from simple_chalk import chalk
from time import sleep
import sys

sys.path.insert(1, 'C:\\Users\\nicol\\Documents\\Ai_Girlfriend\\venv\\Ai_Girlfriend')
sys.path.insert(1, 'C:\\Users\\nicol\\Documents\\Ai_Girlfriend\\venv')

from alfie_chat import *

mineflayer = require("mineflayer")
mineflayer_pathfinder = require("mineflayer-pathfinder")
vec3 = require("vec3")

server_host = "localhost"
server_port = 1234
reconnect = True

follow_toggle = False

def vec3_to_str(v):
    return f"x: {v['x']:.3f}, y: {v['y']:.3f}, z: {v['z']:.3f}"

def vec3_to_dict(v):
    return {"x": v['x'], "y": v['y'], "z": v['z']}

class MCBot:
    def __init__(self, bot_name):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False,
        }
        self.reconnect = reconnect
        self.bot_name = bot_name
        self.start_bot()

    def log(self, message):
        print(f"[{self.bot.username}] {message}")

    def pathfind_to_goal(self, goal_location):
        try:
            self.bot.pathfinder.setGoal(
                mineflayer_pathfinder.pathfinder.goals.GoalNear(
                    goal_location["x"], goal_location["y"], goal_location["z"], 1
                )
            )
        except Exception as e:
            self.log(f"Error: {e}")

    def start_bot(self):

        self.bot = mineflayer.createBot(self.bot_args)
        self.bot.loadPlugin(mineflayer_pathfinder.pathfinder)

        self.start_events()

    def start_events(self):

        @On(self.bot, "login")
        def login(this):
            self.log(chalk.green(f"Logged in"))

            self.bot.chat("Hello mate!")

        @On(self.bot, "kicked")
        def kicked(this):
            self.log(chalk.redBright(f"Got kicked"))

        @On(self.bot, "entityHurt")
        def gotAttacked(this, that, those):
            self.bot.swingArm()

        @On(self.bot, "move")
        def look_it(this, that):
            target = self.bot.nearestEntity()
            if target:
                self.bot.lookAt(target.position.offset(0, 1, 0))
            global follow_toggle
            if follow_toggle:
                vec3_temp = followed_player.entity.position
                player_location = vec3(
                    vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
                )
                if player_location:
                    #kinda works, not really
                    self.bot.pathfinder.setGoal(
                        mineflayer_pathfinder.pathfinder.goals.GoalNear(
                            player_location["x"], player_location["y"], player_location["z"], 1
                        )
                    )
                    sleep(1)

        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified):
            if messagePosition == "chat": 
                    if "bye" in message:
                        self.reconnect = False
                        this.quit()
                    elif "look here" in message:
                        local_players = self.bot.players
                        for el in local_players:
                            player_data = local_players[el]
                            if player_data["uuid"] == sender:
                                vec3_temp = local_players[el].entity.position
                                player_location = vec3(
                                    vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
                            )
                        if player_location:
                            self.bot.lookAt(player_location)
                    elif "follow me" in message or "stop" in message:
                        global follow_toggle
                        if follow_toggle == True:
                            follow_toggle = False
                        else:
                            follow_toggle = True
                        local_players = self.bot.players
                        for el in local_players:
                            player_data = local_players[el]
                            if player_data["uuid"] == sender:
                                global followed_player
                                followed_player = local_players[el]
                    elif "come here" in message:
                        local_players = self.bot.players
                        for el in local_players:
                            player_data = local_players[el]
                            if player_data["uuid"] == sender:
                                vec3_temp = local_players[el].entity.position
                                player_location = vec3(
                                    vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
                                )
                        if player_location:
                            self.pathfind_to_goal(player_location)
                    elif "whats there" in message:
                        block = self.bot.blockAtCursor()
                        if block:
                            self.bot.chat(f"Looking at {block.displayName}")
                        else:
                            self.bot.chat("Looking at air innit")
                    elif "msg" in message:
                        self.bot.chat(call_ai_chat(message.replace("msg", "")))

        @On(self.bot, "end")
        def end(this):
            self.log(chalk.red(f"Disconnected"))
            off(self.bot, "login", login)
            off(self.bot, "kicked", kicked)
            off(self.bot, "messagestr", messagestr)
            off(self.bot, "move", look_it)
            off(self.bot, "entityHurt", gotAttacked)
            if self.reconnect:
                print("Reconnecting")
                self.log(chalk.cyanBright(f"Attempting to reconnect"))
                self.start_bot()
            off(self.bot, "end", end)

if __name__ == "__main__":
    bot = MCBot("friend")