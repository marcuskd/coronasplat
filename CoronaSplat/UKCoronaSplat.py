from os.path import isdir, isfile, join

from time import time
from math import sqrt
from random import randint

import pickle

import pygame

from CoronaSplat.Player import Player
from CoronaSplat.Virus import Virus
from CoronaSplat.MegaVirus import MegaVirus
from CoronaSplat.Syringe import Syringe
from CoronaSplat.Rainbow import Rainbow
from CoronaSplat.get_path import get_path


pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
pygame.init()


def run_game():

    """
    Run the game!
    """

    # --- Initialise variables ---

    # Layout and speed

    screen_height = 800
    screen_width = 1000

    bar_height = 75
    play_area_height = screen_height - bar_height
    play_area_rect = pygame.Rect(0, 0, screen_width, play_area_height)

    frames_per_second = 100
    update_interval = 1 / frames_per_second

    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    pause_interval = 3000  # ms

    # Fonts

    large_text_font_size = 36
    large_text_font = pygame.font.Font(join(get_path('Data/NotoSans-Regular.ttf')), large_text_font_size)
    small_text_font_size = 24
    small_text_font = pygame.font.Font(join(get_path('Data/NotoSans-Regular.ttf')), small_text_font_size)
    score_text_font_size = 30
    score_text_font = pygame.font.Font(join(get_path('Data/NotoSans-Bold.ttf')), score_text_font_size)

    # Load images

    icon_image = pygame.image.load(join(get_path('Graphics/small_virus.png')))
    pygame.display.set_icon(icon_image)
    pygame.display.set_caption('UK CoronaSplat!')

    life_image = pygame.image.load(join(get_path('Graphics/player_left1.png'))).convert_alpha()
    life_spacing = life_image.get_rect().width + 10
    ground_rect = pygame.Rect((0, play_area_height, screen_width, 5))

    nhscore_logo = pygame.image.load(join(get_path('Graphics/NHScore.png'))).convert_alpha()
    jump_image = pygame.image.load(join(get_path('Graphics/player_front.png'))).convert_alpha()

    # Load sounds

    throw_sound = pygame.mixer.Sound(file=join(get_path('Sounds/throw_syringe.wav')))
    splat_sound = pygame.mixer.Sound(file=join(get_path('Sounds/virus_splat.wav')))
    new_virus_sound = pygame.mixer.Sound(file=join(get_path('Sounds/new_virus.wav')))
    lose_life_sound = pygame.mixer.Sound(file=join(get_path('Sounds/lose_life.wav')))
    new_life_sound = pygame.mixer.Sound(file=join(get_path('Sounds/new_life.wav')))
    finished_level_sound = pygame.mixer.Sound(file=join(get_path('Sounds/finished_level.wav')))
    finished_game_sound = pygame.mixer.Sound(file=join(get_path('Sounds/finished_game.wav')))

    # Levels

    num_levels = 10
    rainbow_velocities = [110 + lnum * 10 for lnum in range(num_levels)]  # New life velocities
    speed_scales = [1.2 + 0.05 * lnum for lnum in range(num_levels)]  # Virus speed scale factors
    speed_scales[num_levels - 1] = 2
    num_viruses = [5 + lnum for lnum in range(num_levels)]
    num_viruses[num_levels - 1] = 99999

    # Player

    max_num_lives = 5
    num_lives_start = 3

    min_new_life_interval = 90  # seconds
    max_new_life_interval = 150
    min_new_life_interval_frames = int(min_new_life_interval * frames_per_second)
    max_new_life_interval_frames = int(max_new_life_interval * frames_per_second)

    invincible_time = 2  # s
    invincible_frames = int(invincible_time * frames_per_second)
    invincible_count = 0

    xpos_jump = int(screen_width / 2) - int(jump_image.get_rect().width / 2)
    ypos_jump = play_area_height - jump_image.get_rect().height - 1

    jump_accn = 60
    jump_interval = 0.1  # s

    # Syringes

    syringe_throw_interval = 0.125  # seconds
    syringe_throw_interval_frames = int(syringe_throw_interval * frames_per_second)

    # Viruses

    min_virus_interval = 3  # seconds
    max_virus_interval = 8
    min_virus_interval_frames = int(min_virus_interval * frames_per_second)
    max_virus_interval_frames = int(max_virus_interval * frames_per_second)

    virus_min_start_height = int(0.75 * play_area_height)

    # Scoring

    score_xpos = int(screen_width * 0.85)
    score_ypos = play_area_height + 20

    lives_rect = pygame.Rect(0, play_area_height + 10, int(screen_width / 2), bar_height)
    score_rect = pygame.Rect(score_xpos, score_ypos, screen_width - score_xpos, bar_height)

    num_high_scores = 10
    max_num_chars = 30

    # Load High Scores

    home_dir = 'C:/CoronaSplat'
    if isdir(home_dir):
        hiscore_file = join(home_dir, 'hiscores.dat')
    else:
        hiscore_file = join(get_path('Data/hiscores.dat'))

    if isfile(hiscore_file):
        with open(hiscore_file, 'rb') as fi:
            hiscores = pickle.load(fi)
    else:
        hiscores = {'Names': [None] * num_high_scores, 'Scores': [None] * num_high_scores, 'Times': [None] * num_high_scores}

    # --- Intro ---

    splash_screen = pygame.image.load(join(get_path('Graphics/logo.png')))

    splash_rect = splash_screen.get_rect()
    splash_width = splash_rect.width
    splash_height = splash_rect.height

    splash_screen_scaled = splash_screen.copy()

    scale_fact = 10
    scale_step = 0.1

    nsc = int((scale_fact - 1) / scale_step)

    max_delay = 50

    intro_sound = pygame.mixer.Sound(file=join(get_path('Sounds/intro_sound.wav')))
    intro_sound.play()

    for scn in range(nsc):

        scale = scale_fact - (scn / nsc) * (scale_fact - 1)
        scale_width = int(splash_width * scale)
        scale_height = int(splash_height * scale)

        splash_screen_scaled = pygame.transform.smoothscale(splash_screen_scaled, (scale_width, scale_height))
        splash_rect_scaled = splash_screen_scaled.get_rect()

        screen.blit(splash_screen_scaled, (int(screen_width / 2 - splash_rect_scaled.width / 2),
                                           int(screen_height / 2 - splash_rect_scaled.height / 2)))

        pygame.display.update()

        delay = int(max_delay * (1 - scn / nsc))
        if delay < 1:
            delay = 1

        pygame.time.wait(delay)

    # Background music

    pygame.mixer.music.load(join(get_path('Sounds/background_music.mp3')))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)

    pygame.time.wait(pause_interval)

    # --- Key layout selection ---

    keys_right_handed = {'Left': (pygame.K_z, 'Z'), 'Right': (pygame.K_x, 'X'), 'Throw': (pygame.K_RETURN, 'Enter')}
    keys_left_handed = {'Left': (pygame.K_LEFT, 'Left arrow'), 'Right': (pygame.K_RIGHT, 'Right arrow'), 'Throw': (pygame.K_TAB, 'Tab')}

    screen.fill((0, 0, 0))
    pygame.display.update()

    line = 'Press R for right-handed keyboard layout,'
    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) - int(large_text_font_size / 2) - 5))
    line = 'L for left-handed'
    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) + int(large_text_font_size / 2) + 5))
    pygame.display.update()

    checking = True
    while checking:
        for ievent in pygame.event.get():
            if ievent.type == pygame.KEYDOWN:
                if ievent.key == pygame.K_r:
                    checking = False
                    keys = keys_right_handed
                    line = 'Right-handed keyboard layout selected:'
                elif ievent.key == pygame.K_l:
                    checking = False
                    keys = keys_left_handed
                    line = 'Left-handed keyboard layout selected:'

    screen.fill((0, 0, 0))

    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) - large_text_font_size * 2))
    pygame.display.update()

    line = 'Left: ' + keys['Left'][1]
    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2)))

    line = 'Right: ' + keys['Right'][1]
    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) + large_text_font_size))

    line = 'Throw: ' + keys['Throw'][1]
    text = large_text_font.render(line, True, (255, 255, 255))
    screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) + large_text_font_size * 2))

    pygame.display.update()

    pygame.time.wait(pause_interval)

    # --- Game active loop ---

    game_active = True

    while game_active:

        # Reset variables

        num_lives = num_lives_start
        new_life_count = 0

        level = 0
        score = 0

        game_running = True
        game_complete = False

        # Display lives and score

        screen.fill((0, 0, 0))
        pygame.display.update()

        pygame.draw.rect(screen, (0, 255, 0), ground_rect)

        for lnum in range(num_lives - 1):
            screen.blit(life_image, (lnum * life_spacing, play_area_height + 10))

        screen.blit(nhscore_logo, (int(screen_width * 0.63), play_area_height + 10))

        text = score_text_font.render(str(score), True, (255, 255, 255))
        screen.blit(text, (score_xpos, score_ypos))

        pygame.display.update()

        start_time = time()

        # --- Game level loop ---

        while game_running:

            # Start a new level

            screen.fill((0, 0, 0), rect=play_area_rect)

            if level < num_levels - 1:
                line = 'Get Ready for Level ' + str(level + 1) + '!'
            else:
                line = 'Get Ready for Level ' + str(level + 1) + '.  DESTROY THE MEGAVIRUS!!!'
            text = large_text_font.render(line, True, (255, 255, 255))
            screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) - large_text_font_size))
            pygame.display.update(play_area_rect)
            pygame.time.wait(pause_interval)

            rainbow_velocity = rainbow_velocities[level]
            speed_scale = speed_scales[level]
            max_viruses = num_viruses[level]
            num_spawned = 0
            num_killed = 0

            if level == num_levels - 1:
                core_colour_count = 0
                core_colour = (255, 0, 0)
                core_colour_mult = int(frames_per_second / 10)

            viruses = []  # List of active viruses
            syringes = []  # List of active syringes
            rainbows = []  # List of active rainbows

            syringe_throw_count = syringe_throw_interval_frames
            virus_interval_count = 0

            virus_group = pygame.sprite.Group()

            player = Player(screen_width, play_area_height, frames_per_second)

            dirn = None

            level_running = True
            level_complete = False

            while level_running:

                update_lives = False
                update_score = False

                # Process events

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:

                        line = 'Press Q to quit or R to resume'
                        text = large_text_font.render(line, True, (255, 255, 255))
                        screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(play_area_height / 2)))
                        pygame.display.update(play_area_rect)

                        checking = True
                        while checking:
                            for ievent in pygame.event.get():
                                if ievent.type == pygame.KEYDOWN:
                                    if ievent.key == pygame.K_q:
                                        checking = False
                                        game_running = False
                                        level_running = False
                                    elif ievent.key == pygame.K_r:
                                        checking = False

                    elif event.type == pygame.KEYDOWN:

                        if event.key == keys['Left'][0]:
                            dirn = 'LEFT'
                        elif event.key == keys['Right'][0]:
                            dirn = 'RIGHT'
                        elif event.key == keys['Throw'][0]:
                            if syringe_throw_count >= syringe_throw_interval_frames:
                                throw_sound.play()
                                dirn = 'FORWARD'
                                syringe_throw_count = 0
                                syringes.append(Syringe(player.pos_x + int(player.rect.width * 0.9), player.pos_y))

                    elif event.type == pygame.KEYUP:
                        dirn = None

                syringe_throw_count += 1

                # Process collisions between syringes and viruses

                for syringe in syringes:  # Loop through all syringes

                    xs = syringe.pos_x
                    ys = syringe.pos_y

                    for virus in viruses:  # Loop through all viruses

                        xv = virus.pos_x + virus.rect.width / 2
                        yv = virus.pos_y + virus.rect.height / 2

                        # Check for collision

                        rd = sqrt((xv - xs) ** 2 + (yv - ys) ** 2)

                        if rd <= virus.collision_radius:

                            splat_sound.play()

                            syringes.remove(syringe)

                            if virus.virus_type == 'small':
                                num_killed += 1

                            if virus.virus_type == 'medium':

                                for num in range(2):
                                    new_virus = Virus(screen_width, play_area_height, virus_min_start_height,
                                                      'small', pos_x=xv, pos_y=yv, speed_scale=speed_scale)
                                    viruses.append(new_virus)
                                    virus_group.add(new_virus)

                            elif virus.virus_type == 'large':

                                for num in range(2):
                                    new_virus = Virus(screen_width, play_area_height, virus_min_start_height,
                                                      'medium', pos_x=xv, pos_y=yv, speed_scale=speed_scale)
                                    viruses.append(new_virus)
                                    virus_group.add(new_virus)

                            elif virus.virus_type == 'mega':
                                virus.strength -= 1

                            score += virus.score
                            update_score = True

                            if virus.virus_type != 'mega':
                                viruses.remove(virus)
                                virus_group.remove(virus)

                            break

                if level < num_levels - 1:

                    if num_killed == max_viruses * 4:
                        level_complete = True
                        level_running = False

                elif (len(viruses) > 0) and (viruses[0].strength == 0):  # MegaVirus destroyed!

                    level_complete = True
                    level_running = False
                    score += 500

                    finished_game_sound.play()

                    virus = viruses[0]

                    width = virus.rect.width
                    height = virus.rect.height
                    image = virus.image.copy()

                    theta_step = 5
                    ntheta = int(360 / theta_step)

                    # Destruction sequence of scaled and rotated images

                    for thn in range(ntheta):

                        theta = thn * theta_step

                        screen.fill((0, 0, 0), play_area_rect)

                        scale_fact = 1 - theta / 360
                        scale_width = int(width * scale_fact)
                        scale_height = int(height * scale_fact)
                        image_scaled = pygame.transform.smoothscale(image, (scale_width, scale_height))
                        image_rotated = pygame.transform.rotate(image_scaled, theta)

                        pos_x = virus.pos_x + int(width / 2) - int(scale_width / 2)
                        pos_y = virus.pos_y + int(height / 2) - int(scale_height / 2)

                        screen.blit(image_rotated, (pos_x, pos_y))

                        pygame.display.update()

                        pygame.time.wait(10)

                if invincible_count >= invincible_frames:
                    vlist = pygame.sprite.spritecollide(player, virus_group, False, collided=pygame.sprite.collide_mask)
                else:
                    vlist = []
                    invincible_count += 1

                # Process collisions between player and viruses

                if len(vlist) > 0:

                    for virus in vlist:

                        if virus.virus_type == 'large':
                            num_killed += 4
                        elif virus.virus_type == 'medium':
                            num_killed += 2
                        else:
                            num_killed += 1

                        if virus.virus_type != 'mega':
                            viruses.remove(virus)
                            virus_group.remove(virus)

                    num_lives -= 1
                    update_lives = True
                    invincible_count = 0
                    lose_life_sound.play()

                    if num_lives == 0:

                        level_running = False
                        game_running = False

                    else:

                        player.pos_x = int(screen_width / 2 - player.rect.width / 2)  # Reset player position
                        dirn = 'FORWARD'

                    pygame.time.wait(pause_interval)

                # Process collisions between player and rainbows (new lives)

                for rainbow in rainbows:

                    if pygame.sprite.collide_mask(player, rainbow):

                        num_lives += 1
                        update_lives = True
                        rainbows.remove(rainbow)
                        new_life_sound.play()

                # Start new viruses

                if (level == num_levels - 1) and len(viruses) == 0:

                    new_virus_sound.play()
                    virus = MegaVirus(screen_width, play_area_height, frames_per_second)
                    viruses.append(virus)
                    virus_group.add(virus)
                    num_spawned += 1

                if num_spawned < max_viruses:

                    if virus_interval_count >= randint(min_virus_interval_frames, max_virus_interval_frames):

                        if level == num_levels - 1:

                            pos_x = viruses[0].pos_x + int(viruses[0].rect.width / 2)
                            pos_y = viruses[0].pos_y + int(viruses[0].rect.height / 2)
                            virus_type = 'small'

                        else:
                            pos_x = pos_y = None
                            virus_type = 'large'

                        new_virus_sound.play()
                        virus_interval_count = 0
                        virus = Virus(screen_width, play_area_height, virus_min_start_height,
                                      virus_type, speed_scale=speed_scale, pos_x=pos_x, pos_y=pos_y)
                        viruses.append(virus)
                        virus_group.add(virus)
                        num_spawned += 1

                virus_interval_count += 1

                # Start new rainbows

                if new_life_count >= randint(min_new_life_interval_frames, max_new_life_interval_frames):
                    new_life_count = 0
                    if num_lives < max_num_lives:
                        rainbows.append(Rainbow(screen_width, rainbow_velocity))
                else:
                    new_life_count += 1

                # Redraw

                screen.fill((0, 0, 0), rect=play_area_rect)

                player.update(dirn, update_interval)
                screen.blit(player.image, (player.pos_x, player.pos_y))

                for virus in viruses:
                    virus.update(update_interval)
                    screen.blit(virus.image, (virus.pos_x, virus.pos_y))

                if level == num_levels - 1:

                    virus = viruses[0]
                    pos_x = virus.pos_x + int(virus.rect.width / 2)
                    pos_y = virus.pos_y + int(virus.rect.height / 2)

                    if core_colour_count >= virus.strength * core_colour_mult:
                        core_colour_count = 0
                        if core_colour == (255, 0, 0):
                            core_colour = (0, 255, 0)
                        else:
                            core_colour = (255, 0, 0)
                    core_colour_count += 1

                    pygame.draw.circle(screen, core_colour, (pos_x, pos_y), int(virus.collision_radius))

                # Remove syringes which have gone off the screen

                for syringe in syringes:
                    if not syringe.on_screen:
                        syringes.remove(syringe)

                for syringe in syringes:
                    syringe.update(update_interval)
                    screen.blit(syringe.image, (syringe.pos_x, syringe.pos_y))

                # Remove rainbows which have gone off the screen

                for rainbow in rainbows:
                    if not rainbow.on_screen:
                        rainbows.remove(rainbow)

                for rainbow in rainbows:
                    rainbow.update(update_interval, play_area_height)
                    screen.blit(rainbow.image, (rainbow.pos_x, rainbow.pos_y))

                # Update display

                pygame.display.update(play_area_rect)

                if update_score:
                    screen.fill((0, 0, 0), rect=score_rect)
                    text = score_text_font.render(str(score), True, (255, 255, 255))
                    screen.blit(text, (score_xpos, score_ypos))
                    pygame.display.update(score_rect)

                if update_lives:
                    screen.fill((0, 0, 0), rect=lives_rect)
                    for lnum in range(num_lives - 1):
                        screen.blit(life_image, (lnum * life_spacing, play_area_height + 10))
                    pygame.display.update(lives_rect)

                clock.tick(frames_per_second)

            # End of level

            if level_complete:

                finished_level_sound.play()
                screen.fill((0, 0, 0), rect=play_area_rect)
                line = 'Completed Level ' + str(level + 1) + '!'
                level += 1
                text = large_text_font.render(line, True, (255, 255, 255))

                for num_jumps in range(3):
                    ypos = ypos_jump - 1
                    jump_vel = -80
                    while ypos < ypos_jump:
                        screen.fill((0, 0, 0), play_area_rect)
                        screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) - large_text_font_size))
                        jump_vel += jump_accn * jump_interval
                        ypos += int(jump_vel * jump_interval)
                        if ypos > ypos_jump:
                            ypos = ypos_jump
                        screen.blit(jump_image, (xpos_jump, ypos))
                        pygame.display.update(play_area_rect)
                        pygame.time.wait(30)

                if level == num_levels:
                    game_complete = True
                    game_running = False

        end_time = time()
        game_time = end_time - start_time

        # Update and save High Scores

        scores = hiscores['Scores']
        score_ind = None
        if score > 0:
            for ind in range(len(scores)):
                if (scores[ind] is None) or (score > scores[ind]):
                    score_ind = ind

        # -- Score --

        screen.fill((0, 0, 0))

        if game_complete:
            line = 'CONGRATULATIONS - you have completed UK CoronaSplat!!!'
        else:
            line = 'Game Over!'

        text = large_text_font.render(line, True, (255, 255, 255))
        screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) - large_text_font_size))
        line = 'Score: ' + str(score)
        text = large_text_font.render(line, True, (255, 255, 255))
        screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2)))

        pygame.display.update()

        if score_ind is not None:

            if score_ind == num_high_scores - 1:
                finished_level_sound.play()
                line = 'Congratulations, you have beaten the high score!'
                text = large_text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (int(screen_width / 2) - int(text.get_width() / 2), int(screen_height / 2) + large_text_font_size))

            line = 'Enter your name for the high score table (max ' + str(max_num_chars) + ' characters) and press Enter:'
            text = small_text_font.render(line, True, (255, 255, 255))
            xpos = int(screen_width / 2) - int(text.get_width() / 2)
            screen.blit(text, (xpos, int(screen_height / 2) + 3 * large_text_font_size))

            pygame.display.update()

            ypos = int(screen_height / 2) + 4 * large_text_font_size

            nchars = 0
            entered = False
            name = ''

            # Capture entered characters for name

            while (not entered) and (nchars < max_num_chars):

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if nchars > 0:
                                entered = True
                        else:
                            code = event.key
                            if 32 <= code <= 127:
                                name += chr(code)
                                nchars += 1
                                text = small_text_font.render(name, True, (255, 255, 255))
                                screen.blit(text, (xpos, ypos))
                                pygame.display.update()

            for sind in range(score_ind):
                hiscores['Names'][sind] = hiscores['Names'][sind + 1]
                hiscores['Scores'][sind] = hiscores['Scores'][sind + 1]
                hiscores['Times'][sind] = hiscores['Times'][sind + 1]

            hiscores['Names'][score_ind] = name
            hiscores['Scores'][score_ind] = score
            hiscores['Times'][score_ind] = game_time

            with open(hiscore_file, 'wb') as fi:
                pickle.dump(hiscores, fi, protocol=pickle.HIGHEST_PROTOCOL)

        else:
            pygame.time.wait(pause_interval)

        # -- Credits and game restart --

        lines = [
            'UK CoronaSplat!',
            '',
            'Game by Theo, Lucas and Marcus',
            'Heroics by Jan',
            '',
            'If you have enjoyed the game',
            'please support our NHS by donating to',
            'NHS Charities Together',
            '',
            'https://www.nhscharitiestogether.co.uk/',
            '',
            'Thanks to pygame for a great game dev library,',
            'zapsplat.com for the sound effects and',
            'pyinstaller for the distribution',
            '',
            'Press any key to restart',
            '',
            'High Scores...',
            ''
        ]

        for ind in range(len(hiscores['Names']) - 1, -1, -1):
            if hiscores['Names'][ind] is not None:
                times = hiscores['Times'][ind]
                mins = times // 60
                secs = times % 60
                timestr = '{0:3.0f} minutes, {1:3.1f} seconds'.format(mins, secs)
                lines.append(str(hiscores['Scores'][ind]) + ' by ' + hiscores['Names'][ind] + ' in ' + timestr)

        max_len1 = max([large_text_font.render(line, True, (255, 255, 255)).get_width() for line in lines[:8]])
        max_len2 = max([small_text_font.render(line, True, (255, 255, 255)).get_width() for line in lines[8:]])
        max_len = max(max_len1, max_len2)
        ypos = screen_height
        xpos = int(screen_width / 2) - int(max_len / 2)

        credits_running = True

        while credits_running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    credits_running = False
                    game_active = False
                if event.type == pygame.KEYDOWN:
                    credits_running = False

            screen.fill((0, 0, 0))

            for lin in range(len(lines)):
                if lin < 8:
                    disp_font = large_text_font
                else:
                    disp_font = small_text_font
                text = disp_font.render(lines[lin], True, (255, 255, 255))
                screen.blit(text, (xpos, ypos + lin * large_text_font_size))

            pygame.display.update()

            ypos -= 1
            if ypos + len(lines) * large_text_font_size <= 0:
                ypos = screen_height

            clock.tick(frames_per_second)


if __name__ == '__main__':
    run_game()
