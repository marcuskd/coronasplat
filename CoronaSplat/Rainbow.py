from os.path import join
from random import randint
from pygame.sprite import Sprite
from pygame.image import load
from pygame.sprite import from_surface
from CoronaSplat.get_path import get_path


class Rainbow(Sprite):

    def __init__(self, play_area_width, velocity):

        """
        args...
            play_area_width: width (pixels) of game play area
            play_area_height: height (pixels) of game play area
        """

        super().__init__()

        self.velocity = velocity

        image_name = join(get_path('Graphics/rainbow.png'))

        self.image = load(image_name).convert_alpha()
        self.rect = self.image.get_rect()

        self.pos_x = randint(0, play_area_width - self.rect.width)
        self.pos_y = 0

        self.pos_y_f = self.pos_y

        self.rect.left = self.pos_x

        self.on_screen = True

        self.mask = from_surface(self.image)

    def update(self, dt, play_area_height):

        """
        Update the sprite position
        args...
            dt: Time interval (s)
            play_area_height: Play area vertical extent (pixels)
        """

        self.pos_y_f += self.velocity * dt
        self.pos_y = int(self.pos_y_f)

        if self.pos_y > play_area_height - self.rect.height:
            self.on_screen = False

        self.rect.top = self.pos_y
