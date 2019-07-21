import pyglet
from modules import gamemaker_functions as gmf


class Bullet(pyglet.sprite.Sprite):
    def __init__(self, player, *args, **kwargs):
        super(Bullet, self).__init__(*args, **kwargs)
        self.x = player.x
        self.y = player.y
        self.player_id = player.player_id
        self.spd = player.bulletspeed
        self.dmg = player.dmg
        self.hit = False
        if self.player_id == 1:
            self.scale_x = -1

        factor = 1 if self.player_id == 0 else -1
        self.x += 100 * factor
        self.y += 28
        self.spd *= factor

    def step(self, fixDt, p):
        self.x += self.spd * fixDt
        if gmf.objects_are_colliding(self, p):
            self.hit = True
            self.visible = False
            print('Hit!')
