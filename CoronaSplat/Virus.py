from os.path import join
from math import sqrt
from random import randint
from pygame.sprite import Sprite
from pygame.image import load
from pygame.sprite import from_surface
from CoronaSplat.get_path import get_path


class Virus(Sprite):

    def __init__(self, play_area_width, play_area_height, min_start_height, virus_type,
                 pos_x=None, pos_y=None, speed_scale=1):

        """
        args...
            play_area_width: width (pixels) of game play area
            play_area_height: height (pixels) of game play area
            min_start_height: minimum starting height (pixels) for virus
            virus_type: 'large', 'medium' or 'small'
        kwargs...
            pos_x: x position (pixels) for spawning after larger virus killed
            pos_y: y position (pixels) for spawning after larger virus killed
            speed_scale: scale factor for speed (applied to velocity and acceleration)
        """

        super().__init__()

        scores = {'large': 10,
                  'medium': 20,
                  'small': 30}
        self.score = scores[virus_type]

        velocity_x_lims = {'large': (20, 40),
                           'medium': (30, 60),
                           'small': (40, 80)}  # pixels/s
        accelerations = {'large': 200, 'medium': 400, 'small': 600}  # pixels/s/s

        self.velocity_x = randint(*velocity_x_lims[virus_type])
        self.velocity_x *= speed_scale
        self.acceleration = accelerations[virus_type] * speed_scale

        if randint(0, 100) > 50:
            self.velocity_x = -self.velocity_x

        self.velocity_y = 0

        self.virus_type = virus_type
        image_name = join(get_path('Graphics/' + self.virus_type + '_virus.png'))

        self.image = load(image_name).convert_alpha()
        self.rect = self.image.get_rect()

        half_width = int(self.rect.width / 2)
        half_height = int(self.rect.height / 2)

        if pos_x is None:
            self.pos_x = randint(half_width, play_area_width - half_width)
        else:
            self.pos_x = pos_x

        if pos_y is None:
            self.pos_y = randint(min_start_height + half_height, play_area_height - half_height)
        else:
            self.pos_y = play_area_height - pos_y

        self.velocity_bounce = -sqrt(2 * self.acceleration * self.pos_y)
        self.pos_y = play_area_height - self.pos_y  # y +ve downwards

        self.pos_x_f = self.pos_x  # Retains fractional accuracy
        self.pos_y_f = self.pos_y

        self.xlim_left = 0
        self.xlim_right = int(play_area_width - self.rect.width)

        self.ylim = play_area_height - self.rect.height

        self.mask = from_surface(self.image)

        self.collision_radius = self.rect.width / 2

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

        if self.pos_y_f >= self.ylim:
            self.pos_y_f = self.ylim
            self.velocity_y = self.velocity_bounce

        self.pos_x = int(self.pos_x_f)
        self.pos_y = int(self.pos_y_f)

        self.rect.left = self.pos_x
        self.rect.top = self.pos_y
