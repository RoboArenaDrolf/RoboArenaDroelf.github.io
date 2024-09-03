import os
import pygame
from pygame._sdl2.video import Window
from screeninfo import get_monitors
import sys

from movement import Movement
from arena import Arena
from arenaBuilder import ArenaBuilder
from screens import Screens
from robot import Robot

pygame.init()
pygame.joystick.init()

# Controller initialisieren
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"Joystick {i}: {joystick.get_name()} initialized.")

display_resolution = (720, 720)
available_resolutions = [(720, 720), (1280, 720), (1280, 1080), (1920, 1080)]
monitor = get_monitors()[0]
fullscreen_res = (monitor.width, monitor.height)
fullscreen = False
mouse_visibility_counter = 0
mouse_visible = True
framerate = 120

screen = pygame.display.set_mode(display_resolution)
pygame.display.set_caption("Robo Arena")

white = (255, 255, 255)

map_filename = "secondMap.json"
maps = []
arena = Arena(map_filename, pygame)
movement = Movement(arena.tile_size / 120.0)

robot_radius = arena.tile_size * 0.5

game_paused = False
run = True
start_game = False
menu = True
build_arena = False
settings = False
playing = False
map = False
robots = []
use_controller = False
single_player = False
death = False
win = False

input_active_x = False
input_active_y = False
x_tiles = ""
y_tiles = ""
menu_items = []
selected_item_index = 0
recently_switched_item = False

# Initiale Fensterposition
window = Window.from_display_module()
initial_window_pos = window.position

clock = pygame.time.Clock()

pygame.mixer.init()
jumping_sound = pygame.mixer.Sound("../Sounds/jumping.mp3")
jumping_sound.set_volume(0.7)
death_sound = pygame.mixer.Sound("../Sounds/death.mp3")
death_sound.set_volume(0.7)
footsteps_sound = pygame.mixer.Sound("../Sounds/footsteps.mp3")
click_sound = pygame.mixer.Sound("../Sounds/click.mp3")
music = pygame.mixer.Sound("../Sounds/music.mp3")
heavy_sword_sound = pygame.mixer.Sound("../Sounds/heavy_sword.mp3")
heavy_sword_sound.set_volume(0.5)
laser_sound = pygame.mixer.Sound("../Sounds/laser.mp3")
laser_sound.set_volume(0.5)

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


def update_maps(map_names):
    global maps
    for name in map_names:
        maps.append(name + ".json")


map_names = get_json_filenames(arena.maps_base_path)
update_maps(map_names)
screens = Screens(pygame, available_resolutions, map_names)


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


def reset_selected_item():
    global selected_item_index
    menu_items[selected_item_index].selected = False
    selected_item_index = 0


def handle_main_menu_events():
    global robots, map, menu, build_arena, settings, run, use_controller

    if play_item.pressed:
        click_sound.play()
        robots = []
        map = True
        menu = False
    elif build_arena_item.pressed:
        click_sound.play()
        build_arena = True
        menu = False
        reset_selected_item()
    elif settings_item.pressed:
        click_sound.play()
        settings = True
        menu = False
        reset_selected_item()
    elif exit_item.pressed:
        click_sound.play()
        run = False


def handle_build_arena_menu_events(event):
    global input_active_x, input_active_y, build_arena, menu, x_tiles, y_tiles, screens

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        if input_rect_x_tiles.collidepoint(mouse_pos):
            input_active_x = True
            input_active_y = False
        elif input_rect_y_tiles.collidepoint(mouse_pos):
            input_active_y = True
            input_active_x = False
        elif start_building_item.pressed:
            try:
                num_x = int(x_tiles)
                num_y = int(y_tiles)
                if num_x <= 0 or num_y <= 0:
                    raise ValueError
                build_arena = False
                menu = True
                arenaBuilder = ArenaBuilder(num_x, num_y, pygame)
                arenaBuilder.main()
                map_names = get_json_filenames(arena.maps_base_path)
                update_maps(map_names)
                screens = Screens(pygame, available_resolutions, map_names)
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
    global display_resolution, fullscreen, menu, settings, screen, arena, movement, screens, use_controller

    dis_res_changed = False

    if controller_on_off_item.pressed:
        click_sound.play()
        use_controller = not use_controller
    elif fullscreen_item.pressed:
        click_sound.play()
        display_resolution = fullscreen_res
        fullscreen = True
        dis_res_changed = True
    elif back_item.pressed:
        click_sound.play()
        menu = True
        settings = False
        reset_selected_item()

    for i, res_item in enumerate(resolution_items):
        if res_item.pressed:
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
        screens = Screens(pygame, available_resolutions, get_json_filenames(arena.maps_base_path))
        arena = Arena(map_filename, pygame)
        movement = Movement(arena.tile_size / 120.0)
        recalculate_robot_values()


