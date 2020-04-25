from os.path import join
from random import randint
from pygame.sprite import Sprite
from pygame.image import load
from pygame.sprite import from_surface
from CoronaSplat.get_path import get_path


class MegaVirus(Sprite):

    def __init__(self, play_area_width, play_area_height, frame_rate):

        """
        args...
            play_area_width: width (pixels) of game play area
            play_area_height: height (pixels) of game play area
            frame_rate: frame rate (frames per second)
        """

        super().__init__()

        self.score = 50  # per hit of target area

        self.velocity_x_range = (100, 250)  # pixels/s
        self.acceleration_range = (-125, 125)  # pixels/s/s

        self.velocity_x = randint(*self.velocity_x_range)
        self.acceleration = randint(*self.acceleration_range)

        if randint(0, 100) > 50:  # Equal chance of going left or right
            self.velocity_x = -self.velocity_x

        self.velocity_y = 0

        self.virus_type = 'mega'
        image_name = join(get_path('Graphics/' + self.virus_type + '_virus.png'))

        self.image = load(image_name).convert_alpha()
        self.rect = self.image.get_rect()

        half_width = int(self.rect.width / 2)
        half_height = int(self.rect.height / 2)

        self.pos_x = int(play_area_width / 2) - half_width
        self.pos_y = int(play_area_height / 2) - half_height

        self.pos_x_f = self.pos_x  # Retains fractional accuracy
        self.pos_y_f = self.pos_y

        self.xlim_left = 0
        self.xlim_right = int(play_area_width - self.rect.width)

        self.ylim_top = 0
        self.ylim_bottom = play_area_height - self.rect.height

        self.mask = from_surface(self.image)

        self.collision_radius = 10

        self.strength = 20

        self.dirn_update = frame_rate * 2
        self.dirn_count = 0

    def update(self, dt):

        """
        Update the sprite position
        args...
            dt: Time interval (s)
        """

        self.pos_x_f += self.velocity_x * dt

        self.velocity_y += self.acceleration * dt
        self.pos_y_f += self.velocity_y * dt

        if self.pos_x_f >= self.xlim_right:
            self.pos_x_f = self.xlim_right
            self.velocity_x = -self.velocity_x
        elif self.pos_x_f <= self.xlim_left:
            self.pos_x_f = self.xlim_left
            self.velocity_x = -self.velocity_x

        if self.pos_y_f <= self.ylim_top:
            self.pos_y_f = self.ylim_top
            self.velocity_y = -self.velocity_y
        if self.pos_y_f >= self.ylim_bottom:
            self.pos_y_f = self.ylim_bottom
            self.velocity_y = -self.velocity_y

        self.pos_x = int(self.pos_x_f)
        self.pos_y = int(self.pos_y_f)

        self.rect.left = self.pos_x
        self.rect.top = self.pos_y

        if self.dirn_count == self.dirn_update:
            self.dirn_count = 0
            self.velocity_x = randint(*self.velocity_x_range)
            if randint(0, 100) > 50:
                self.velocity_x = -self.velocity_x
            self.acceleration = randint(*self.acceleration_range)
        else:
            self.dirn_count += 1
