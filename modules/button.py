import pyglet

pyglet.resource.path = ["resources"]
pyglet.resource.reindex()


class Button(pyglet.sprite.Sprite):
    def __init__(self, file_name, text="", x=0, y=0, long_press=False):
        self.sprites_image = pyglet.resource.image(file_name)
        self.sprites = pyglet.image.ImageGrid(self.sprites_image, 1, 3)
        [center_image(self.sprites[i]) for i in range(len(self.sprites))]
        self.pressed = False
        self.click = False
        self.long_press = long_press
        self.active = True

        super(Button, self).__init__(img=self.sprites[0], x=x, y=y)

        self.txt_label = pyglet.text.Label(text=text, anchor_x='center', anchor_y='center',
                                           font_size=36, font_name='Born2bSportyV2',
                                           x=round(self.x),
                                           y=round(self.y))

        self.left = self.x - self.image.anchor_x
        self.right = self.left + self.width
        self.bottom = self.y - self.image.anchor_y
        self.top = self.bottom + self.height

    def refresh(self, mouse_x, mouse_y, pressed):
        if not self.active:
            return

        self.left = self.x - self.image.anchor_x
        self.right = self.left + self.width
        self.bottom = self.y - self.image.anchor_y
        self.top = self.bottom + self.height

        self.txt_label.x, self.txt_label.y = round(self.x), round(self.y)

        self.click = False
        if self.collision(mouse_x, mouse_y):
            self.image = self.sprites[1]

            if pressed:
                self.image = self.sprites[2]
                # When not clicked yet send signal about click
                if not self.pressed or self.long_press:
                    self.click = True

            self.pressed = pressed

        else:
            self.image = self.sprites[0]

    def collision(self, point_x, point_y):
        if point_x < self.left:
            return False
        if point_x > self.right:
            return False
        if point_y < self.bottom:
            return False
        if point_y > self.top:
            return False
        return True

    def draw(self):
        super(Button, self).draw()
        if self.visible:
            self.txt_label.draw()


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
