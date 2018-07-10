from serpent.game import Game

from .api.api import AIsaacAPI

from .environments.boss_fight_environment import BossFightEnvironment, Bosses, DoubleBosses, MiniBosses, Items

from serpent.utilities import Singleton

import time


class SerpentAIsaacGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"

        kwargs["window_name"] = "Binding of Isaac: Afterbirth+"

        kwargs["app_id"] = "250900"
        kwargs["app_args"] = None

        super().__init__(**kwargs)

        self.api_class = AIsaacAPI

        self.environments = {
            "BOSS_FIGHT": BossFightEnvironment
        }

        self.environment_data = {
            "BOSSES": Bosses,
            "DOUBLE_BOSSES": DoubleBosses,
            "MINI_BOSSES": MiniBosses,
            "ITEMS": Items
        }

        self.frame_transformation_pipeline_string = "RESIZE:100x100|GRAYSCALE|FLOAT"

    @property
    def screen_regions(self):
        regions = dict(
            HUD_HEART_1=(12, 84, 32, 106),
            HUD_HEART_2=(12, 108, 32, 130),
            HUD_HEART_3=(12, 132, 32, 154),
            HUD_HEART_4=(12, 156, 32, 178),
            HUD_HEART_5=(12, 180, 32, 202),
            HUD_HEART_6=(12, 204, 32, 226),
            HUD_HEART_7=(32, 84, 52, 106),
            HUD_HEART_8=(32, 108, 52, 130),
            HUD_HEART_9=(32, 132, 52, 154),
            HUD_HEART_10=(32, 156, 52, 178),
            HUD_HEART_11=(32, 180, 52, 202),
            HUD_HEART_12=(32, 204, 52, 226),
            HUD_BOSS_HP=(519, 371, 522, 592),
            HUD_BOSS_SKULL=(496, 340, 529, 373)
        )

        return regions
