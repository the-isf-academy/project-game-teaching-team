# game.py
# Authors: Jacob Wolf
#
# This file should run your game.
#
# You can (and should) create other files and modules to import them
# here as needed.

from quest.examples.island import IslandAdventure
from quest.contrib.inventory import InventoryMixin, InventoryItemMixin
from quest.sprite import NPC
from quest.dialogue import Dialogue
from quest.modal import DialogueModal
from quest.helpers import resolve_resource_path
import random

BEGIN_PROB_NOTIF = .001
NOTIF_TYPES = ["FACEBOOK"]

class PhoneGame(InventoryMixin, IslandAdventure):
    """This game allows the player to play through the life of a character.
    """
    def __init__(self):
            super().__init__()
            self.dialogue = Dialogue.from_ink("phone.ink")
            self.modal = DialogueModal(self, self.dialogue)
            self.prob_notif = BEGIN_PROB_NOTIF
            self.notif_types = NOTIF_TYPES

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

    def on_update(self, delta_time):
        if self.running:
            if self.phone in self.inventory():
                if random.choices([True, False], weights=[self.prob_notif, 1-self.prob_notif])[0]:
                    notif_type = random.choice(self.notif_types)
                    self.dialogue.run(start_at=notif_type)
                    self.open_modal(self.modal)
        super().on_update(delta_time)

    def close_modal(self):
        super().close_modal()
        if len(self.dialogue.knots_visited) < 2:
            self.prob_notif -= 0.0001
        else:
            self.prob_notif += len(self.dialogue.knots_visited)*0.0001


class Phone(InventoryItemMixin, NPC):
    description = "phone"
    detailed_description = "your connection to the world?"

if __name__ == '__main__':
    game = PhoneGame()
    game.run()