def handle_start_game_menu_events():
    global robots, start_game, playing, single_player

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

    if one_player_item.pressed:
        click_sound.play()
        robots = [robot1]
        single_player = True
    elif two_player_item.pressed:
        click_sound.play()
        robots = [robot1, robot2]
        single_player = False
    elif three_player_item.pressed:
        click_sound.play()
        robots = [robot1, robot2, robot3]
        single_player = False
    elif four_player_item.pressed:
        click_sound.play()
        robots = [robot1, robot2, robot3, robot4]
        single_player = False
    if robots:
        start_game = False
        reset_selected_item()
        playing = True
        # print("purging")
        # when we start a new round delete all projectiles that may still exist
        robot1.reset_projectiles()
        robot2.reset_projectiles()
        robot3.reset_projectiles()
        robot4.reset_projectiles()


def handle_death_or_win_screen_events():
    global menu, death, win
    if main_menu_item.pressed:
        click_sound.play()
        menu = True
        death = False
        win = False
    elif quit_item.pressed:
        click_sound.play()
        pygame.quit()
        sys.exit()


def handle_pause_screen_events():
    global game_paused, menu, playing

    if resume_item.pressed:
        click_sound.play()
        game_paused = False
    elif main_menu_item.pressed:
        click_sound.play()
        menu = True
        playing = False
        game_paused = False
        reset_selected_item()
    elif quit_item.pressed:
        click_sound.play()
        pygame.quit()
        sys.exit()


def handle_map_screen_events():
    global map, start_game, arena, map_filename

    for i, level_item in enumerate(level_items):
        if level_item.pressed:
            click_sound.play()
            map_filename = maps[i]
            arena = Arena(map_filename, pygame)
            recalculate_robot_values()
            map = False
            start_game = True
            reset_selected_item()
            break


def game_loop():
    global player_robot, frame_count, win, playing

    screen.fill(white)
    arena.paint_arena(screen)
    # Handling of player robot
    for player_robot in robots:
        robot_handling(player_robot)
        player_robot.decrease_hit_cooldown()
    # moved hit_reg here since it only should be done once
    robots[0].ranged_hit_reg(pygame, screen, robots, arena)
    # Multiplayer: Check if only one is left
    if not single_player and len(robots) == 1:
        win = True
        playing = False


def robot_handling(robot):
    # Execute attacks
    robot_attacks(robot)
    # Robot movement
    robot_movement(robot)
    # Robot rendering
    robot.paint_robot(pygame, screen)
    # Check if robot dies
    check_robot_death(robot)


def robot_movement(robot):
    moved = False
    if use_controller and joysticks:
        if robot.player_number < len(joysticks):
            joystick = joysticks[robot.player_number]
            moved = move_robot_controller(robot, joystick)
    else:
        if robot.player_number == 0:
            keys = pygame.key.get_pressed()
            moved = move_robot_keys(robot, keys)
    if not moved:
        if robot.vel < 0:
            if robot.tile_below == 2:
                robot.change_acceleration(robot.accel + (arena.tile_size / 2000.0) / 2)
            else:
                robot.change_acceleration(robot.accel + arena.tile_size / 2000.0)
            if robot.vel + robot.accel >= 0:
                robot.change_velocity_cap(0)
                robot.change_acceleration(0)
        elif robot.vel > 0:
            if robot.tile_below == 2:
                robot.change_acceleration(robot.accel - (arena.tile_size / 2000.0) / 2)
            else:
                robot.change_acceleration(robot.accel - arena.tile_size / 2000.0)
            if robot.vel + robot.accel <= 0:
                robot.change_velocity_cap(0)
                robot.change_acceleration(0)
        else:
            robot.change_acceleration(0)
    if robot.tile_below == 3:  # if we stand on sand
        robot.change_velocity_cap_lower(robot.vel + robot.accel, robot.vel_max / 2)
        # we can at best move half as fast as on a normal tile
    else:
        robot.change_velocity_cap(robot.vel + robot.accel)
    movement.move_robot(robot, robot.vel, arena, dt)


