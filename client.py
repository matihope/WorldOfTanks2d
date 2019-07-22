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

        self.current_screen = 0  # 0=Menu, 1=Game
        self.ip = '192.168.0.11'
        self.port = 5555
        self.n = None
        self.this_client_id = 0

        self.game_mode = 'OFFLINE'
        self.p1_tank_type = 'HEAVY'
        self.p2_tank_type = 'HEAVY'

        self.dt = 1
        self.fixDt = 0
        self.FPS = 0
        self.desired_FPS = 60

        self.menu_batch = pyglet.graphics.Batch()
        self.main_batch = pyglet.graphics.Batch()
        self.add_ons_1 = pyglet.graphics.Batch()

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
        self.p2_ready_to_shot = False

        self.bullet_list = []

        self.buttons = {
            'set_ip': button.Button('button.png', self.ip if self.ip is not None else 'Set IP', x=self.width/2, y=500),
            'gamemode': button.Button('button.png', self.game_mode, x=self.width/2, y=400),
            'p1_tank_type': button.Button('button.png', f'P1:{self.p1_tank_type}', x=self.width/2-200, y=250),
            'p2_tank_type': button.Button('button.png', f'P2:{self.p2_tank_type}', x=self.width/2+200, y=250),
            'play': button.Button('button.png', 'PLAY!', x=self.width/2, y=100)
        }
        self.buttons['set_ip'].active = False
        self.buttons['set_ip'].visible = False

        threading.Thread(target=self.FPS_COUNTER).start()
        pyglet.clock.schedule_interval(self.game_tick, 1/250)

    def game_tick(self, dt):
        self.dt = dt
        self.fixDt = self.desired_FPS * dt
        self.FPS_label.text = str(self.FPS)

        # Menu
        if self.current_screen == 0:
            [button.refresh(self.mouse_x, self.mouse_y, self.mouse_left_is_pressed) for button in self.buttons.values()]
        # Game
        if self.current_screen == 1:
            if self.game_mode == 'OFFLINE':
                self.player1.step(self.keys, dt)
                self.player2.step(self.keys, dt)

                # Player2 shot
                if self.player2.ready_to_shot:
                    self.bullet_list.append(bullet.Bullet(self.player2, img=self.bullet_image, batch=self.main_batch))

                for b in self.bullet_list:
                    if b.hit:
                        if b.player_id == 0:
                            self.player1.hp -= b.dmg
                        else:
                            self.player2.hp -= b.dmg
                        self.bullet_list.remove(b)
            else:
                self.player1.step(self.keys, dt)
                for b in self.bullet_list:
                    if b.hit:
                        self.bullet_list.remove(b)

                if self.player2.ready_to_shot:
                    self.make_enemy_bullet()

            # Refreshing bullets
            [b.step(self.fixDt, self.player1 if b.player_id == self.player2.player_id else self.player2) for b in
             self.bullet_list]
            # Player1 shot
            if self.player1.ready_to_shot:
                self.bullet_list.append(bullet.Bullet(self.player1, img=self.bullet_image, batch=self.main_batch))

        # 180 100

        self.draw_elements()

    def draw_elements(self):
        self.clear()
        glClearColor(46 / 255, 46 / 255, 49 / 255, 0.2)  # Bg Color

        # To draw
        # Menu
        if self.current_screen == 0:
            [b.draw() for b in self.buttons.values()]
            self.handle_buttons()

        # Game
        if self.current_screen == 1:
            self.main_batch.draw()
            self.add_ons_1.draw()

        self.message_label.text = self.text_for_message_label
        self.message_label.draw()

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
            self.p1_tank_type = 'DESTROYER' if self.p1_tank_type == 'HEAVY' else 'HEAVY'
            self.buttons['p1_tank_type'].txt_label.text = f'P1:{self.p1_tank_type}'

        if self.buttons['p2_tank_type'].click:
            self.p2_tank_type = 'DESTROYER' if self.p2_tank_type == 'HEAVY' else 'HEAVY'
            self.buttons['p2_tank_type'].txt_label.text = f'P2:{self.p2_tank_type}'

        if self.buttons['set_ip'].click:
            self.ip = input('Give me new ip:')
            self.buttons['set_ip'].txt_label.text = f'IP:{self.ip}'

        if self.buttons['gamemode'].click:
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

        if self.buttons['play'].click:
            if self.game_mode == 'OFFLINE':
                self.player1 = player.Player(self.tank_image.anchor_x, self.height-self.tank_image.anchor_y,
                                             self.p1_tank_type, 0, self.game_mode, self.height,
                                             img=self.tank_image, batch=self.main_batch)
                self.player2 = player.Player(self.width-self.tank_image.anchor_x, self.tank_image.anchor_y,
                                             self.p2_tank_type, 1, self.game_mode, self.height, img=self.tank_image,
                                             batch=self.main_batch)
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
                                                     img=self.tank_image, batch=self.main_batch)
                    else:
                        self.player1 = player.Player(self.width-self.tank_image.anchor_x, self.tank_image.anchor_y,
                                                     self.p1_tank_type, 1, self.game_mode, self.height,
                                                     img=self.tank_image, batch=self.main_batch)
                    
                    self.n.send_player(self.player1)
                    self.n.p2(self)

                    self.current_screen = 1
                    threading.Thread(target=self.trade_info).start()

                else:
                    self.display_message('Set your ip first!', 3)

    def display_message(self, message, t):
        threading.Thread(target=self.threaded_msg, args=(message, t, )).start()

    def threaded_msg(self, message, t):
        self.text_for_message_label = message
        for s in range(t):
            time.sleep(1)
        self.text_for_message_label = ''

    def trade_info(self):
        while not self.has_exit:
            self.n.trade(self.player1, self)

    def make_enemy_bullet(self):
        self.bullet_list.append(bullet.Bullet(self.player2, img=self.bullet_image, batch=self.main_batch))
        self.player2.ready_to_shot = False
        print('Made a enemy\'s bullet!')


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


if __name__ == '__main__':
    window = GameWindow(1300, 800, resizable=False, vsync=True, caption='WorldOfTanks2d')
    pyglet.app.run()
