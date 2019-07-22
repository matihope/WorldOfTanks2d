from modules import player


class PlayerInit(object):
    def __init__(self, p):
        self.x = p.x
        self.y = p.y
        self.width = p.width
        self.height = p.height
        self.tank_type = p.tank_type
        self.player_id = p.player_id
        self.dmg = p.dmg
        self.bulletspeed = p.bulletspeed
        self.ready_to_shot = p.ready_to_shot
        self.gun_is_reloaded = p.gun_is_reloaded


class PlayerLite(object):
    def __init__(self, y, gun_is_reloaded):
        self.y = y
        self.gun_is_reloaded = gun_is_reloaded


def my_stripInit(player):
    new_p = PlayerInit(player)
    return new_p


def my_stripLite(player):
    new_p = PlayerLite(player.y, player.gun_is_reloaded)
    return new_p


def un_stripInit(p, self):
    self.player2 = player.Player(p.x, p.y, p.tank_type, p.player_id, 'ONLINE', self.height,
                                 img=self.tank_image, batch=self.main_batch)


def un_stripLite(player, self):
    self.player2.y = player.y
    self.player2.ready_to_shot = True if self.player2.gun_is_reloaded and not player.gun_is_reloaded else self.player2.ready_to_shot
    self.player2.gun_is_reloaded = player.gun_is_reloaded


def server_strip(p_old, p_new):
    p_old.y = p_new.y
    p_old.gun_is_reloaded = p_new.gun_is_reloaded
