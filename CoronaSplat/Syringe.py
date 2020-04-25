from os.path import join
from pygame.sprite import Sprite
from pygame.image import load
from CoronaSplat.get_path import get_path


class Syringe(Sprite):

    def __init__(self, start_pos_x, start_pos_y):

        """
        args...
            start_pos_x: starting x coordinate (pixels)
            start_pos_y: starting y coordinate (pixels)
        """

        super().__init__()

        self.velocity = -500  # pixels/s

        image_name = join(get_path('Graphics/syringe.png'))

        self.image = load(image_name).convert_alpha()
        self.rect = self.image.get_rect()

        half_width = int(self.rect.width / 2)
        half_height = int(self.rect.height / 2)
        self.pos_x = start_pos_x - half_width
        self.pos_y = start_pos_y - half_height

        self.pos_y_f = self.pos_y

        self.rect.left = self.pos_x

        self.on_screen = True

    def update(self, dt):

        """
        Update the sprite position
        args...
            dt: Time interval (s)
        """

        self.pos_y_f += self.velocity * dt
        self.pos_y = int(self.pos_y_f)

        if self.pos_y < 0:
            self.on_screen = False

        self.rect.top = self.pos_y