def robot_attacks(robot):
    # Player melee attack cooldown
    if robot.melee_cd != 0 and robot.light_attack:
        if robot.melee_cd == 60:  # reset cooldown     
            robot.melee_cd = 0
        elif robot.melee_cd < 30:  # attack will stay for a certain duration
            robot.melee_attack(pygame, screen, robots, arena, "light")
            robot.melee_cd += 1
        else:
            robot.melee_cd += 1
    elif robot.melee_cd != 0 and robot.heavy_attack:
        if robot.melee_cd == 120:  # reset cooldown
            robot.melee_cd = 0
        elif robot.melee_cd <= 60:  # attack will stay for a certain duration
            robot.melee_attack(pygame, screen, robots, arena, "heavy")
            robot.melee_cd += 1
        else:
            robot.no_move = False  # after 60 Frames, attack is finished , we are allowed to move again
            robot.melee_cd += 1
    elif robot.melee_cd != 0 and robot.flame_attack:
        if robot.melee_cd == 180:  # reset cooldown
            robot.melee_cd = 0
        elif 5 < robot.melee_cd < 60:  # attack will stay for a certain duration
            robot.melee_attack(pygame, screen, robots, arena, "flame")
            robot.melee_cd += 1
        else:
            robot.melee_cd += 1
    elif robot.melee_cd != 0 and robot.stab_attack:
        if robot.melee_cd == 40:  # reset cooldown
            robot.melee_cd = 0
        elif robot.melee_cd < 40:  # attack will stay for a certain duration
            robot.melee_attack(pygame, screen, robots, arena, "stab")
            robot.melee_cd += 1
        else:
            robot.melee_cd += 1
    # Player ranged attack cooldown
    if robot.ranged_cd != 0 and (not robot.ranged_explodes and not robot.ranged_bounces and not robot.ranged_laser):
        if robot.ranged_cd == 60:
            robot.ranged_cd = 0
        elif robot.ranged_cd <= 10:  # second ranged attack at ranged_cd == 10
            robot.ranged_attack(screen, robots, arena, "normal")
            robot.ranged_cd += 1
        else:
            robot.ranged_cd += 1
    elif robot.ranged_cd != 0 and robot.ranged_explodes:
        if robot.ranged_cd == 120:
            robot.ranged_cd = 0
        else:
            robot.ranged_cd += 1
    elif player_robot.ranged_cd != 0 and robot.ranged_bounces:
        if player_robot.ranged_cd == 60:
            player_robot.ranged_cd = 0
        else:
            player_robot.ranged_cd += 1
    elif robot.ranged_cd != 0 and robot.ranged_laser:
        if robot.ranged_cd == 240:  # long cooldown
            robot.ranged_cd = 0
        elif robot.ranged_cd <= 30:  # laser stays until ranged_cd == 30
            robot.ranged_attack(screen, robots, arena, "laser")
            robot.ranged_cd += 1
        else:
            robot.ranged_cd += 1
    robot.handle_explosions(screen, arena, robots)


def check_robot_death(robot):
    global playing, death
    # Überprüfen, ob player die seitlichen Grenzen der Arena erreicht hat
    if robot.posx + robot.radius - arena.x_offset < 0:
        robot.health = 0
    elif robot.posx - robot.radius + arena.x_offset > display_resolution[0]:
        robot.health = 0
    # Überprüfen, ob player die oberen und unteren Grenzen der Arena erreicht hat
    if robot.posy + robot.radius < arena.y_offset:
        robot.health = 0
    elif robot.posy - robot.radius > display_resolution[1] - arena.y_offset:
        robot.health = 0
    # Check if player is dead:
    if robot.health <= 0:
        death_sound.play()
        if single_player:
            death = True
            playing = False
        else:
            robots.remove(robot)


def move_robot_keys(robot, keys):
    if keys[pygame.K_LEFT] and (not robot.no_move):
        if robot.tile_below == 2:  # if we stand on ice
            robot.change_acceleration(robot.accel - (arena.tile_size / 1000.0) / 2)
            # we accelerate half as fast as normal
        else:
            robot.change_acceleration(robot.accel - arena.tile_size / 1000.0)
        robot.change_alpha(180)
        robot.direction_left = True
    elif keys[pygame.K_RIGHT] and (not robot.no_move):
        if robot.tile_below == 2:  # if we stand on ice
            robot.change_acceleration(robot.accel + (arena.tile_size / 1000.0) / 2)
            # we accelerate half as fast as normal
        else:
            robot.change_acceleration(robot.accel + arena.tile_size / 1000.0)
        robot.change_alpha(0)
        robot.direction_left = False
    elif keys[pygame.K_DOWN] and (not robot.no_move):
        robot.change_alpha(90)
        return False
    elif keys[pygame.K_UP] and (not robot.no_move):
        robot.change_alpha(270)
        return False
    else:
        return False
    return True


