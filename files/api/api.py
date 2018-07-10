from serpent.game_api import GameAPI

from serpent.input_controller import KeyboardEvent, KeyboardEvents, KeyboardKey

from ..environments.common import Bosses, DoubleBosses, MiniBosses

import serpent.cv

import numpy as np
import skimage.measure

import pyperclip

import time


class AIsaacAPI(GameAPI):

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {
            "MOVEMENT": {
                "MOVE UP": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W)
                ],
                "MOVE LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE DOWN": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S)
                ],
                "MOVE RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "MOVE TOP-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE TOP-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "MOVE DOWN-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE DOWN-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "DON'T MOVE": []
            },
            "SHOOTING": {
                "SHOOT UP": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP)
                ],
                "SHOOT LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)
                ],
                "SHOOT DOWN": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN)
                ],
                "SHOOT RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)
                ],
                "DON'T SHOOT": []
            }
        }

    @property
    def boss_hp(self):
        return 654

    @property
    def heart_colors(self):
        return {
            "lefts": {
                (236, 0, 4): "RED",
                (255, 0, 4): "RED",
                (97, 117, 163): "SOUL",
                (63, 63, 63): "BLACK",
            },
            "rights": {
                (236, 0, 4): "RED",
                (72, 87, 121): "SOUL",
                (48, 48, 48): "BLACK",
                (255, 255, 255): "ETERNAL"
            }
        }

    def start_boss_fight(self, boss=None, items=None, input_controller=None):
        input_controller.tap_key(KeyboardKey.KEY_R, duration=1.5)
        time.sleep(1)

        input_controller.tap_key(KeyboardKey.KEY_GRAVE)
        time.sleep(0.5)

        for item in items:
            pyperclip.copy(f"giveitem c{item.value}")
            input_controller.tap_keys([KeyboardKey.KEY_LEFT_CTRL, KeyboardKey.KEY_V], duration=0.1)
            time.sleep(0.1)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.1)

        if (isinstance(boss, Bosses) or isinstance(boss, DoubleBosses)) and boss.value != 0:
            input_controller.type_string("goto s.bos")
            input_controller.type_string(f"s.{boss.value}")
            time.sleep(0.1)

            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.1)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.5)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.5)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.2)
        elif isinstance(boss, Bosses) and boss.value == 0:
            pyperclip.copy("stage 9")
            input_controller.tap_keys([KeyboardKey.KEY_LEFT_CTRL, KeyboardKey.KEY_V], duration=0.1)
            time.sleep(0.1)

            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.1)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.5)

            input_controller.tap_key(KeyboardKey.KEY_W, duration=4)
            time.sleep(0.1)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.2)
        elif isinstance(boss, MiniBosses):
            pyperclip.copy(f"goto s.miniboss.{boss.value}")
            input_controller.tap_keys([KeyboardKey.KEY_LEFT_CTRL, KeyboardKey.KEY_V], duration=0.1)
            time.sleep(0.1)

            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.1)
            input_controller.tap_key(KeyboardKey.KEY_ENTER)
            time.sleep(0.5)

    def get_isaac_hp(self, game_frame):
        hearts = self.get_isaac_hearts(game_frame)

        # Curse of the Unknown
        if not len(hearts):
            return -1

        return 24 - hearts.count(None)

    def get_isaac_hearts(self, game_frame):
        heart_positions = range(1, 13)
        heart_labels = [f"HUD_HEART_{position}" for position in heart_positions]

        hearts = list()

        for heart_label in heart_labels:
            heart = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions[heart_label])

            left_heart_pixel = tuple(heart[3, 5, :])
            right_heart_pixel = tuple(heart[3, 17, :])
            unknown_heart_pixel = tuple(heart[9, 11, :])

            if unknown_heart_pixel == (230, 230, 230):
                return hearts

            heart_colors = self.heart_colors

            hearts.append(heart_colors["lefts"].get(left_heart_pixel))
            hearts.append(heart_colors["rights"].get(right_heart_pixel))

        return hearts

    def get_boss_hp(self, game_frame):
        boss_hp_bar = serpent.cv.extract_region_from_image(
            game_frame.frame,
            self.game.screen_regions["HUD_BOSS_HP"]
        )

        return np.count_nonzero(boss_hp_bar[:, :, 0] > 128)

    def is_boss_dead(self, game_frame):
        boss_skull = serpent.cv.extract_region_from_image(
            game_frame.frame,
            self.game.screen_regions["HUD_BOSS_SKULL"]
        )

        reference_boss_skull = np.squeeze(self.game.sprites["SPRITE_BOSS_SKULL"].image_data)

        ssim_score = skimage.measure.compare_ssim(
            boss_skull,
            reference_boss_skull,
            multichannel=True
        )

        return ssim_score < 0.5
