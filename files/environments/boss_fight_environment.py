from serpent.environment import Environment
from serpent.utilities import SerpentError

from .common import Bosses, DoubleBosses, MiniBosses, Items

import random
import collections

import numpy as np


class BossFightEnvironment(Environment):

    def __init__(self, game_api=None, input_controller=None, bosses=None, items=None):
        super().__init__("Boss Fight Environment", game_api=game_api, input_controller=input_controller)

        if not isinstance(bosses, list):
            raise SerpentError("'bosses' is expected to be a list of Bosses|DoubleBosses|MiniBosses enum items...")

        filtered_bosses = list()

        for boss in bosses:
            if isinstance(boss, Bosses) or isinstance(boss, DoubleBosses) or isinstance(boss, MiniBosses):
                filtered_bosses.append(boss)

        if not len(filtered_bosses):
            raise SerpentError("'bosses' needs to contain at least 1 valid Bosses|DoubleBosses|MiniBosses enum item...")

        self.bosses = filtered_bosses
        self.boss = None

        if items is None:
            items = list()

        filtered_items = list()

        for item in items:
            if isinstance(item, Items):
                filtered_items.append(item)

        self.items = filtered_items

        self.reset()

    @property
    def new_episode_data(self):
        return {
            "boss": str(self.boss),
            "starting_boss_hp": self.game_api.boss_hp,
        }

    @property
    def end_episode_data(self):
        return {
            "boss": str(self.boss),
            "starting_boss_hp": self.game_api.boss_hp,
            "final_boss_hp": self.game_state["boss_hps"][0]
        }

    def new_episode(self, maximum_steps=None, reset=False):
        self.reset_game_state()

        self.boss = random.choice(self.bosses)
        self.game_api.start_boss_fight(boss=self.boss, items=self.items, input_controller=self.input_controller)

        super().new_episode(maximum_steps=maximum_steps, reset=reset)

    def reset(self):
        self.reset_game_state()
        super().reset()

    def reset_game_state(self):
        self.game_state = {
            "isaac_hp": 1,
            "isaac_hps": collections.deque(np.full((100,), 6), maxlen=100),
            "isaac_alive": True,
            "boss_hp_total": self.game_api.boss_hp,
            "boss_hp": self.game_api.boss_hp,
            "boss_hps": collections.deque(np.full((100,), self.game_api.boss_hp), maxlen=100),
            "boss_dead": False,
            "damage_taken": False,
            "damage_dealt": False,
            "steps_since_damage_taken": 0,
            "steps_since_damage_dealt": 100,
        }

    def update_game_state(self, game_frame):
        isaac_hp = self.game_api.get_isaac_hp(game_frame)

        # We skip Curse of the Unknown because we rely on HP values
        if isaac_hp == -1:
            self.new_episode(reset=True)
            return False

        self.game_state["damage_taken"] = isaac_hp < self.game_state["isaac_hp"]

        if self.game_state["damage_taken"]:
            self.game_state["steps_since_damage_taken"] = 0
        else:
            self.game_state["steps_since_damage_taken"] += 1

        self.game_state["isaac_hp"] = isaac_hp
        self.game_state["isaac_hps"].appendleft(isaac_hp)

        last_isaac_hps = self.game_state["isaac_hps"][0] + self.game_state["isaac_hps"][1]
        self.game_state["isaac_alive"] = last_isaac_hps > 0

        boss_hp = self.game_api.get_boss_hp(game_frame)

        self.game_state["damage_dealt"] = boss_hp < self.game_state["boss_hp"]

        if self.game_state["damage_dealt"]:
            self.game_state["steps_since_damage_dealt"] = 0
        else:
            self.game_state["steps_since_damage_dealt"] += 1

        if boss_hp == 0:
            if self.game_api.is_boss_dead(game_frame):
                self.game_state["boss_dead"] = True
            else:
                boss_hp = self.game_state["boss_hp"]

        self.game_state["boss_hp"] = boss_hp
        self.game_state["boss_hps"].appendleft(boss_hp)

        return True