def move_robot_controller(robot, joystick):
    value_x = joystick.get_axis(0)
    value_y = joystick.get_axis(1)
    if value_x < -0.2 and (not robot.no_move):
        if robot.tile_below == 2:  # if we stand on ice
            robot.change_acceleration(robot.accel - (arena.tile_size / 1000.0) / 2)
            # we accelerate half as fast as normal
        else:
            robot.change_acceleration(robot.accel - arena.tile_size / 1000.0)
        robot.change_alpha(180)
        robot.direction_left = True
    elif value_x > 0.2 and (not robot.no_move):
        if robot.tile_below == 2:  # if we stand on ice
            robot.change_acceleration(robot.accel + (arena.tile_size / 1000.0) / 2)
            # we accelerate half as fast as normal
        else:
            robot.change_acceleration(robot.accel + arena.tile_size / 1000.0)
        robot.change_alpha(0)
        robot.direction_left = False
    elif value_y > 0.2 and (not robot.no_move):
        robot.change_alpha(90)
        return False
    elif value_y < -0.2 and (not robot.no_move):
        robot.change_alpha(270)
        return False
    else:
        return False
    return True


def keydown_handling(event):
    global game_paused
    if playing and not game_paused:
        player_robot = robots[0]
        key = event.key
        if key == pygame.K_ESCAPE:
            game_paused = True
        elif (
                key == pygame.K_g and player_robot.melee_cd == 0
        ):  # we can attack if we have no cooldown and press the button
            player_robot.melee_attack(pygame, screen, robots, arena, "light")
            player_robot.melee_cd += 1
        elif (
                key == pygame.K_h and player_robot.melee_cd == 0
        ):  # we can attack if we have no cooldown and press the button
            heavy_sword_sound.play()
            player_robot.melee_attack(pygame, screen, robots, arena, "heavy")
            player_robot.no_move = True  # charge attack no moving allowed
            player_robot.melee_cd += 1
        elif key == pygame.K_r and player_robot.ranged_cd == 0:
            player_robot.ranged_attack(screen, robots, arena, "normal")
            player_robot.ranged_cd += 1
        elif key == pygame.K_t and player_robot.ranged_cd == 0:
            player_robot.ranged_attack(screen, robots, arena, "explosive")
            player_robot.ranged_cd += 1
        elif key == pygame.K_z and player_robot.ranged_cd == 0:
            player_robot.ranged_attack(screen, robots, arena, "bouncy")
            player_robot.ranged_cd += 1
        elif key == pygame.K_k and player_robot.melee_cd == 0:
            player_robot.melee_attack(pygame, screen, robots, arena, "flame")
            player_robot.melee_cd += 1
        elif key == pygame.K_u and player_robot.ranged_cd == 0:
            laser_sound.play()
            player_robot.ranged_attack(screen, robots, arena, "laser")
            player_robot.ranged_cd += 1
        elif key == pygame.K_j and player_robot.melee_cd == 0:
            player_robot.melee_attack(pygame, screen, robots, arena, "stab")
            player_robot.melee_cd += 1
        elif key == pygame.K_f:
            player_robot.take_damage_debug(10)
        elif key == pygame.K_SPACE and (not player_robot.no_move):
            jumping_sound.play()
            if player_robot.jump_counter <= 1:
                player_robot.jump = True
    elif build_arena:
        handle_build_arena_menu_events(event)


def joybuttons_handling(event):
    global game_paused
    if playing and not game_paused:
        joystick_id = event.instance_id
        if joystick_id < len(robots):
            player_robot = robots[joystick_id]
            if event.button == 0:
                if player_robot.jump_counter <= 1:
                    player_robot.jump = True
            elif event.button == 7:
                game_paused = True
    else:
        if event.button == 1:
            menu_items[selected_item_index].pressed = True
        if start_game:
            handle_start_game_menu_events()


def joyaxis_handling(event):
    global selected_item_index, recently_switched_item
    if playing and not game_paused:
        joystick_id = event.instance_id
        if joystick_id < len(robots):
            player_robot = robots[joystick_id]
            if (
                    event.axis == 5 and event.value > 0.2 and player_robot.melee_cd == 0
            ):  # we can attack if we have no cooldown and press the button
                player_robot.melee_attack(pygame, screen, robots, arena, "light")
                player_robot.melee_cd += 1
            if event.axis == 4 and event.value > 0.2 and (player_robot.ranged_cd == 0 or player_robot.ranged_cd == 10):
                player_robot.ranged_attack(screen, robots, arena, "normal")
                player_robot.ranged_cd += 1
    else:
        if event.axis == 1:
            if event.value > 0.2 and not recently_switched_item:
                menu_items[selected_item_index].selected = False
                selected_item_index += 1
                if selected_item_index >= len(menu_items):
                    selected_item_index = 0
                recently_switched_item = True
            elif event.value < -0.2 and not recently_switched_item:
                menu_items[selected_item_index].selected = False
                selected_item_index -= 1
                if selected_item_index < 0:
                    selected_item_index = len(menu_items) - 1
                recently_switched_item = True
            elif -0.2 <= event.value <= 0.2:
                recently_switched_item = False


