import os
import random
import pygame
from pygame._sdl2.video import Window
from screeninfo import get_monitors
import sys
import time 

from movement import Movement
from arena import Arena
from arenaBuilder import ArenaBuilder
from robot import Robot
from screens import Screens

pygame.init()

display_resolution = (720, 720)
available_resolutions = [(720, 720), (1280, 720), (1280, 1080), (1920, 1080)]
monitor = get_monitors()[0]
fullscreen_res = (monitor.width, monitor.height)
fullscreen = False

screen = pygame.display.set_mode(display_resolution)
pygame.display.set_caption("Robo Arena")

white = (255, 255, 255)

map_name = "secondMap.json"
arena = Arena(map_name, pygame)
movement = Movement(arena.tile_size / 120.0)
screens = Screens(pygame)

robot_radius = arena.tile_size * 0.5

game_paused = False
run = True
start_game = False
menu = True
build_arena = False
settings = False
playing = False
map = False
player_count = 0
death = False
robots = []
direction_left = False

input_active_x = False
input_active_y = False
x_tiles = ""
y_tiles = ""

# Zähler für die Anzahl der Frames, bevor die Richtung des Roboters geändert wird
change_direction_interval = 100  # Ändere die Richtung alle 120 Frames
frame_count = 0
# Initiale Fensterposition
window = Window.from_display_module()
initial_window_pos = window.position

jump = []

clock = pygame.time.Clock()

pygame.mixer.init()
jumping_sound = pygame.mixer.Sound("Sounds/jumping.mp3")
death_sound = pygame.mixer.Sound("Sounds/death.mp3")
damage_sound = pygame.mixer.Sound("Sounds/damage.mp3")
footsteps_sound = pygame.mixer.Sound("Sounds/footsteps.mp3")
click_sound = pygame.mixer.Sound("Sounds/click.mp3")
fight_sound = pygame.mixer.Sound("Sounds/fight.mp3")
music = pygame.mixer.Sound("Sounds/music.mp3")

def get_json_filenames(directory):
    json_files = []
    # Gehe durch alle Dateien im angegebenen Verzeichnis
    for filename in os.listdir(directory):
        # Überprüfe, ob die Datei die Endung .json hat
        if filename.endswith(".json"):
            # Überprüfe, ob es nicht die emptyMap ist, denn diese wird ausgeschlossen
            if filename != "emptyMap.json":
                # Füge den Dateinamen ohne die Endung .json der Liste hinzu
                json_files.append(filename[:-5])
    return json_files


def get_png_filenames(directory):
    png_files = []
    # Gehe durch alle Dateien im angegebenen Verzeichnis
    for filename in os.listdir(directory):
        # Überprüfe, ob die Datei die Endung .png hat
        if filename.endswith(".png"):
            # Füge den Dateinamen der Liste hinzu
            png_files.append(filename)
    return png_files


def recalculate_robot_values():
    global robots, robot_radius
    robot_radius = arena.tile_size * 0.5
    if robots:
        for i, robot in enumerate(robots):
            robot.radius = robot_radius
            robot.posx = arena.spawn_positions[i][0] + robot_radius
            robot.posy = arena.spawn_positions[i][1] + robot_radius
            robot.accel_max = arena.tile_size / 50.0
            robot.accel_alpha_max = arena.tile_size / 50.0
            robot.vel_max = arena.tile_size / 10.0


def handle_main_menu_events():
    global robots, map, menu, build_arena, settings, run

    if play_rect.collidepoint(mouse_pos):
        robots = []
        map = True
        menu = False
    elif build_arena_rect.collidepoint(mouse_pos):
        build_arena = True
        menu = False
    elif settings_rect.collidepoint(mouse_pos):
        settings = True
        menu = False
    elif exit_rect.collidepoint(mouse_pos):
        run = False


