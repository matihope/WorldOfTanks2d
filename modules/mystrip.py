from modules import player


class PlayerInit(object):
    def __init__(self, x, y, width, height, tank_type, player_id, shot, gun_is_reloaded):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tank_type = tank_type
        self.player_id = player_id
        self.ready_to_shot = shot
        self.gun_is_reloaded = gun_is_reloaded


class PlayerLite(object):
    def __init__(self, y, gun_is_reloaded):
        self.y = y
        self.gun_is_reloaded = gun_is_reloaded


def my_stripInit(player):
    new_p = PlayerInit(player.x, player.y, player.width, player.height, player.tank_type,
                       player.player_id, player.ready_to_shot, player.gun_is_reloaded)
    return new_p


def my_stripLite(player):
    new_p = PlayerLite(player.y, player.gun_is_reloaded)
    return new_p


def un_stripInit(p, self):
    self.player2 = player.Player(p.x, p.y, p.tank_type, p.player_id, 'ONLINE', self.height,
                                 img=self.tank_image, batch=self.main_batch)


def un_stripLite(player, self):
    self.player2.y = player.y
    self.player2.ready_to_shot = player.ready_to_shot


def server_strip(p_old, p_new):
    p_old.y = p_new.y
    p_old.ready_to_shot = True if not p_new.gun_is_reloaded and p_old.gun_is_reloaded else False
    p_old.gun_is_reloaded = p_new.gun_is_reloaded
