import pyglet
import sys
from modules import player


class PlayerInit(object):
    def __init__(self, x, y, tank_type, player_id, shot):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tank_type = tank_type
        self.player_id = player_id
        self.ready_to_shot = shot


class PlayerLite(object):
    def __init__(self, y, shot):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player_id = player_id
        self.ready_to_shot = shot


def my_stripInit(player):
    new_p = PlayerInit(player.x, player.y, player.tank_type, player.player_id, player.ready_to_shot)
    return new_p


def my_stripLite(player):
    new_p = PlayerLite(player.y, player.ready_to_shot)
    return new_p


def un_stripInit(p, self):
    self.player2 = player.Player(p.x, p.y, p.tank_type, p.player_id, self.height, img=self.tank_image, batch=self.main_batch)


def un_stripLite(player, self):
    self.player2.y = player.y
    self.player2.ready_to_shot = player.ready_to_shot
