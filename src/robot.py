import math
import pygame

from src.projectiles import Projectile
from src.explosions import Explosion


class Robot:
    posx: int
    posy: int
    radius = 0
    alpha = 0
    accel = float(0)
    accel_alpha = float(0)
    vel = float(0)
    vel_alpha = float(0)
    vertical_speed = float(0)
    health_max: int
    health: int
    color: str
    jump = False
    jump_counter = 0
    direction_left = False
    projectiles = []
    explosions = []
    melee_cd = 0
    ranged_cd = 0
    robots_base_path = "../Robots/"
    recoil_percent = 0.1
    hit_cooldown = 0
    i_frames: int
    attack_start: int
    attack_buffer: int
    ranged_normal: bool  # true = normal
    ranged_explodes: bool
    ranged_bounces: bool
    ranged_laser: bool
    light_attack: bool  # true = light
    heavy_attack: bool  # true = heavy
    stab_attack: bool
    flame_attack: bool
    no_move = False  # false = moving allowed true = moving not allowed, start with allowed movement
    fire_timer = int
    explosions = []
    laser_len: int
    flammen_len: int
    old_alpha = 0
    robot_type = 0
    light_melee: str
    heavy_melee: str
    light_ranged: str
    heavy_ranged: str

    tile_below: int
    # Normal/No effect = 0
    # Lava = 1
    # Ice = 2
    # Sand = 3

    def __init__(self, x, y, r, a, am, aam, vm, hm, c, pn):
        self.posx = x
        self.posy = y
        self.radius = r
        self.alpha = a % 360
        self.accel_max = am
        self.accel_alpha_max = aam
        self.vel_max = vm
        self.health_max = hm
        self.health = self.health_max
        self.color = c
        self.player_number = pn
        self.no_move = False

        self.first_robot = pygame.image.load(self.robots_base_path + "firstRobot.png")
        self.first_robot = pygame.transform.scale(self.first_robot, (self.radius * 2, self.radius * 2))
        self.first_robot_flipped = pygame.transform.flip(self.first_robot, True, False)
        self.second_robot = pygame.image.load(self.robots_base_path + "secondRobot.png")
        self.second_robot = pygame.transform.scale(self.second_robot, (self.radius * 2, self.radius * 2))
        self.second_robot_flipped = pygame.transform.flip(self.second_robot, True, False)
        self.third_robot = pygame.image.load(self.robots_base_path + "thirdRobot.png")
        self.third_robot = pygame.transform.scale(self.third_robot, (self.radius * 2, self.radius * 2))
        self.third_robot_flipped = pygame.transform.flip(self.third_robot, True, False)
        self.fourth_robot = pygame.image.load(self.robots_base_path + "fourthRobot.png")
        self.fourth_robot = pygame.transform.scale(self.fourth_robot, (self.radius * 2, self.radius * 2))
        self.fourth_robot_flipped = pygame.transform.flip(self.fourth_robot, True, False)

        self.tile_below = 0
        self.i_frames = 0
        self.fire_timer = 0

        self.kreissäge = pygame.image.load("../Animation/kreissäge.png")
        self.scaled_kreissäge = None
        self.schwert = pygame.image.load("../Animation/schwert.png")
        self.scaled_schwert = None
        self.flammen = pygame.image.load("../Animation/flammen.png")
        self.scaled_flammen = self.flammen
        self.extra_flammen = None
        self.heavy_sword = pygame.image.load("../Animation/massive_sword.png")
        self.scaled_heavy_sword = None
        self.explosion = pygame.image.load("../Animation/explosion.png")
        self.scaled_explosion = None

        self.kreissäge_sound = pygame.mixer.Sound("../Sounds/säge.mp3")
        self.kreissäge_sound.set_volume(0.45)
        self.fight_sound = pygame.mixer.Sound("../Sounds/fight.mp3")
        self.fight_sound.set_volume(0.7)
        self.shooting_sound = pygame.mixer.Sound("../Sounds/shooting.mp3")
        self.laser_sound = pygame.mixer.Sound("../Sounds/laser.mp3")
        self.missle_sound = pygame.mixer.Sound("../Sounds/missle.mp3")
        self.missle_sound.set_volume(0.45)
        self.explosion_sound = pygame.mixer.Sound("../Sounds/explosion.mp3")
        self.explosion_sound.set_volume(0.45)
        self.laser = pygame.image.load("../Animation/laser.png")
        self.scaled_laser = self.laser
        self.damage_sound = pygame.mixer.Sound("../Sounds/damage.mp3")
        self.damage_sound.set_volume(0.3)
        self.heavy_sword_sound = pygame.mixer.Sound("../Sounds/heavy_sword.mp3")
        self.heavy_sword_sound.set_volume(0.5)
        self.laser_sound = pygame.mixer.Sound("../Sounds/laser.mp3")
        self.laser_sound.set_volume(0.5)
        self.fire_sound = pygame.mixer.Sound("../Sounds/fire.mp3")
        self.fire_sound.set_volume(0.3)

    def change_acceleration(self, a):
        if abs(a) <= self.accel_max:
            self.accel = a
        else:
            if a < 0:
                self.accel = -self.accel_max
            else:
                self.accel = self.accel_max

    def change_rot_acceleration(self, aa):
        if abs(aa) < self.accel_alpha_max:
            self.accel_alpha = aa
        else:
            self.accel_alpha = self.accel_alpha_max

    def change_velocity(self, v):
        self.vel = v

    def change_alpha(self, a):
        self.alpha = a % 360

    def change_velocity_cap(self, v):
        if abs(v) < self.vel_max:
            self.vel = v
        else:
            if v < 0:
                self.vel = -self.vel_max
            else:
                self.vel = self.vel_max
        # self.alpha = 270 + (90 / self.vel_max) * self.vel

    def change_velocity_cap_lower(self, v, c):
        if c < self.vel_max:
            if abs(v) < c:
                self.vel = v
            else:
                if v < 0:
                    self.vel = -c
                else:
                    self.vel = c
        else:
            self.change_velocity_cap(v)

    def change_turn_velocity(self, va):
        self.vel = va

    def take_damage_debug(self, d, fire):
        if (
            self.i_frames == 0 and d != 0  # no i-frames we are allowed to take damage
        ):  # workarround for 0 damage projectiles to not add i-frames on hit
            if d <= self.health:
                self.health = self.health - d
                self.i_frames = 10
                self.apply_fire(fire)
            else:
                self.health = 0
        else:  # we have i-frames we cannot take damage
            pass

    def take_damage_force(self, d):
        #  here we do not care for i-frames we force the robot to take damage
        if d <= self.health:
            self.health = self.health - d
        else:
            self.health = 0

    def fire_damage(self):
        if self.fire_timer > 0:
            if self.fire_timer % 5 == 0:  # every 3 frames
                self.take_damage_force(1)  # take 1 damage from fire
                #  print(self.player_number, "you are burning", self.fire_timer)
            self.fire_timer -= 1  # reduce fire timer by 1

    def apply_fire(self, t):
        if t > 0:  # increase time on fire
            if self.fire_timer + t < 120:
                self.fire_timer = self.fire_timer + t
            else:
                self.fire_timer = 60  # maximum time a robot can be on fire
        else:  # decrease time on fire
            if self.fire_timer + t > 0:
                self.fire_timer = self.fire_timer + t
            else:
                self.fire_timer = 0  # minimum time is 0

    def melee_attack_old(self, pygame, screen, robots, arena):  # keep this for now -Björn
        new_x = self.radius * (math.cos(math.radians(self.alpha)))
        new_y = self.radius * (math.sin(math.radians(self.alpha)))
        line_start = (self.posx + new_x, self.posy + new_y)
        line_end = (self.posx + new_x * 2, self.posy + new_y * 2)
        pygame.draw.line(screen, "red", line_start, line_end, width=4)

        for i in range(1, len(robots)):
            # now I will use https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line:
            # Line defined by two points
            if (
                self.distance_from_segment(
                    line_start[0], line_start[1], line_end[0], line_end[1], robots[i].posx, robots[i].posy
                )
                <= robots[i].radius
            ):  # if the distance from this line to the center of a robot
                # is smaller than it's radius, we have a hit and that robot takes some damage
                robots[i].take_damage_debug(1, 0)
                if robots[i].hit_cooldown <= 0:
                    if self.alpha == 180:
                        direction = Projectile.Direction.LEFT
                    elif self.alpha == 0:
                        direction = Projectile.Direction.RIGHT
                    elif self.alpha == 270:
                        direction = Projectile.Direction.UP
                    else:
                        direction = Projectile.Direction.DOWN
                    self.recoil(arena, robots[i], direction, 0.05)

    def distance_from_segment(self, x1, y1, x2, y2, x3, y3):
        # Vektoren berechnen
        px, py = x2 - x1, y2 - y1
        norm = px * px + py * py
        if norm == 0:  # x1=x2, y1=y2 -> not a line, but a point
            # now we don't have a distance form a line to a point but from a point to another point
            distance = math.sqrt((x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1))
            return distance
        # Punkt auf die Linie projizieren
        u = ((x3 - x1) * px + (y3 - y1) * py) / norm

        # Überprüfen, ob die Projektion innerhalb der Strecke liegt
        if u < 0:
            # Nächster Punkt ist P1
            closest_x, closest_y = x1, y1
        elif u > 1:
            # Nächster Punkt ist P2
            closest_x, closest_y = x2, y2
        else:
            # Projektion auf die Strecke
            closest_x = x1 + u * px
            closest_y = y1 + u * py

        # Abstand zwischen P3 und dem nächstgelegenen Punkt berechnen
        dx, dy = x3 - closest_x, y3 - closest_y
        distance = math.sqrt(dx * dx + dy * dy)

        return distance

    def melee_attack(self, pygame, screen, robots, arena, type):
        if type == "heavy":
            self.heavy_attack = True
            self.light_attack = False
            self.flame_attack = False
            self.stab_attack = False

            self.no_move = True

            hit_box_height = 2 * self.radius
            hit_box_width = 2 * self.radius

            if 30 == self.melee_cd:
                self.heavy_sword_sound.play()

            if 30 <= self.melee_cd <= 60:
                hit_box_height = 2 * self.radius
                hit_box_width = 2 * self.radius
                if self.scaled_heavy_sword is None:
                    # Berechne die Länge der Linie
                    line_length = hit_box_width
                    # Skalieren der Kreissäge auf die Länge der Linie
                    original_width = self.heavy_sword.get_width()
                    original_height = self.heavy_sword.get_height()
                    scale_factor = line_length / original_width
                    self.scaled_heavy_sword = pygame.transform.scale(
                        self.heavy_sword, (int(line_length), int(original_height * scale_factor))
                    )
                if self.alpha == 0:  # right
                    rect_left_x = self.posx + 0.5 * hit_box_width
                    rect_top_y = self.posy - 0.5 * hit_box_height
                    heavy_sword_rotated = self.scaled_heavy_sword
                elif self.alpha == 90:  # down
                    rect_left_x = self.posx - 0.5 * hit_box_width
                    rect_top_y = self.posy + 0.5 * hit_box_height
                    heavy_sword_rotated = pygame.transform.rotate(self.scaled_heavy_sword, -90)
                elif self.alpha == 180:  # left
                    rect_left_x = self.posx - 1.5 * hit_box_height
                    rect_top_y = self.posy - 0.5 * hit_box_height
                    heavy_sword_rotated = pygame.transform.rotate(self.scaled_heavy_sword, -180)
                elif self.alpha == 270:  # up
                    rect_left_x = self.posx - 0.5 * hit_box_height
                    rect_top_y = self.posy - 1.5 * hit_box_height
                    heavy_sword_rotated = pygame.transform.rotate(self.scaled_heavy_sword, -270)
                else:  # failsafe
                    print("how did you do this? alpha=", self.alpha)

            if 30 <= self.melee_cd <= 60:
                hit_box = pygame.Rect(rect_left_x, rect_top_y, hit_box_width, hit_box_height)
                self.hit_reg_rect(robots, arena, hit_box, 10, self.player_number, 0, 0.1)
                screen.blit(heavy_sword_rotated, hit_box)

        elif type == "light":
            self.heavy_attack = False
            self.light_attack = True
            self.flame_attack = False
            self.stab_attack = False
            if self.melee_cd == 0:
                if self.alpha == 0:  # right
                    self.attack_start = 315
                elif self.alpha == 90:  # down
                    self.attack_start = 45
                elif self.alpha == 180:  # left
                    self.attack_start = 135
                elif self.alpha == 270:  # up
                    self.attack_start = 225
                else:  # failsafe
                    print("how did you do this? alpha=", self.alpha)

            new_x = self.radius * (math.cos(math.radians(self.attack_start)))
            new_y = self.radius * (math.sin(math.radians(self.attack_start)))
            line_start = (self.posx + new_x, self.posy + new_y)
            line_end = (self.posx + new_x * 2.5, self.posy + new_y * 2.5)
            line_center = ((line_start[0] + line_end[0]) // 2, (line_start[1] + line_end[1]) // 2)

            dx = line_end[0] - line_start[0]
            dy = line_end[1] - line_start[1]
            angle = math.degrees(math.atan2(dy, dx))

            if self.scaled_kreissäge is None:
                # Berechne die Länge der Linie
                line_length = math.hypot(dx, dy)

                # Skalieren der Kreissäge auf die Länge der Linie
                original_width = self.kreissäge.get_width()
                original_height = self.kreissäge.get_height()
                scale_factor = line_length / original_width
                self.scaled_kreissäge = pygame.transform.scale(
                    self.kreissäge, (int(line_length), int(original_height * scale_factor))
                )

            kreissäge_rotated = pygame.transform.rotate(self.scaled_kreissäge, -angle)
            kreissäge_rect = kreissäge_rotated.get_rect(center=line_center)

            if self.melee_cd == 0:
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.attack_buffer = 0
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.kreissäge_sound.play()
                screen.blit(kreissäge_rotated, kreissäge_rect)
            elif self.melee_cd % 5 == 0 and self.melee_cd <= 30:
                self.attack_start = (self.attack_start + 15) % 360
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.attack_buffer = 4
                screen.blit(kreissäge_rotated, kreissäge_rect)
            elif self.attack_buffer > 0:
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.attack_buffer -= 1
                screen.blit(kreissäge_rotated, kreissäge_rect)

        elif type == "stab":
            self.heavy_attack = False
            self.light_attack = False
            self.stab_attack = True
            self.flame_attack = False

            if self.melee_cd == 0:
                self.attack_start = self.alpha
            elif self.attack_buffer == 0:
                if self.melee_cd % 3 == 0:
                    self.attack_start = self.alpha
                elif self.melee_cd % 3 == 1:
                    self.attack_start = (self.alpha + 30) % 360
                else:
                    self.attack_start = (self.alpha - 30) % 360

            new_x = self.radius * (math.cos(math.radians(self.attack_start)))
            new_y = self.radius * (math.sin(math.radians(self.attack_start)))
            line_start = (self.posx + new_x, self.posy + new_y)
            line_end = (self.posx + new_x * 2.5, self.posy + new_y * 2.5)
            line_center = ((line_start[0] + line_end[0]) // 2, (line_start[1] + line_end[1]) // 2)

            dx = line_end[0] - line_start[0]
            dy = line_end[1] - line_start[1]
            angle = math.degrees(math.atan2(dy, dx))

            if self.scaled_schwert is None:
                # Berechne die Länge der Linie
                line_length = math.hypot(dx, dy)

                # Skalieren das Schwert auf die Länge der Linie
                original_width = self.schwert.get_width()
                original_height = self.schwert.get_height()
                scale_factor = line_length / original_width
                self.scaled_schwert = pygame.transform.scale(
                    self.schwert, (int(line_length), int(original_height * scale_factor))
                )

            schwert_rotated = pygame.transform.rotate(self.scaled_schwert, -angle)
            schwert_rect = schwert_rotated.get_rect(center=line_center)

            if self.melee_cd == 0:
                # pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.attack_buffer = 9
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.fight_sound.play()
                screen.blit(schwert_rotated, schwert_rect)
            elif self.attack_buffer == 0:
                # pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.attack_buffer = 9
                self.fight_sound.play()
                screen.blit(schwert_rotated, schwert_rect)
            elif self.attack_buffer > 5:
                # pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.attack_buffer -= 1
                screen.blit(schwert_rotated, schwert_rect)
            elif self.attack_buffer > 0:
                new_x = self.radius * (math.cos(math.radians(self.attack_start)))
                new_y = self.radius * (math.sin(math.radians(self.attack_start)))
                line_start = (self.posx + new_x - 15, self.posy + new_y - 13)
                line_end = (self.posx + new_x * 2.5 - 15, self.posy + new_y * 2.5 - 13)
                # pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 5, 0.05)
                self.attack_buffer -= 1
                screen.blit(schwert_rotated, schwert_rect)
        elif type == "flame":
            self.heavy_attack = False
            self.light_attack = False
            self.flame_attack = True
            self.stab_attack = False

            if self.melee_cd == 0:
                self.flammen_len = 0
                self.extra_flammen = None
                self.fire_sound.play()

            (len_x, len_y) = self.find_closest_block(screen, arena)  # x,y cords of nearest collision in front
            max_range = self.radius * 4  # this is the maximum range of the flames
            # calculate the rectangle based on viewing direction
            if self.alpha == 0:  # right
                hit_box_height = self.radius
                hit_box_width = min(abs(len_x - self.posx), max_range) - self.radius
                rect_left_x = self.posx + self.radius
                rect_top_y = self.posy - 0.5 * self.radius
                hit_box2_height = 2 * self.radius
                hit_box2_width = self.radius
                rect_left2_x = self.posx + self.radius + min(abs(len_x - self.posx), max_range) - self.radius
                rect_top2_y = self.posy - 1.5 * self.radius

            elif self.alpha == 90:  # down
                hit_box_height = min(abs(len_y - self.posy), max_range) - self.radius
                hit_box_width = self.radius
                rect_left_x = self.posx - 0.5 * self.radius
                rect_top_y = self.posy + self.radius
                hit_box2_height = self.radius
                hit_box2_width = 3 * self.radius
                rect_left2_x = self.posx - 1.5 * self.radius
                rect_top2_y = self.posy + self.radius + hit_box_height

            elif self.alpha == 180:  # left
                hit_box_height = self.radius
                hit_box_width = min(abs(len_x - self.posx), max_range) - self.radius
                rect_left_x = self.posx - self.radius - hit_box_width
                rect_top_y = self.posy - 0.5 * self.radius
                hit_box2_height = 2 * self.radius
                hit_box2_width = self.radius
                rect_left2_x = self.posx - self.radius - hit_box_width - self.radius
                rect_top2_y = self.posy - 1.5 * self.radius

            elif self.alpha == 270:  # up
                hit_box_height = min(abs(len_y - self.posy), max_range) - self.radius
                hit_box_width = self.radius
                rect_left_x = self.posx - 0.5 * self.radius
                rect_top_y = self.posy - self.radius - hit_box_height
                hit_box2_height = self.radius
                hit_box2_width = 3 * self.radius
                rect_left2_x = self.posx - 1.5 * self.radius
                rect_top2_y = self.posy - self.radius - hit_box_height - self.radius

            hit_box = pygame.Rect(rect_left_x, rect_top_y, hit_box_width, hit_box_height)
            hit_box2 = pygame.Rect(rect_left2_x, rect_top2_y, hit_box2_width, hit_box2_height)

            flammen_len = int(max(hit_box_width, hit_box_height))
            if self.old_alpha != self.alpha:
                self.old_alpha = self.alpha
                if hit_box_width > 0 and hit_box_height > 0:
                    flammen_rotated = pygame.transform.rotate(self.flammen, -self.alpha)
                    self.flammen_len = flammen_len
                    self.scaled_flammen = pygame.transform.scale(
                        flammen_rotated, (int(hit_box_width), int(hit_box_height))
                    )
                    screen.blit(self.scaled_flammen, hit_box)
                if hit_box2_width > 0 and hit_box2_height > 0:
                    if self.alpha == 0 or self.alpha == 180:
                        extra_flammen_rotated = pygame.transform.rotate(self.flammen, 90)
                    else:
                        extra_flammen_rotated = self.flammen
                    self.extra_flammen = pygame.transform.scale(
                        extra_flammen_rotated, (int(hit_box2_width), int(hit_box2_height))
                    )
                    screen.blit(self.extra_flammen, hit_box2)
            else:
                if hit_box_width > 0 and hit_box_height > 0:
                    if flammen_len * 1.3 < self.flammen_len or flammen_len * 0.7 > self.flammen_len:
                        flammen_rotated = pygame.transform.rotate(self.flammen, -self.alpha)
                        self.flammen_len = flammen_len
                        self.scaled_flammen = pygame.transform.scale(
                            flammen_rotated, (int(hit_box_width), int(hit_box_height))
                        )
                    screen.blit(self.scaled_flammen, hit_box)
                if hit_box2_width > 0 and hit_box2_height > 0:
                    if self.extra_flammen is None:
                        if self.alpha == 0 or self.alpha == 180:
                            extra_flammen_rotated = pygame.transform.rotate(self.flammen, 90)
                        else:
                            extra_flammen_rotated = self.flammen
                        self.extra_flammen = pygame.transform.scale(
                            extra_flammen_rotated, (int(hit_box2_width), int(hit_box2_height))
                        )
                    screen.blit(self.extra_flammen, hit_box2)

            # now we have the rectangle, so we draw it and calculate the hit_reg
            self.hit_reg_rect(robots, arena, hit_box, 4, self.player_number, 20, 0.05)
            self.hit_reg_rect(robots, arena, hit_box2, 2, self.player_number, 40, 0.05)

    def ranged_attack(self, screen, robots, arena, type):
        if self.ranged_cd == 0 or self.ranged_cd == 10:
            self.laser_len = 0
            r = self.radius / 4
            if self.alpha == 0:  # right
                xs = self.vel_max
                ys = 0
                x = self.posx + self.radius + r
                y = self.posy
            elif self.alpha == 90:  # down
                xs = 0
                ys = self.vel_max
                x = self.posx
                y = self.posy + self.radius + r
            elif self.alpha == 180:  # left
                xs = -self.vel_max
                ys = 0
                x = self.posx - self.radius - r
                y = self.posy
            elif self.alpha == 270:  # up
                xs = 0
                ys = -self.vel_max
                x = self.posx
                y = self.posy - self.radius - r
            else:  # failsafe
                print("how did you do this? alpha=", self.alpha)
            pn = self.player_number  # projectile created by player number x
            if type == "normal":
                self.shooting_sound.play()
                self.ranged_normal = True
                self.ranged_explodes = False
                self.ranged_bounces = False
                self.ranged_laser = False
                t = type
                d = 4
                c = "black"
                b = 0
                rec = 0.025
            elif type == "bouncy":
                self.shooting_sound.play()
                self.ranged_normal = False

                self.ranged_explodes = False
                self.ranged_bounces = True
                self.ranged_laser = False
                t = type
                d = 3
                c = "blue"
                b = 2
                rec = 0.025
            elif type == "explosive":
                self.missle_sound.play()
                self.ranged_normal = False
                self.ranged_explodes = True
                self.ranged_laser = False
                self.ranged_bounces = False
                t = type
                r = r * 2
                xs = xs / 2
                ys = ys / 2
                d = 0
                c = "gray"
                b = 0
                rec = 0
            elif type == "laser":
                self.ranged_normal = False
                self.ranged_explodes = False
                self.ranged_laser = True
                self.ranged_bounces = False

                self.no_move = True

                if self.ranged_cd == 0:
                    self.laser_sound.play()
            else:
                print("invalid type default to normal")
                self.ranged_normal = True
                self.ranged_explodes = False
                self.ranged_bounces = False
                self.ranged_laser = False
                t = "normal"
                d = 1
                c = "black"
                b = 0
                rec = 0.025
            # this shouldn't be needed since the robot that owns the projectiles array has this number,
            # but I used this as a fix in ranged_hit_reg, in order to be unable to hit yourself
            if type == "laser":
                pass  # if we fire a laser, we do not want another projectile added
            else:
                self.projectiles.append(Projectile(x, y, c, r, xs, ys, d, pn, b, t, rec))
        if type == "laser":

            #  if 30 <= self.ranged_cd <= 60:
            # self.hit_reg_rect(robots, arena, hit_box, 10, self.player_number, 0, 0.1)
            # pass

            (len_x, len_y) = self.find_closest_block(screen, arena)  # x,y cords of nearest collision in front
            max_range = self.radius * 10  # this is the maximum range of the laser
            # calculate the rectangle based on viewing direction
            if self.alpha == 0:  # right
                hit_box_height = 2 * self.radius
                hit_box_width = min(abs(len_x - self.posx), max_range)
                rect_left_x = self.posx + self.radius
                rect_top_y = self.posy - self.radius
            elif self.alpha == 90:  # down
                hit_box_height = min(abs(len_y - self.posy), max_range)
                hit_box_width = 2 * self.radius
                rect_left_x = self.posx - self.radius
                rect_top_y = self.posy + self.radius
            elif self.alpha == 180:  # left
                hit_box_height = 2 * self.radius
                hit_box_width = min(abs(len_x - self.posx), max_range)
                rect_left_x = self.posx - self.radius - hit_box_width
                rect_top_y = self.posy - self.radius
            elif self.alpha == 270:  # up
                hit_box_height = min(abs(len_y - self.posy), max_range)
                hit_box_width = 2 * self.radius
                rect_left_x = self.posx - self.radius
                rect_top_y = self.posy - self.radius - hit_box_height

            laser_len = int(max(hit_box_width, hit_box_height))
            if hit_box_width > 0 and hit_box_height > 0:
                if laser_len * 1.3 < self.laser_len or laser_len * 0.7 > self.laser_len or self.old_alpha != self.alpha:
                    laser_rotated = pygame.transform.rotate(self.laser, -self.alpha)
                    self.old_alpha = self.alpha
                    self.laser_len = laser_len
                    self.scaled_laser = pygame.transform.scale(laser_rotated, (int(hit_box_width), int(hit_box_height)))

            # now we have the rectangle, so we draw it and calculate the hit_reg
            hit_box = pygame.Rect(rect_left_x, rect_top_y, hit_box_width, hit_box_height)
            screen.blit(self.scaled_laser, hit_box)
            self.hit_reg_rect(robots, arena, hit_box, 10, self.player_number, 0, 0.1)

    def find_closest_block(self, screen, arena):
        r = 0  # this looks like it works, a projectile with radius 0
        pn = self.player_number  # projectile created by player number x
        if self.alpha == 0:  # right
            xs = 1
            ys = 0
            x = self.posx + self.radius
            y = self.posy
        elif self.alpha == 90:  # down
            xs = 0
            ys = 1
            x = self.posx
            y = self.posy + self.radius
        elif self.alpha == 180:  # left
            xs = -1
            ys = 0
            x = self.posx - self.radius
            y = self.posy
        elif self.alpha == 270:  # up
            xs = 0
            ys = -1
            x = self.posx
            y = self.posy - self.radius
        else:  # failsafe
            print("how did you do this? alpha=", self.alpha)
        proj_number = len(self.projectiles)
        t = "tracer"
        d = 0
        c = "black"
        self.projectiles.append(Projectile(x, y, c, r, xs, ys, d, pn, 0, t, 0))
        # this projectile will be used to find a possibly existing closest block

        # now we must find distance to the edges of the arena
        screen_height = screen.get_height()
        screen_width = screen.get_width()
        x_right = abs(self.posx - arena.x_offset)  # distance to left arena edge
        x_left = abs(self.posx - (screen_width - arena.x_offset))
        y_up = abs(self.posy - arena.y_offset)
        y_down = abs(self.posy - (screen_height - arena.y_offset))
        # print(x_left, x_right, y_up, y_down)
        x_col = self.posx
        y_col = self.posy
        i = 0
        if ys == 0:  # left or right
            if self.alpha == 180:  # right
                while i < x_right and not self.projectiles[proj_number].check_collision_x(arena):
                    # we take our tracer projectile and move it until we hit either a block, the edge of the map,
                    # or the maximum range
                    self.projectiles[proj_number].move_projectile(1)
                    x_col += 1  # we save the x cord of our final point at the end of the loop
                    i += 1
            else:  # left
                while i < x_left and not self.projectiles[proj_number].check_collision_x(arena):
                    self.projectiles[proj_number].move_projectile(1)
                    x_col += 1
                    i += 1
            self.projectiles.pop(proj_number)  # once we have a collision we remove the projectile
        else:  # up or down
            if self.alpha == 90:  # down
                while i < y_down and not self.projectiles[proj_number].check_collision_y(arena):
                    self.projectiles[proj_number].move_projectile(1)
                    y_col += 1  # or y cord in these 2 cases
                    i += 1
            else:  # up
                while i < y_up and not self.projectiles[proj_number].check_collision_y(arena):
                    self.projectiles[proj_number].move_projectile(1)
                    y_col += 1
                    i += 1
            self.projectiles.pop(proj_number)  # once we are done here we can delete the projectile
        # print(x_col, y_col)
        return x_col, y_col

    def ranged_hit_reg(self, pygame, screen, robots, arena):
        # we can probably get screen_height and screen_width from the screen itself
        screen_height = screen.get_height()
        screen_width = screen.get_width()
        # this should be it
        for i in range(0, len(robots)):
            to_delete = []
            for j in range(0, len(robots[i].projectiles)):
                if i != robots[i].projectiles[j].player_number:  # do not hit yourself
                    # get distance from projectile center to robot center
                    distance = abs(robots[i].posx - robots[i].projectiles[j].x) + abs(
                        robots[i].posy - robots[i].projectiles[j].y
                    )
                    if distance < (robots[i].radius + robots[i].projectiles[j].radius):
                        # we have a direct hit
                        robots[i].take_damage_debug(robots[i].projectiles[j].damage, 0)
                        if robots[i].hit_cooldown <= 0:
                            if robots[i].projectiles[j].x_speed > 0:
                                direction = Projectile.Direction.RIGHT
                            elif robots[i].projectiles[j].x_speed < 0:
                                direction = Projectile.Direction.LEFT
                            elif robots[i].projectiles[j].y_speed > 0:
                                direction = Projectile.Direction.DOWN
                            else:
                                direction = Projectile.Direction.UP
                            self.recoil(arena, robots[i], direction, robots[i].projectiles[j].recoil)
                        # DO NOT REMOVE PROJECTILES INSIDE THE LOOP instead
                        to_delete.append(j)  # save the index (might be multiple)
                # Überprüfen, ob die Projectile die seitlichen Grenzen der Arena erreicht hat
                else:
                    if robots[i].projectiles[j].x < robots[i].projectiles[j].radius + arena.x_offset:
                        to_delete.append(j)
                        # left  # we shot the left wall
                    elif robots[i].projectiles[j].x > screen_width - robots[i].projectiles[j].radius - arena.x_offset:
                        to_delete.append(j)
                        # right
                    # Überprüfen, ob die Projectile die oberen und unteren Grenzen der Arena erreicht hat
                    elif robots[i].projectiles[j].y - robots[i].projectiles[j].radius < arena.y_offset:
                        to_delete.append(j)
                        # up
                    elif robots[i].projectiles[j].y + robots[i].projectiles[j].radius > screen_height - arena.y_offset:
                        to_delete.append(j)
                        # down
                    # Kollisionen in y-Richtung überprüfen und behandeln
                    elif robots[i].projectiles[j].check_collision_y(arena):
                        if robots[i].projectiles[j].bounce_count > 0:
                            robots[i].projectiles[j].bounce()
                        else:
                            to_delete.append(j)
                    # Kollisionen in x-Richtung überprüfen und behandeln
                    elif robots[i].projectiles[j].check_collision_x(arena):
                        if robots[i].projectiles[j].bounce_count > 0:
                            robots[i].projectiles[j].bounce()
                        else:
                            to_delete.append(j)
            # im not 100% sure if it's possible for a projectile to be added to the to_delete array twice,
            # so I might have to add a duplicate remover here

            to_delete = reversed(to_delete)  # reverse it so we delete the largest index first
            for n in to_delete:  # after the j loop we delete them
                if robots[i].projectiles[n].type == "explosive":  # if projectile is explosive
                    #  place holder explosion
                    rectx = robots[i].projectiles[n].x
                    recty = robots[i].projectiles[n].y
                    rectr = robots[i].projectiles[n].radius
                    explosive_rect = pygame.Rect(rectx - 4 * rectr, recty - 4 * rectr, 8 * rectr, 8 * rectr)
                    self.explosions.append(Explosion(5, 10, explosive_rect))
                    self.missle_sound.stop()
                    self.explosion_sound.play()
                    # could be consolidated into an object

                    # tested with this, we do identify explosions correctly
                robots[i].projectiles.pop(n)

    def reset_projectiles(self):
        for i in range(0, len(self.projectiles)):
            self.projectiles.pop(0)
        # self.projectiles = [] # this does not work properly :(

    def hit_reg_line(self, robots, arena, line_start, line_end, dmg, recoil):
        for i in range(0, len(robots)):  # old hitreg should still work
            if i == self.player_number:
                continue
            # now I will use https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line:
            # Line defined by two points
            if (
                self.distance_from_segment(
                    line_start[0], line_start[1], line_end[0], line_end[1], robots[i].posx, robots[i].posy
                )
                <= robots[i].radius
            ):  # if the distance from this line to the center of a robot
                # is smaller than it's radius, we have a hit and that robot takes some damage
                robots[i].take_damage_debug(dmg, 0)
                if robots[i].hit_cooldown <= 0:
                    if self.alpha == 180:
                        direction = Projectile.Direction.LEFT
                    elif self.alpha == 0:
                        direction = Projectile.Direction.RIGHT
                    elif self.alpha == 270:
                        direction = Projectile.Direction.UP
                    else:
                        direction = Projectile.Direction.DOWN
                    self.recoil(arena, robots[i], direction, recoil)

    def hit_reg_rect(self, robots, arena, rect, dmg, exception, fire, recoil):
        # exception is used to exclude one robot
        # if we change our collision to be a hit box, we could use some builtin functions
        tl = rect.topleft
        tr = rect.topright
        bl = rect.bottomleft
        br = rect.bottomright
        for i in range(0, len(robots)):  # check all robots
            if i != exception:  # use -1 for no exception

                if (
                    (bl[1] < robots[i].posy < tl[1] and bl[0] < robots[i].posx < br[0])  # inside of rect
                    or (
                        self.distance_from_segment(tl[0], tl[1], tr[0], tr[1], robots[i].posx, robots[i].posy)
                        <= robots[i].radius
                    )
                    or (
                        self.distance_from_segment(tl[0], tl[1], bl[0], bl[1], robots[i].posx, robots[i].posy)
                        <= robots[i].radius
                    )
                    or (
                        self.distance_from_segment(br[0], br[1], tr[0], tr[1], robots[i].posx, robots[i].posy)
                        <= robots[i].radius
                    )
                    or (
                        self.distance_from_segment(br[0], br[1], bl[0], bl[1], robots[i].posx, robots[i].posy)
                        <= robots[i].radius
                    )
                ):
                    # or distance from robot to the sides of the rect is < robot radius
                    robots[i].take_damage_debug(dmg, fire)
                    dist_top = self.distance_from_segment(tl[0], tl[1], tr[0], tr[1], robots[i].posx, robots[i].posy)
                    dist_left = self.distance_from_segment(tl[0], tl[1], bl[0], bl[1], robots[i].posx, robots[i].posy)
                    dist_right = self.distance_from_segment(br[0], br[1], tr[0], tr[1], robots[i].posx, robots[i].posy)
                    dist_down = self.distance_from_segment(br[0], br[1], bl[0], bl[1], robots[i].posx, robots[i].posy)

                    # find shortest distance from robot center to edge of hitbox and remember the side
                    if dist_top <= dist_down:
                        if dist_top <= dist_left:
                            if dist_top <= dist_right:
                                direction = Projectile.Direction.UP
                            else:  # dist_top <= dist_down, dist_top <= dist_left and dist_right < dist_top
                                direction = Projectile.Direction.RIGHT
                        else:  # dist_top <= dist_down and dist_left < dist_top-> dist_left < dist_top <= dist_down
                            if dist_left <= dist_right:
                                direction = Projectile.Direction.LEFT
                            else:  # dist_left < dist_top <= dist_down and dist_right < dist_left
                                direction = Projectile.Direction.RIGHT
                    else:  # dist_down < dist_top
                        if dist_down <= dist_left:
                            if dist_down <= dist_right:
                                direction = Projectile.Direction.DOWN
                            else:  # dist_down < dist_top, dist_down <= dist_left  and dist_right < dist_down
                                direction = Projectile.Direction.RIGHT
                        else:  # dist_left < dist_down < dist_top
                            if dist_left <= dist_right:
                                direction = Projectile.Direction.LEFT
                            else:
                                direction = Projectile.Direction.RIGHT

                    if robots[i].hit_cooldown <= 0:
                        self.recoil(arena, robots[i], direction, recoil)

    def decrease_hit_cooldown(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def decrease_i_frames(self):
        if self.i_frames > 0:
            self.i_frames -= 1

    def recoil(self, arena, robot, direction, recoil):
        self.damage_sound.play()
        robot.hit_cooldown = 20  # setting this so the robot doesn't get launched into space

        if direction == Projectile.Direction.UP:
            robot.vertical_speed += -arena.tile_size / 3 * robot.recoil_percent  # recoil up
        elif direction == Projectile.Direction.DOWN:
            robot.vertical_speed += arena.tile_size / 3 * robot.recoil_percent  # recoil down
        elif direction == Projectile.Direction.LEFT:
            robot.vertical_speed += -arena.tile_size / 4 * robot.recoil_percent  # recoil up
            robot.change_acceleration(robot.accel - (arena.tile_size / 3) * robot.recoil_percent)  # recoil left
            robot.change_velocity_cap(robot.vel + robot.accel)
        elif direction == Projectile.Direction.RIGHT:
            robot.vertical_speed += -arena.tile_size / 4 * robot.recoil_percent  # recoil up
            robot.change_acceleration(robot.accel + (arena.tile_size / 3) * robot.recoil_percent)  # recoil right
            robot.change_velocity_cap(robot.vel + robot.accel)

        robot.recoil_percent += recoil

    def handle_explosions(self, screen, arena, robots):
        for i in range(0, len(self.explosions)):
            if self.explosions[i].duration > 0:
                if self.scaled_explosion is None:
                    self.scaled_explosion = pygame.transform.scale(
                        self.explosion, (self.explosions[i].rectangle.width, self.explosions[i].rectangle.height)
                    )
                screen.blit(self.scaled_explosion, self.explosions[i].rectangle)
                self.hit_reg_rect(robots, arena, self.explosions[i].rectangle, self.explosions[i].damage, -1, 0, 0.1)
                self.explosions[i].reduce_duration()
            elif self.explosions[i].duration == 0:
                self.explosions.pop(i)

    def reset_explosions(self):
        for i in range(0, len(self.explosions)):
            self.explosions.pop(0)

    def paint_robot(self, pygame, screen, dt_scaled):
        # Bild des Roboters zeichnen
        image_rect = self.first_robot.get_rect(center=(self.posx, self.posy))
        pn = self.player_number
        if pn == 0:
            if not self.direction_left:
                screen.blit(self.first_robot, image_rect)
            elif self.direction_left:
                screen.blit(self.first_robot_flipped, image_rect)
        elif pn == 1:
            if not self.direction_left:
                screen.blit(self.second_robot, image_rect)
            elif self.direction_left:
                screen.blit(self.second_robot_flipped, image_rect)
        elif pn == 2:
            if not self.direction_left:
                screen.blit(self.third_robot, image_rect)
            elif self.direction_left:
                screen.blit(self.third_robot_flipped, image_rect)
        elif pn == 3:
            if not self.direction_left:
                screen.blit(self.fourth_robot, image_rect)
            elif self.direction_left:
                screen.blit(self.fourth_robot_flipped, image_rect)
        self.draw_health_bar(screen, self.health, self.health_max, self.player_number, self.color)
        self.draw_recoil_text(screen, self.recoil_percent, self.player_number, self.color)
        # projectiles
        for i in self.projectiles:  # each robot will paint and update the projectiles it has created
            # print(self.player_number, i.player_number)  # why do all robots share the projectiles?
            if self.player_number == i.player_number:  # this should fix it
                i.paint_projectile(pygame, screen)
                i.move_projectile(dt_scaled)

    # Lebenspunkte als Balken
    def draw_health_bar(self, screen, health, max_health, player_number, color):
        screen_width = pygame.display.get_window_size()[0]
        screen_height = pygame.display.get_window_size()[1]
        bar_width = screen_width / 6
        bar_height = screen_height / 40
        bar_x = screen_width / 3.42 + (screen_width / 4) * (player_number - 1)
        bar_y = screen_height / 30

        # Hintergrund des Balkens (für die maximalen Lebenspunkte)
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Füllung des Balkens (entsprechend der aktuellen Lebenspunkte)
        health_width = (health / max_health) * bar_width
        pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))

        # Rahmen um den Balken
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    # Rückstoßanzeige mit spezieller Schriftart
    def draw_recoil_text(self, screen, recoil_percent, player_number, color):
        screen_width = pygame.display.get_window_size()[0]
        screen_height = pygame.display.get_window_size()[1]
        font_path = "../fonts/Bigdex.ttf"
        # Eine coole Schriftart laden
        recoil_font = pygame.font.Font(font_path, int(screen_height / 20))
        # Rückstoßprozente als Text rendern
        recoil_text = recoil_font.render(f"{int(recoil_percent * 100)}%", True, color)
        recoil_rect = recoil_text.get_rect(
            center=(screen_width / 2.62 + (screen_width / 4) * (player_number - 1), screen_height / 13)
        )

        # Textumrandung (zum Beispiel ein leichtes Schwarz für besseren Kontrast)
        outline_thickness = 2
        outline_color = (0, 0, 0)
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx != 0 or dy != 0:
                    screen.blit(
                        recoil_font.render(f"{int(recoil_percent * 100)}%", True, outline_color),
                        recoil_rect.move(dx, dy),
                    )

        # Den eigentlichen Text rendern
        screen.blit(recoil_text, recoil_rect)
