import pyglet
from pyglet.window import key, mouse
from modules import player, button, network, bullet
from pyglet.gl import *
import threading
import time


pyglet.resource.path = ["resources"]
pyglet.resource.reindex()


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__(*args, **kwargs)

        # Set key handler.
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.current_screen = 0  # 0=Menu, 1=Game 2=Stats
        self.ip = '192.168.0.11'
        self.port = 5555
        self.n = None
        self.this_client_id = 0

        self.game_mode = 'OFFLINE'
        self.tank_type_list = ['HEAVY', 'MEDIUM', 'LIGHT', 'DESTROYER']
        self.p1_tank_type = 'HEAVY'
        self.p2_tank_type = 'HEAVY'

        self.dt = 1
        self.fixDt = 0
        self.FPS = 0
        self.desired_FPS = 60

        self.menu_batch = pyglet.graphics.Batch()
        self.main_batch = pyglet.graphics.Batch()
        self.add_ons_1 = pyglet.graphics.Batch()
        self.stats_batch = pyglet.graphics.Batch()

        self.mouse_left_is_pressed = False
        self.mouse_x, self.mouse_y = 0, 0

        self.FPS_label = pyglet.text.Label(text=':)', anchor_x='left', anchor_y='top', batch=self.add_ons_1,
                                           font_name='Born2bSportyV2', font_size=16, color=(255, 211, 0, 255))
        self.FPS_label.x, self.FPS_label.y = 0, self.height

        self.text_for_message_label = ''
        self.message_label = pyglet.text.Label(text=self.text_for_message_label, anchor_x='center', anchor_y='center',
                                               font_name='Born2bSportyV2', font_size=72, color=(255, 50, 50, 255))
        self.message_label.x, self.message_label.y = self.width/2, self.height/2

        self.tank_image = pyglet.resource.image('tank.png')
        center_image(self.tank_image)

        self.bullet_image = pyglet.resource.image('bullet.png')
        center_image(self.bullet_image)
        
        # CREATING PLAYERS IN BUTTON HANDLING
        self.player1 = None
        self.player2 = None
        self.end_the_game = False
        self.drawn_end_screen = False

        self.bullet_list = []

        self.buttons = {
            'set_ip': button.Button('button.png', self.ip if self.ip is not None else 'Set IP', x=self.width/2, y=500),
            'gamemode': button.Button('button.png', self.game_mode, x=self.width/2, y=400),
            'p1_tank_type': button.Button('button.png', f'P1:{self.p1_tank_type}', x=self.width/2-200, y=250),
            'p2_tank_type': button.Button('button.png', f'P2:{self.p2_tank_type}', x=self.width/2+200, y=250),
            'play': button.Button('button.png', 'PLAY!', x=self.width/2, y=100),
            'stats': button.Button('button.png', 'Tank stats', x=150, y=50)
        }
        self.back_from_stats_button = button.Button('button.png', 'Back to menu', x=150, y=50)
        self.buttons['set_ip'].active = False
        self.buttons['set_ip'].visible = False

        self.logo_lbl_bg = pyglet.text.Label(text='World Of Tanks 2D', anchor_x='center', anchor_y='center',
                                             font_name='Born2bSportyV2', font_size=96, color=(5, 5, 5, 255),
                                             x=self.width / 2 + 2, y=650 - 2, batch=self.stats_batch)
        self.logo_lbl = pyglet.text.Label(text='World Of Tanks 2D', anchor_x='center', anchor_y='center',
                                          font_name='Born2bSportyV2', font_size=96, color=(109, 176, 176, 255),
                                          x=self.width / 2, y=650, batch=self.stats_batch)

        self.heavy_stats_lbl = pyglet.text.Label(anchor_x='center', anchor_y='center', font_name='Born2bSportyV2',
                                                 multiline=True, width=230, font_size=24,
                                                 color=(191, 191, 61, 255), batch=self.stats_batch)
        self.heavy_stats_lbl.x, self.heavy_stats_lbl.y = self.width * 1/5, self.height / 2
        self.medium_stats_lbl = pyglet.text.Label(anchor_x='center', anchor_y='center', font_name='Born2bSportyV2',
                                                  multiline=True, width=230, font_size=24,
                                                  color=(63, 191, 191, 255), batch=self.stats_batch)
        self.medium_stats_lbl.x, self.medium_stats_lbl.y = self.width * 2/5, self.height / 2
        self.light_stats_lbl = pyglet.text.Label(anchor_x='center', anchor_y='center', font_name='Born2bSportyV2',
                                                 multiline=True, width=230, font_size=24,
                                                 color=(63, 191, 63, 255), batch=self.stats_batch)
        self.light_stats_lbl.x, self.light_stats_lbl.y = self.width * 3/5, self.height / 2
        self.destroyer_stats_lbl = pyglet.text.Label(anchor_x='center', anchor_y='center', font_name='Born2bSportyV2',
                                                     multiline=True, width=230, font_size=24,
                                                     color=(200, 100, 100, 255), batch=self.stats_batch)
        self.destroyer_stats_lbl.x, self.destroyer_stats_lbl.y = self.width * 4/5, self.height / 2

        self.heavy_stats_lbl.text = 'HEAVY:              ' \
                                    'Hp - 3000           ' \
                                    'Dmg - 400           ' \
                                    'Bulletspeed - 20    ' \
                                    'Reload - 3          ' \
                                    'Spd - 5'

        self.medium_stats_lbl.text = 'MEDIUM:             ' \
                                     'Hp - 2200           ' \
                                     'Dmg - 320           ' \
                                     'Bulletspeed - 15    ' \
                                     'Reload - 3          ' \
                                     'Spd - 6'

        self.light_stats_lbl.text = 'LIGHT:              ' \
                                    'Hp - 1500           ' \
                                    'Dmg - 240           ' \
                                    'Bulletspeed - 20    ' \
                                    'Reload - 3          ' \
                                    'Spd - 8'
        self.destroyer_stats_lbl.text = 'DESTROYER:          ' \
                                        'Hp - 1800           ' \
                                        'Dmg - 1750          ' \
                                        'Bulletspeed - 25    ' \
                                        'Reload - 7          ' \
                                        'Spd - 5'

        threading.Thread(target=self.FPS_COUNTER).start()
        pyglet.clock.schedule_interval(self.game_tick, 1/250)

    def game_tick(self, dt):
        self.dt = dt
        self.fixDt = self.desired_FPS * dt
        self.FPS_label.text = str(self.FPS)

        # Menu
        if self.current_screen == 0:
            [b.refresh(self.mouse_x, self.mouse_y, self.mouse_left_is_pressed) for b in self.buttons.values()]
            self.back_from_stats_button.refresh(self.mouse_x, self.mouse_y, self.mouse_left_is_pressed)
        # Game
        elif self.current_screen == 1:
            if self.game_mode == 'OFFLINE':
                self.player1.step(self.keys, dt)
                self.player2.step(self.keys, dt)

                # Player1 shot is outside this if statement, because it works the same for both ONLINE and OFFLINE
                # Player2 shot
                if self.player2.ready_to_shot:
                    self.bullet_list.append(bullet.Bullet(self.player2, img=self.bullet_image, batch=self.main_batch))

                for b in self.bullet_list:
                    if b.hit:
                        if b.player_id == 0:
                            self.player2.hp -= b.dmg
                        else:
                            self.player1.hp -= b.dmg
                        self.bullet_list.remove(b)

                if self.player1.hp <= 0 or self.player2.hp <= 0:
                    winner = 'P2 WON!' if self.player1.hp <= 0 else 'P1 WON!'
                    self.text_for_message_label = winner
                    self.display_message(winner, 3)
                    self.end_the_game = True
            else:
                self.player1.step(self.keys, dt)

                for b in self.bullet_list:
                    if b.hit:
                        if b.player_id != self.player1.player_id:
                            self.player1.hp -= b.dmg
                        self.bullet_list.remove(b)

                if self.player2.ready_to_shot:
                    self.make_enemy_bullet()

            # Refreshing bullets
            for b in self.bullet_list:
                b.step(self.fixDt, self.player1 if b.player_id == self.player2.player_id else self.player2)
                if not (0 < b.x < self.width):
                    self.bullet_list.remove(b)

            # Player1 shot
            if self.player1.ready_to_shot:
                self.bullet_list.append(bullet.Bullet(self.player1, img=self.bullet_image, batch=self.main_batch))

            # 180 100

        # Stats
        elif self.current_screen == 2:
            self.back_from_stats_button.refresh(self.mouse_x, self.mouse_y, self.mouse_left_is_pressed)

        self.draw_elements()
        if self.end_the_game:
            self.end_the_game = False
            self.player1 = None
            self.player2 = None
            self.bullet_list = []
            self.current_screen = 0

    def draw_elements(self):
        self.clear()
        glClearColor(46 / 255, 46 / 255, 49 / 255, 0.2)  # Bg Color

        # To draw
        # Menu
        if self.current_screen == 0:
            [b.draw() for b in self.buttons.values()]
            self.handle_buttons()
            self.logo_lbl_bg.draw()
            self.logo_lbl.draw()

        # Game
        elif self.current_screen == 1:
            try:
                self.player1.draw()
                self.player2.draw()
            except AttributeError:
                pass
            self.main_batch.draw()
            self.add_ons_1.draw()

        elif self.current_screen == 2:
            self.back_from_stats_button.draw()
            self.handle_buttons()
            self.stats_batch.draw()

        self.message_label.text = self.text_for_message_label
        self.message_label.draw()

        if self.drawn_end_screen:
            self.drawn_end_screen = False
            time.sleep(3)
        if self.end_the_game:
            self.drawn_end_screen = True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.mouse_left_is_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.mouse_left_is_pressed = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = x, y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_press(x, y, buttons, modifiers)
        self.on_mouse_motion(x, y, dx, dy)

    def FPS_COUNTER(self):
        # Make a list to make an avg of fps
        FPS_ = []
        for frame in range(3):
            FPS_.append(self.dt)

        while not self.has_exit:
            FPS_.remove(FPS_[0])
            FPS_.append(1/self.dt)
            self.FPS = round(float(sum(FPS_)) / max(len(FPS_), 1))  # Average of FPS
            time.sleep(1)

    def handle_buttons(self):
        if self.buttons['p1_tank_type'].click:
            self.p1_tank_type = switch(self.p1_tank_type, self.tank_type_list)
            self.buttons['p1_tank_type'].txt_label.text = f'P1:{self.p1_tank_type}'

        elif self.buttons['p2_tank_type'].click:
            self.p2_tank_type = switch(self.p2_tank_type, self.tank_type_list)
            self.buttons['p2_tank_type'].txt_label.text = f'P2:{self.p2_tank_type}'

        elif self.buttons['set_ip'].click:
            self.ip = input('Give me new ip:')
            self.buttons['set_ip'].txt_label.text = f'IP:{self.ip}'

        elif self.buttons['gamemode'].click:
            self.game_mode = 'OFFLINE' if self.game_mode == 'ONLINE' else 'ONLINE'
            self.buttons['gamemode'].txt_label.text = self.game_mode
            self.buttons['set_ip'].active = not self.buttons['set_ip'].active
            self.buttons['set_ip'].visible = not self.buttons['set_ip'].visible
            if self.game_mode == 'ONLINE':
                self.buttons['p1_tank_type'].x = self.width/2
                self.buttons['p2_tank_type'].active = False
                self.buttons['p2_tank_type'].visible = False
            else:
                self.buttons['p1_tank_type'].x = self.width/2-200
                self.buttons['p2_tank_type'].active = True
                self.buttons['p2_tank_type'].visible = True

        elif self.buttons['play'].click:
            if self.game_mode == 'OFFLINE':
                self.player1 = player.Player(self.tank_image.anchor_x, self.height-self.tank_image.anchor_y,
                                             self.p1_tank_type, 0, self.game_mode, self.height, img=self.tank_image)
                self.player2 = player.Player(self.width-self.tank_image.anchor_x, self.tank_image.anchor_y,
                                             self.p2_tank_type, 1, self.game_mode, self.height, img=self.tank_image)
                self.current_screen = 1
            else:
                if self.ip is not None:
                    # Connecting with server
                    self.n = network.Network(self.ip)
                    self.this_client_id = int(self.n.getId())
                    print(self.this_client_id)

                    if self.this_client_id == 0:
                        self.player1 = player.Player(self.tank_image.anchor_x, self.height-self.tank_image.anchor_y,
                                                     self.p1_tank_type, 0, self.game_mode, self.height,
                                                     in_online_main_player=True, img=self.tank_image)
                    else:
                        self.player1 = player.Player(self.width-self.tank_image.anchor_x, self.tank_image.anchor_y,
                                                     self.p1_tank_type, 1, self.game_mode, self.height,
                                                     in_online_main_player=True, img=self.tank_image)
                    
                    self.n.send_player(self.player1)
                    self.n.p2(self)

                    self.current_screen = 1
                    threading.Thread(target=self.trade_info).start()

                else:
                    self.display_message('Set your ip first!', 3)

        elif self.buttons['stats'].click:
            self.current_screen = 2

        elif self.back_from_stats_button.click:
            self.current_screen = 0

        for btn in self.buttons.values():
            if btn.long_press:
                continue
            btn.click = False

    def display_message(self, message, t):
        threading.Thread(target=self.threaded_msg, args=(message, t, )).start()

    def threaded_msg(self, message, t):
        self.text_for_message_label = message
        for s in range(t):
            time.sleep(1)
        self.text_for_message_label = ''

    def trade_info(self):
        end = False
        while not end and not self.has_exit:
            try:
                self.n.trade(self.player1, self)
                if self.player1.hp <= 0 or self.player2.hp <= 0:
                    winner = 'ENEMY WON :(' if self.player1.hp <= 0 else 'YOU WON!'
                    self.text_for_message_label = winner
                    self.display_message(winner, 3)
                    end = True
            except AttributeError:
                break
        self.n.trade(self.player1, self)
        time.sleep(1/130)
        self.n = None
        self.end_the_game = True

    def make_enemy_bullet(self):
        self.bullet_list.append(bullet.Bullet(self.player2, img=self.bullet_image, batch=self.main_batch))
        self.player2.ready_to_shot = False


def switch(to_switch, opt_list):
    curr = opt_list.index(to_switch)
    if curr == len(opt_list)-1:
        new_value = opt_list[0]
    else:
        new_value = opt_list[curr+1]
    return new_value


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


if __name__ == '__main__':
    window = GameWindow(1300, 800, resizable=False, vsync=True, caption='WorldOfTanks2d')
    pyglet.app.run()
