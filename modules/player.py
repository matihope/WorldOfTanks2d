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

        self.game_mode = 'SINGLEPLAYER'
        self.in_online_main_player = in_online_main_player

        self.tank_type = tank_type
        self.remaining_reload = 0
        self.gun_is_reloaded = True
        self.ready_to_shot = False

        if self.tank_type == 'HEAVY':
            self.hp_max = 3000
            self.dmg = 400
            self.reload = 3
            self.bulletspeed = 15

        elif self.tank_type == 'DESTROYER':
            self.hp_max = 1800
            self.dmg = 1700
            self.reload = 5
            self.bulletspeed = 25

        self.hp = self.hp_max
        self.prev_hp = self.hp
        self.hp_count_down_factor = self.hp//100

        color = (50, 255, 50, 255) if self.in_online_main_player else (255, 50, 50, 255)
        self.hp_lbl = pyglet.text.Label(text=f'{self.hp}/{self.hp_max}', anchor_x='center', anchor_y='center',
                                        font_name='Born2bSportyV2', font_size=16, color=color)
        self.hp_lbl.x = self.x - (20 * self.scale_x)

    def step(self, keys, dt):
        self.ready_to_shot = False
        self.dt = dt

        if len(keys) > 0:
            self.move(keys)

        key_shot = False
        if self.game_mode == 'OFFLINE':
            if (self.player_id == 0 and (keys[key.SPACE] or keys[key.D])) or \
               (self.player_id == 1 and keys[key.J]):
                key_shot = True
        else:
            if keys[key.SPACE] or keys[key.D]:
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
        print('Reloaded!')

    def move(self, keys):
        if self.player_id == 0 or self.game_mode == 'ONLINE':
            moveV = int(keys[key.W] or keys[key.UP]) - int(keys[key.S] or keys[key.DOWN])
        else:
            moveV = int(keys[key.W]) - int(keys[key.S])

        moveV *= self.spd * self.dt * 40

        # Clamping move area
        if self.y - self.image.anchor_y + moveV > 0 and \
           self.y + self.image.anchor_y + moveV < self.window_height:
            self.y += moveV

    def shot(self):
        print('Shot!')
        self.ready_to_shot = True

    def update_labels(self):
        self.hp_lbl.y = min(self.window_height-20, round(self.y) + 85)
        self.hp_lbl.text = f'{self.hp}/{self.hp_max}'

    def draw(self):
        super(Player, self).draw()
        self.update_labels()
        self.hp_lbl.draw()