def mouse_handling():
    mouse_pos = pygame.mouse.get_pos()
    if not playing or game_paused:
        for item in menu_items:
            if item.rect.collidepoint(mouse_pos):
                item.pressed = True
        if build_arena:
            handle_build_arena_menu_events(event)
        elif start_game:
            handle_start_game_menu_events()


def screens_painting():
    global menu_items, resume_item, main_menu_item, quit_item, play_item, build_arena_item, \
        settings_item, exit_item, controller_on_off_item, resolution_items, fullscreen_item, back_item, \
        input_rect_x_tiles, input_rect_y_tiles, start_building_item, one_player_item, two_player_item, \
        three_player_item, four_player_item, level_items

    if game_paused:
        menu_items = screens.pause_screen(pygame, screen)
        resume_item, main_menu_item, quit_item = menu_items[0], menu_items[1], menu_items[2]
        handle_pause_screen_events()
    elif death:
        menu_items = screens.death_screen(pygame, screen)
        main_menu_item, quit_item = menu_items[0], menu_items[1]
        handle_death_or_win_screen_events()
    elif win:
        menu_items = screens.win_screen(pygame, screen, robots[0])
        main_menu_item, quit_item = menu_items[0], menu_items[1]
        handle_death_or_win_screen_events()
    elif menu:
        menu_items = screens.main_menu_screen(pygame, screen)
        play_item, build_arena_item, settings_item, exit_item = (
            menu_items[0],
            menu_items[1],
            menu_items[2],
            menu_items[3],
        )
        handle_main_menu_events()
    elif settings:
        menu_items = screens.settings_screen(pygame, screen)
        controller_on_off_item = menu_items[0]
        resolution_items = []
        for i in range(1, 5):
            resolution_items.append(menu_items[i])
        fullscreen_item, back_item = menu_items[5], menu_items[6]
        handle_settings_menu_events()
    elif build_arena:
        input_rect_x_tiles, input_rect_y_tiles, menu_items = screens.build_arena_screen(
            pygame, screen, x_tiles, y_tiles
        )
        start_building_item = menu_items[0]
    elif start_game:
        menu_items = screens.start_screen(pygame, screen)
        one_player_item, two_player_item, three_player_item, four_player_item = (
            menu_items[0],
            menu_items[1],
            menu_items[2],
            menu_items[3],
        )
    elif map:
        menu_items = screens.maps_screen(pygame, screen)
        level_items = menu_items
        handle_map_screen_events()


def item_selections():
    global selected_item_index
    # Check mouse pos and select menu items
    if not use_controller:
        mouse_pos = pygame.mouse.get_pos()
        for i, item in enumerate(menu_items):
            if item.rect.collidepoint(mouse_pos):
                selected_item_index = i
                item.selected = True
            else:
                item.selected = False
    # If using controller: Check selected item index and set it to True
    else:
        menu_items[selected_item_index].selected = True
    # Reset pressed items
    for item in menu_items:
        item.pressed = False


##################################
# MAIN LOOP
##################################
while run:
    pygame.time.delay(0)
    dt = clock.tick(framerate)

    if mouse_visible:
        mouse_visibility_counter += 1
        if mouse_visibility_counter >= 2 * framerate:
            mouse_visible = False
            pygame.mouse.set_visible(False)

    # Bugfix for bug with changing window position mid-game
    current_window_pos = window.position
    if playing:
        if current_window_pos != initial_window_pos:
            game_paused = True
    initial_window_pos = current_window_pos

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_handling()
        elif not mouse_visible and event.type == pygame.MOUSEMOTION:
            pygame.mouse.set_visible(True)
            mouse_visible = True
            mouse_visibility_counter = 0
        else:
            if use_controller:
                if event.type == pygame.JOYBUTTONDOWN:
                    joybuttons_handling(event)
                elif event.type == pygame.JOYAXISMOTION:
                    joyaxis_handling(event)
            else:
                if event.type == pygame.KEYDOWN:
                    keydown_handling(event)

    if playing and not game_paused:
        game_loop()
    # Painting the screens:
    else:
        screens_painting()
        item_selections()

    pygame.display.update()

pygame.quit()