def handle_build_arena_menu_events(event):
    global input_active_x, input_active_y, build_arena, menu, arenaBuilder, x_tiles, y_tiles

    if event.type == pygame.MOUSEBUTTONDOWN:
        if input_rect_x_tiles.collidepoint(mouse_pos):
            input_active_x = True
            input_active_y = False
        elif input_rect_y_tiles.collidepoint(mouse_pos):
            input_active_y = True
            input_active_x = False
        elif start_building_rect.collidepoint(mouse_pos):
            try:
                num_x = int(x_tiles)
                num_y = int(y_tiles)
                if num_x <= 0 or num_y <= 0:
                    raise ValueError
                build_arena = False
                menu = True
                arenaBuilder = ArenaBuilder(num_x, num_y, pygame)
                arenaBuilder.main()
            except ValueError:
                screens.show_popup("There should only be positive numbers in the fields!")

    elif event.type == pygame.KEYDOWN:
        if input_active_x:
            if event.key == pygame.K_BACKSPACE:
                x_tiles = x_tiles[:-1]
            else:
                x_tiles += event.unicode
        elif input_active_y:
            if event.key == pygame.K_BACKSPACE:
                y_tiles = y_tiles[:-1]
            else:
                y_tiles += event.unicode


def handle_settings_menu_events():
    global mouse_pos, display_resolution, fullscreen, menu, settings, screen, arena, movement, screens

    dis_res_changed = False

    if fullscreen_rect.collidepoint(mouse_pos):
        click_sound.play()
        display_resolution = fullscreen_res
        fullscreen = True
        dis_res_changed = True
    elif back_rect.collidepoint(mouse_pos):
        click_sound.play()
        menu = True
        settings = False

    for i, res_rect in enumerate(resolution_rects):
        if res_rect.collidepoint(mouse_pos):
            click_sound.play()
            display_resolution = available_resolutions[i]
            fullscreen = False
            dis_res_changed = True
            break

    if dis_res_changed:
        if fullscreen:
            screen = pygame.display.set_mode(display_resolution, pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(display_resolution)
        screens = Screens(pygame)
        arena = Arena(map_name, pygame)
        movement = Movement(arena.tile_size / 120.0)
        recalculate_robot_values()


def handle_start_game_menu_events():
    global player_count, robots, jump, start_game, playing

    robot1 = Robot(
        arena.spawn_positions[0][0] + robot_radius,
        arena.spawn_positions[0][1] + robot_radius,
        robot_radius,
        0,
        arena.tile_size / 50.0,
        arena.tile_size / 50.0,
        arena.tile_size / 10.0,
        100,
        "blue",
        0,
    )
    robot2 = Robot(
        arena.spawn_positions[1][0] + robot_radius,
        arena.spawn_positions[1][1] + robot_radius,
        robot_radius,
        0,
        arena.tile_size / 50.0,
        arena.tile_size / 50.0,
        arena.tile_size / 10.0,
        100,
        "red",
        1,
    )
    robot3 = Robot(
        arena.spawn_positions[2][0] + robot_radius,
        arena.spawn_positions[2][1] + robot_radius,
        robot_radius,
        0,
        arena.tile_size / 50.0,
        arena.tile_size / 50.0,
        arena.tile_size / 10.0,
        100,
        "green",
        2,
    )
    robot4 = Robot(
        arena.spawn_positions[3][0] + robot_radius,
        arena.spawn_positions[3][1] + robot_radius,
        robot_radius,
        0,
        arena.tile_size / 50.0,
        arena.tile_size / 50.0,
        arena.tile_size / 10.0,
        100,
        "yellow",
        3,
    )

    if one_player_rect.collidepoint(mouse_pos):
        #click_sound.play()
        player_count = 1
        robots = [robot1]
    elif two_player_rect.collidepoint(mouse_pos):
        #click_sound.play()
        player_count = 2
        robots = [robot1, robot2]
        jump = [False]
    elif three_player_rect.collidepoint(mouse_pos):
        #click_sound.play()
        player_count = 3
        robots = [robot1, robot2, robot3]
        jump = [False, False]
    elif four_player_rect.collidepoint(mouse_pos):
        #click_sound.play()
        player_count = 4
        robots = [robot1, robot2, robot3, robot4]
        jump = [False, False, False]
    if robots:
        start_game = False
        playing = True


def handle_death_screen_events():
    global menu, death

    if main_menu_rect.collidepoint(mouse_pos):
        click_sound.play()
        menu = True
        death = False
    elif quit_rect.collidepoint(mouse_pos):
        click_sound.play()
        pygame.quit()
        sys.exit()


def handle_pause_screen_events():
    global game_paused, menu, playing

    if resume_rect.collidepoint(mouse_pos):
        click_sound.play()
        game_paused = False
    elif main_menu_rect.collidepoint(mouse_pos):
        click_sound.play()
        menu = True
        playing = False
        game_paused = False
    elif quit_rect.collidepoint(mouse_pos):
        click_sound.play()
        pygame.quit()
        sys.exit()


def handle_map_screen_events():
    global map, start_game, arena, map_name, movement

    for i, level_rect in enumerate(level_rects):
        if level_rect.collidepoint(mouse_pos):
            click_sound.play()
            map_name = maps[i]
            arena = Arena(map_name, pygame)
            recalculate_robot_values()
            movement = Movement(arena.tile_size / 120.0)
            map = False
            start_game = True
            break


def game_loop():
    global player_robot, playing, death, frame_count, force

    screen.fill(white)
    arena.paint_arena(screen)
    frame_count += 1
    player_robot = robots[0]
    # Handling of player robot
    player_robot_handling(player_robot)
    # Handling of bots
    bots_handling()


def bots_handling():
    global frame_count

    # Setup bots random movement
    if frame_count >= change_direction_interval:
        for i in range(1, len(robots)):
            # Zufällige Änderungen der Beschleunigung und der Drehgeschwindigkeit
            robots[i].change_acceleration(robots[i].accel + random.uniform(-1, 1))
            # Setze den Zähler zurück
            frame_count = 0
            jump[i - 1] = random.choice([True, False])
    # Move and paint bots
    for i in range(1, len(robots)):
        robots[i].change_velocity_cap(robots[i].vel + robots[i].accel)
        robots[i].decrease_hit_cooldown()
        if robots[i].vel < 0:
            robots[i].change_acceleration(robots[i].accel + arena.map_size[0] / 40000)
            if robots[i].vel + robots[i].accel >= 0:
                robots[i].change_velocity_cap(0)
                robots[i].change_acceleration(0)
        elif robots[i].vel > 0:
            robots[i].change_acceleration(robots[i].accel - arena.map_size[0] / 40000)
            if robots[i].vel + robots[i].accel <= 0:
                robots[i].change_velocity_cap(0)
                robots[i].change_acceleration(0)
        else:
            robots[i].change_acceleration(0)
        # Bewegung des Roboters
        movement.move_bot(
            robots[i], display_resolution[1], display_resolution[0], robots[i].vel, arena, jump[i - 1], dt
        )
        jump[i - 1] = False
        robots[i].paint_robot(pygame, screen, direction_left)


def player_robot_handling(player_robot):
    global playing, death, direction_left

    # Überprüfen, ob player die seitlichen Grenzen der Arena erreicht hat
    if player_robot.posx + player_robot.radius - arena.x_offset < 0:
        player_robot.health = 0
    elif player_robot.posx - player_robot.radius + arena.x_offset > display_resolution[0]:
        player_robot.health = 0
    # Überprüfen, ob player die oberen und unteren Grenzen der Arena erreicht hat
    if player_robot.posy + player_robot.radius < arena.y_offset:
        player_robot.health = 0
    elif player_robot.posy - player_robot.radius > display_resolution[1] - arena.y_offset:
        player_robot.health = 0
    # Check if player is dead:
    if player_robot.health <= 0:
        playing = False
        death = True
        death_sound.play()
    # attack will stay for a certain duration
    if player_robot.melee_cd < 30 and player_robot.melee_cd != 0:
        player_robot.melee_attack(pygame, screen, robots, arena)
        player_robot.melee_cd += 1
    # Player melee attack cooldown
    elif player_robot.melee_cd != 0:
        if player_robot.melee_cd == 30:
            fight_sound.play()
        if player_robot.melee_cd == 60:
            player_robot.melee_cd = 0
            #fight_sound.play()
        else:
            player_robot.melee_cd += 1
    # second ranged attack at ranged_cd == 10
    if player_robot.ranged_cd < 11 and player_robot.ranged_cd != 0:
        player_robot.ranged_attack()
        player_robot.ranged_cd += 1
    # Player ranged attack cooldown
    elif player_robot.ranged_cd != 0:
        if player_robot.ranged_cd == 60:
            player_robot.ranged_cd = 0
        else:
            player_robot.ranged_cd += 1

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_robot.change_acceleration(player_robot.accel - arena.tile_size / 1000.0)
        player_robot.change_alpha(180)
        direction_left = True
        #footsteps_sound.play()
    elif keys[pygame.K_RIGHT]:
        player_robot.change_acceleration(player_robot.accel + arena.tile_size / 1000.0)
        player_robot.change_alpha(0)
        direction_left = False
        #footsteps_sound.play()
    elif keys[pygame.K_DOWN]:
        player_robot.change_alpha(90)
    elif keys[pygame.K_UP]:
        player_robot.change_alpha(270)
    else:
        if player_robot.vel < 0:
            player_robot.change_acceleration(player_robot.accel + arena.tile_size / 2000.0)
            if player_robot.vel + player_robot.accel >= 0:
                player_robot.change_velocity_cap(0)
                player_robot.change_acceleration(0)
        elif player_robot.vel > 0:
            player_robot.change_acceleration(player_robot.accel - arena.tile_size / 2000.0)
            if player_robot.vel + player_robot.accel <= 0:
                player_robot.change_velocity_cap(0)
                player_robot.change_acceleration(0)
        else:
            player_robot.change_acceleration(0)
    player_robot.change_velocity_cap(player_robot.vel + player_robot.accel)
    movement.move_robot(player_robot, player_robot.vel, arena, dt)
    player_robot.paint_robot(pygame, screen, direction_left)
    player_robot.ranged_hit_reg(robots, display_resolution[1], display_resolution[0], arena)



while run:
    pygame.time.delay(0)
    dt = clock.tick(120)

    current_window_pos = window.position
    if playing:
        if current_window_pos != initial_window_pos:
            game_paused = True
    initial_window_pos = current_window_pos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if not playing:
                if menu:
                    click_sound.play()
                    handle_main_menu_events()
                elif build_arena:
                    click_sound.play()
                    handle_build_arena_menu_events(event)
                elif settings:
                    click_sound.play()
                    handle_settings_menu_events()
                elif start_game:
                    click_sound.play()
                    handle_start_game_menu_events()
                elif death:
                    handle_death_screen_events()
                elif map:
                    handle_map_screen_events()
            elif game_paused:
                handle_pause_screen_events()

        elif event.type == pygame.KEYDOWN:
            if playing and not game_paused:
                key = event.key
                player_robot = robots[0]
                if key == pygame.K_ESCAPE:
                    game_paused = True
                elif (
                    key == pygame.K_g and player_robot.melee_cd == 0
                ):  # we can attack if we have no cooldown and press the button
                    player_robot.melee_attack(pygame, screen, robots, arena)
                    player_robot.melee_cd += 1
                elif key == pygame.K_r and (player_robot.ranged_cd == 0 or player_robot.ranged_cd == 10):
                    player_robot.ranged_cd += 1
                elif key == pygame.K_f:
                    player_robot.take_damage_debug(10)
                elif key == pygame.K_SPACE:
                    jumping_sound.play()
                    if player_robot.jump_counter <= 1:
                        player_robot.jump = True
            elif build_arena:
                handle_build_arena_menu_events(event)

    if playing and not game_paused:
        game_loop()
    # Painting the screens:
    elif game_paused:
        resume_rect, quit_rect, main_menu_rect = screens.pause_screen(pygame, screen)
    elif death:
        quit_rect, main_menu_rect = screens.death_screen(pygame, screen)
    elif menu:
        play_rect, build_arena_rect, exit_rect, settings_rect = screens.main_menu(pygame, screen)
    elif settings:
        resolution_rects, fullscreen_rect, back_rect = screens.settings_menu(pygame, screen, available_resolutions)
    elif build_arena:
        input_rect_x_tiles, input_rect_y_tiles, start_building_rect = screens.build_arena_menu(
            pygame, screen, x_tiles, y_tiles
        )
    elif start_game:
        one_player_rect, two_player_rect, three_player_rect, four_player_rect = screens.start_screen(pygame, screen)
    elif map:
        level_rects, maps = screens.level_menu(pygame, screen, get_json_filenames(arena.maps_base_path))

    pygame.display.update()


pygame.quit()
