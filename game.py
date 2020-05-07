# game.py
# Authors: Jacob Wolf
#
# This file should run your game.
#
# You can (and should) create other files and modules to import them
# here as needed.

from quest.examples.island_time import IslandAdventure
from quest.contrib.inventory import InventoryMixin, InventoryItemMixin
from quest.contrib.timer import TimerMixin
from quest.sprite import NPC
from quest.dialogue import Dialogue
from quest.modal import DialogueModal
from quest.engines import ContinuousPhysicsEngine
from quest.text_label import TextLabel
from quest.helpers import resolve_resource_path
import arcade
import random
import datetime

BEGIN_PROB_NOTIF = .001
NOTIF_TYPES = ["FACEBOOK", "MESSENGER", "COSTAR", "COSTARONE", "COSTARTWO"]
GAME_LENGTH = 2

            

class PhoneGame(InventoryMixin, IslandAdventure):
    """This game allows the player to play through the life of a character.
    """
    screen_width = 600
    screen_height = 600
    max_darkness = 100
    time_cycle_secs = 60
    display_time = True
    
    def __init__(self):
            super().__init__()
            self.dialogue = Dialogue.from_ink("phone.ink")
            self.modal = DialogueModal(self, self.dialogue)
            self.prob_notif = BEGIN_PROB_NOTIF
            self.notif_types = NOTIF_TYPES
            self.total_notifs = 0
            self.notifs_interacted = 0
            self.game_over = False

    def setup_npcs(self):
            """Creates and places Grandma and the vegetables.
            """
            super().setup_npcs()
            npc_data = [
                [Phone, "images/phone.png", .05, 400, 400],
            ]
            for sprite_class, image, scale, x, y in npc_data:
                sprite = sprite_class(image, scale)
                sprite.center_x = x
                sprite.center_y = y
                self.npc_list.append(sprite)
                self.phone = sprite

    def setup_physics_engine(self):
        """Passes optional `time` parameter to the standard :py:class:`ContinuousPhysicsEngine`.
        The result is that the sprites in the game change their appearance as time progresses in
        the game.
        """
        self.physics_engine = TimedContinuousPhysicsEngine(self)

    def on_update(self, delta_time):
        if self.physics_engine.time_since_start() > GAME_LENGTH:
            self.game_over = True
            self.running = False
        if self.running:
            if self.phone in self.inventory():
                if random.choices([True, False], weights=[self.prob_notif, 1-self.prob_notif])[0]:
                    self.total_notifs += 1
                    notif_type = random.choice(self.notif_types)
                    self.dialogue.run(start_at=notif_type)
                    self.open_modal(self.modal)
        super().on_update(delta_time)

    def draw_game_over(self):
        """
        Draw "Game over" across the screen.

        Code from Python Arcade library documentation:
        https://arcade.academy/examples/instruction_and_game_over_screens.html
        """
        output = "Game Over"
        arcade.draw_text(output, self.view_left + self.screen_width/2, self.view_bottom + self.screen_height/1.5,
            arcade.color.WHITE, 54, align="center", anchor_x="center", anchor_y="center")

        output = "You recieved {} notifications.".format(self.total_notifs)
        arcade.draw_text(output, self.view_left + self.screen_width/2, self.view_bottom + self.screen_height/2.5,
            arcade.color.WHITE, 24, align="center", anchor_x="center", anchor_y="center")
        output = "You responded to {} of them.".format(self.notifs_interacted)
        arcade.draw_text(output, self.view_left + self.screen_width/2, self.view_bottom + self.screen_height/2.9,
            arcade.color.WHITE, 24, align="center", anchor_x="center", anchor_y="center")

    def on_draw(self):
        super().on_draw()
        if self.game_over:
            self.draw_game_over()

    def close_modal(self):
        super().close_modal()
        if len(self.dialogue.knots_visited) < 2:
            self.prob_notif -= 0.001
        else:
            self.notifs_interacted += 1
            self.prob_notif += len(self.dialogue.knots_visited)*0.001

    def message(self):
        """ Displays the time in the game relative to the time cycle
        """
        if self.display_time:
            time = str(datetime.timedelta(seconds = (GAME_LENGTH - self.physics_engine.time_since_start())))
            return time.split(".")[0] 
        
class TimedContinuousPhysicsEngine(ContinuousPhysicsEngine, TimerMixin):
    """ Physics engine that also makes time-based updates
    """
    def __init__(self, game):
        self.init_timer()
        super().__init__(game)

    def update(self):
        """Calculates shade by converting the time passed since the start of the game to a percentage
        of the current day/night cycle.
        """
        super().update()
        time_since_start = self.time_since_start() 
        curr_mod = time_since_start%self.game.time_cycle_secs
        grade = abs(curr_mod - self.game.time_cycle_secs/2) / (self.game.time_cycle_secs/2)
        color_value = grade*(255-self.game.max_darkness) + self.game.max_darkness
        for sprite in self.all_sprites:
            sprite.color = (color_value, color_value, color_value)


class Phone(InventoryItemMixin, NPC):
    description = "phone"
    detailed_description = "your connection to the world?"

if __name__ == '__main__':
    game = PhoneGame()
    game.run()
