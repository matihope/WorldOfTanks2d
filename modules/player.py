import pyglet
from pyglet.window import key
import threading
import time


class Player(pyglet.sprite.Sprite):
    def __init__(self, x, y, tank_type, player_id, game_mode, window_height, in_online_main_player=False, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.hsp = 0
        self.vsp = 0
        self.spd = 5
        self.player_id = player_id
        if self.player_id == 1:
            self.scale_x = -1
        self.game_mode = game_mode
        self.window_height = window_height
        self.dt = None
        self.in_online_main_player = in_online_main_player

        self.tank_type = tank_type
        self.remaining_reload = 0
        self.gun_is_reloaded = True
        self.ready_to_shot = False
        self.space_bar_unpressed = True

        if self.tank_type == 'HEAVY':
            self.hp_max = 3000
            self.dmg = 400
            self.bulletspeed = 20
            self.reload = 3

        elif self.tank_type == 'MEDIUM':
            self.hp_max = 2200
            self.dmg = 320
            self.bulletspeed = 15
            self.reload = 3
            self.spd = 6

        elif self.tank_type == 'LIGHT':
            self.hp_max = 1500
            self.dmg = 240
            self.bulletspeed = 20
            self.reload = 2
            self.spd = 8

        elif self.tank_type == 'DESTROYER':
            self.hp_max = 1800
            self.dmg = 1750
            self.bulletspeed = 25
            self.reload = 7

        self.hp = self.hp_max
        self.prev_hp = self.hp
        self.hit_dmg = self.hp

        x = round(self.x - 20 * self.scale_x)
        y = round(self.y + 70)
        self.vertex_list_hp_bar_bg = pyglet.graphics.vertex_list(4, ('v2i', [x - 55, y + 25, x + 55, y + 25, x + 55, y, x - 55, y]),
                                                                 ('c3B', (170, 70, 50, 170, 70, 50, 170, 70, 50, 170, 70, 50)))
        self.vertex_list_hp_bar_hit = pyglet.graphics.vertex_list(4, ('v2i', [x - 50, y + 23, x + 50, y + 23, x + 50, y + 3, x - 50, y + 3]),
                                                                  ('c3B', (255, 200, 15, 255, 200, 15, 255, 200, 15, 255, 200, 15)))
        self.vertex_list_hp_bar_hp = pyglet.graphics.vertex_list(4, ('v2i', [x - 50, y + 23, x + 50, y + 23, x + 50, y + 3, x - 50, y + 3]),
                                                                 ('c3B', (100, 200, 100, 100, 200, 100, 100, 200, 100, 100, 200, 100, )))

        color = (50, 255, 50, 255) if self.in_online_main_player else (255, 50, 50, 255)
        self.hp_lbl = pyglet.text.Label(text=f'{self.hp}/{self.hp_max}', anchor_x='center', anchor_y='center',
                                        font_name='Born2bSportyV2', font_size=16, color=color)
        self.hp_lbl.x = self.x - (20 * self.scale_x)

        self.hit_lbl = pyglet.text.Label(text='', anchor_x='center', anchor_y='center',
                                         font_name='Born2bSportyV2', font_size=16, color=(255, 200, 200, 255))
        self.hit_lbl.x = self.hp_lbl.x

        self.reload_lbl = pyglet.text.Label(text='', anchor_x='left', anchor_y='center',
                                            font_name='Born2bSportyV2', font_size=16, color=(255, 200, 200, 255))
        self.reload_lbl.x = self.x + (64 if self.scale_x == 1 else -92)

    def step(self, keys, dt):
        self.ready_to_shot = False
        self.dt = dt

        if len(keys) > 0:
            self.move(keys)

        # To allow just one press shot
        key_spacebar = False
        if self.space_bar_unpressed and keys[key.SPACE]:
            self.space_bar_unpressed = False
            key_spacebar = True
        elif not self.space_bar_unpressed and not keys[key.SPACE]:
            self.space_bar_unpressed = True

        key_shot = False
        if self.game_mode == 'OFFLINE':
            if (self.player_id == 0 and keys[key.D]) or \
               (self.player_id == 1 and keys[key.J]):
                key_shot = True
        else:
            if key_spacebar or keys[key.D]:
                key_shot = True

        if key_shot and self.gun_is_reloaded:
            self.gun_is_reloaded = False
            self.shot()
            self.remaining_reload = self.reload
            threading.Thread(target=self.reloading).start()

    def reloading(self):
        while self.remaining_reload > 0:
            self.remaining_reload -= self.dt
            time.sleep(self.dt)
        self.gun_is_reloaded = True

    def move(self, keys):
        gm = True if self.game_mode == 'OFFLINE' else False
        if self.player_id == 0:
            moveV = int(keys[key.W] or (keys[key.UP] if gm else False)) - int(keys[key.S] or (keys[key.DOWN] if gm else False))
        else:
            moveV = int(keys[key.I]) - int(keys[key.K])

        moveV *= self.spd * self.dt * 40
        # Clamping move area
        if self.y - self.image.anchor_y + moveV > 0 and \
           self.y + self.image.anchor_y + moveV < self.window_height:
            self.y += moveV

    def shot(self):
        self.ready_to_shot = True

    def update_labels(self):
        self.hp = max(self.hp, 0)

        # Dealing dmg
        if self.hp != self.prev_hp:
            dmg = self.prev_hp - self.hp
            self.prev_hp = self.hp
            self.hit_lbl.text = str(-dmg)

        self.hp_lbl.y = min(self.window_height-40, round(self.y) + 105)
        self.hp_lbl.text = f'{self.hp}/{self.hp_max}'

        self.hit_lbl.y = min(self.window_height-20, round(self.y) + 125)

        if self.in_online_main_player or self.game_mode == 'OFFLINE':
            self.reload_lbl.y = round(self.y) + 50
            if self.gun_is_reloaded:
                self.reload_lbl.text = 'R'
                self.reload_lbl.color = (50, 200, 50, 255)
            else:
                self.reload_lbl.text = str(round(self.remaining_reload * 100) / 100)
                c = round((150 * self.remaining_reload/self.reload))
                self.reload_lbl.color = (50 + c, 200 - c, 50, 255)

        # The bar area
        x = round(self.x - 20 * self.scale_x)
        y = min(round(self.y + 70), self.window_height - 75)
        self.vertex_list_hp_bar_bg.vertices = [x - 55, y + 25, x + 55, y + 25, x + 55, y, x - 55, y]

        hp_on_bar = int(100 * (self.hp / self.hp_max))
        self.vertex_list_hp_bar_hp.vertices = [x - 50, y + 23, x - 50 + hp_on_bar, y + 23, x - 50 + hp_on_bar, y + 3,
                                               x - 50, y + 3]

        if self.hit_dmg > self.hp:
            # Speed of smalling the hit_dmg bar
            self.hit_dmg = max(self.hp, self.hit_dmg-int(self.hp_max/500))

            dmg_on_bar = int(100 * (self.hit_dmg / self.hp_max))
            self.vertex_list_hp_bar_hit.vertices = [x - 50, y + 23, x - 50 + dmg_on_bar, y + 23,
                                                    x - 50 + dmg_on_bar, y + 3, x - 50, y + 3]
        else:
            self.hit_lbl.text = ''

    def draw(self):
        super(Player, self).draw()
        self.update_labels()
        self.hp_lbl.draw()
        self.hit_lbl.draw()
        if self.in_online_main_player or self.game_mode == 'OFFLINE':
            self.reload_lbl.draw()

        # Drawing bg
        self.vertex_list_hp_bar_bg.draw(pyglet.gl.GL_QUADS)
        # Drawing hit_dmg
        if self.hit_dmg > self.hp:
            self.vertex_list_hp_bar_hit.draw(pyglet.gl.GL_QUADS)
        # Drawing hp
        self.vertex_list_hp_bar_hp.draw(pyglet.gl.GL_QUADS)
