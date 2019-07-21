from modules import player, bullet


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
        self.gun_is_reloaded = p.ready_to_shot


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
    if player.ready_to_shot:
        self.bullet_list.append(bullet.Bullet(self.player2,
                                              img=self.bullet_image, batch=self.main_batch))  # Other player's bullet
        print('Made a enemy\'s bullet!')


def server_strip(p_old, p_new):
    p_old.y = p_new.y
    p_old.ready_to_shot = True if not p_new.gun_is_reloaded and p_old.gun_is_reloaded else p_old.ready_to_shot
    p_old.gun_is_reloaded = p_new.gun_is_reloaded
