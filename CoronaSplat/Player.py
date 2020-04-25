from os.path import join
from pygame.sprite import Sprite
from pygame.image import load
from pygame.sprite import from_surface
from CoronaSplat.get_path import get_path


class Player(Sprite):

    def __init__(self, play_area_width, play_area_height, frame_rate):

        """
        args...
            play_area_width: width (pixels) of game play area
            play_area_height: height (pixels) of game play area
            frame_rate: frame rate (frames per second)
        """

        super().__init__()

        self.velocity_x_abs = 200  # pixels/s
        self.velocity_x = 0

        image_names = ['Graphics/player_front.png',
                       'Graphics/player_back.png',
                       'Graphics/player_left1.png',
                       'Graphics/player_left2.png',
                       'Graphics/player_left3.png',
                       'Graphics/player_left4.png',
                       'Graphics/player_right1.png',
                       'Graphics/player_right2.png',
                       'Graphics/player_right3.png',
                       'Graphics/player_right4.png']

        self.images = [load(join(get_path(image_names[img]))).convert_alpha() for img in range(len(image_names))]

        self.image_index = 0  # Start facing outwards
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()

        self.image_update_interval = 0.03  # s
        self.image_update_frames = int(self.image_update_interval * frame_rate)
        self.image_update_count = 0
        self.image_increment = 1  # Used to move forwards and backwards between images for walking effect

        self.pos_x = int(play_area_width / 2 - self.rect.width / 2)
        self.pos_y = play_area_height - self.rect.height

        self.xlim_left = 0
        self.xlim_right = int(play_area_width - self.rect.width)

        self.rect.left = self.pos_x
        self.rect.top = self.pos_y

        self.mask = from_surface(self.image)

    def update(self, dirn, dt):

        """
        Update the sprite position
        args...
            dirn: Direction string
            dt: Time interval (s)
        """

        if dirn is not None:

            if dirn == 'LEFT':
                self.velocity_x = -self.velocity_x_abs
            elif dirn == 'RIGHT':
                self.velocity_x = self.velocity_x_abs

            self.pos_x += int(self.velocity_x * dt)

            if self.pos_x >= self.xlim_right:
                self.pos_x = self.xlim_right
            elif self.pos_x <= self.xlim_left:
                self.pos_x = self.xlim_left

            self.image_update_count += 1

            if self.image_update_count == self.image_update_frames:

                self.image_update_count = 0

                if dirn == 'LEFT':
                    if (self.image_index < 2) or (self.image_index > 5):  # Starting to move left
                        self.image_index = 2
                    else:  # Continuing to move left
                        self.image_index += self.image_increment
                        if self.image_index > 5:
                            self.image_index = 5
                            self.image_increment = -1
                        if self.image_index < 2:
                            self.image_index = 2
                            self.image_increment = 1

                if dirn == 'RIGHT':
                    if self.image_index < 6:  # Starting to move right
                        self.image_index = 6
                    else:  # Continuing to move right
                        self.image_index += self.image_increment
                        if self.image_index > 9:
                            self.image_index = 9
                            self.image_increment = -1
                        if self.image_index < 6:
                            self.image_index = 6
                            self.image_increment = 1

                if dirn == 'FORWARD':
                    self.image_index = 1
                    self.velocity_x = 0

            self.rect.left = self.pos_x

            self.image = self.images[self.image_index]
            self.mask = from_surface(self.image)
