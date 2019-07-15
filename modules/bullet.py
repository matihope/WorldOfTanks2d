import pyglet
from pyglet.window import key, mouse
from modules import gamemaker_functions as gmf
import threading
import time


class Bullet(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super(Bullet, self).__init__(*args, **kwargs)
        self.spd = spd
        self.direction = direction
        self.player_id = player_id
        self.dmg = dmg
        self.hit = False

    def step(self):
        self.x += self.spd * self.dmg
        if gmf.
