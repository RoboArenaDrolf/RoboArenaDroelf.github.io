import math
import pygame

from src.projectiles import Projectile


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
    projectiles = []
    melee_cd = 0
    ranged_cd = 0
    robots_base_path = "./../Robots/"
    recoil_percent = 0.1
    hit_cooldown = 0
    attack_start: int
    attack_buffer: int
    ranged_explodes: bool  # false = normal true = explosive
    heavy_attack: bool  # false = light true = heavy
    no_move = False  # false = moving allowed true = moving not allowed, start with allowed movement
    explosions = []

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
        self.first_robot = pygame.image.load(self.robots_base_path + "firstRobot.png")
        self.first_robot = pygame.transform.scale(self.first_robot, (self.radius * 2, self.radius * 2))
        self.first_robot_flipped = pygame.transform.flip(self.first_robot, True, False)
        self.second_robot = pygame.image.load(self.robots_base_path + "secondRobot.png")
        self.second_robot = pygame.transform.scale(self.second_robot, (self.radius * 2, self.radius * 2))
        self.second_robot_flipped = pygame.transform.flip(self.second_robot, True, False)
        self.tile_below = 0

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

    def take_damage_debug(self, d):
        if d <= self.health:
            self.health = self.health - d
        else:
            self.health = 0

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
                # print(i, "hit")
                robots[i].take_damage_debug(1)
                if robots[i].hit_cooldown <= 0:
                    self.recoil(arena, robots[i])

    def distance_from_segment(self, x1, y1, x2, y2, x3, y3):
        # Vektoren berechnen
        px, py = x2 - x1, y2 - y1
        norm = px * px + py * py

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
            if 30 <= self.melee_cd <= 60:
                hit_box_height = 2 * self.radius
                hit_box_width = 2 * self.radius
                if self.alpha == 0:  # right
                    rect_left_x = self.posx + 0.5 * hit_box_width
                    rect_top_y = self.posy - 0.5 * hit_box_height
                elif self.alpha == 90:  # down
                    rect_left_x = self.posx - 0.5 * hit_box_width
                    rect_top_y = self.posy + 0.5 * hit_box_height
                elif self.alpha == 180:  # left
                    rect_left_x = self.posx - 1.5 * hit_box_height
                    rect_top_y = self.posy - 0.5 * hit_box_height
                elif self.alpha == 270:  # up
                    rect_left_x = self.posx - 0.5 * hit_box_height
                    rect_top_y = self.posy - 1.5 * hit_box_height
                else:  # failsafe
                    print("how did you do this? alpha=", self.alpha)
                hit_box = pygame.Rect(rect_left_x, rect_top_y, hit_box_width, hit_box_height)
                pygame.draw.rect(screen, "red", hit_box, width=2)
                self.hit_reg_rect(robots, arena, hit_box, 10, self.player_number)
        elif type == "light":
            self.heavy_attack = False
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
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.attack_buffer = 0
                self.hit_reg_line(robots, arena, line_start, line_end, 1)
            elif self.melee_cd % 5 == 0 and self.melee_cd <= 30:
                self.attack_start = (self.attack_start + 15) % 360
                new_x = self.radius * (math.cos(math.radians(self.attack_start)))
                new_y = self.radius * (math.sin(math.radians(self.attack_start)))
                line_start = (self.posx + new_x, self.posy + new_y)
                line_end = (self.posx + new_x * 2.5, self.posy + new_y * 2.5)
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 1)
                self.attack_buffer = 4
            elif self.attack_buffer > 0:
                new_x = self.radius * (math.cos(math.radians(self.attack_start)))
                new_y = self.radius * (math.sin(math.radians(self.attack_start)))
                line_start = (self.posx + new_x, self.posy + new_y)
                line_end = (self.posx + new_x * 2.5, self.posy + new_y * 2.5)
                pygame.draw.line(screen, "red", line_start, line_end, width=4)
                self.hit_reg_line(robots, arena, line_start, line_end, 1)
                self.attack_buffer -= 1

    def ranged_attack(self, type):
        if self.ranged_cd == 0 or self.ranged_cd == 10:
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
                self.ranged_explodes = False
                t = type
                d = 1
                c = "black"
            elif type == "explosive":
                self.ranged_explodes = True
                t = type
                r = r * 2
                xs = xs / 2
                ys = ys / 2
                d = 5
                c = "gray"
            else:
                print("invalid type default to normal")
                self.ranged_explodes = False
                t = "normal"
                d = 1
                c = "black"
            # this shouldn't be needed since the robot that owns the projectiles array has this number,
            # but I used this as a fix in ranged_hit_reg, in order to be unable to hit yourself
            self.projectiles.append(Projectile(x, y, c, r, xs, ys, d, pn, t))  # this append must be the reason

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
                        robots[i].take_damage_debug(robots[i].projectiles[j].damage)
                        if robots[i].hit_cooldown <= 0:
                            self.recoil(arena, robots[i])
                        # DO NOT REMOVE PROJECTILES INSIDE THE LOOP instead
                        to_delete.append(j)  # save the index (might be multiple)
                # Überprüfen, ob die Projectile die seitlichen Grenzen der Arena erreicht hat
                if robots[i].projectiles[j].x < robots[i].projectiles[j].radius + arena.x_offset:
                    to_delete.append(j)
                    # print("we delete this, left")  # shoot the left wall and see this
                elif robots[i].projectiles[j].x > screen_width - robots[i].projectiles[j].radius - arena.x_offset:
                    to_delete.append(j)
                    # print("we delete this, right")
                # Überprüfen, ob die Projectile die oberen und unteren Grenzen der Arena erreicht hat
                elif robots[i].projectiles[j].y - robots[i].projectiles[j].radius < arena.y_offset:
                    to_delete.append(j)
                    # print("we delete this, up")
                elif robots[i].projectiles[j].y + robots[i].projectiles[j].radius > screen_height - arena.y_offset:
                    to_delete.append(j)
                    # print("we delete this, down")
                # Kollisionen in y-Richtung überprüfen und behandeln
                elif robots[i].projectiles[j].check_collision_y(arena):
                    to_delete.append(j)
                # Kollisionen in x-Richtung überprüfen und behandeln
                elif robots[i].projectiles[j].check_collision_x(arena):
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
                    self.explosions.append(explosive_rect)  # add the explosion
                    self.explosions.append(5)  # add the duration
                    # could be consolidated into an object

                    # print("boom")
                    # tested with this, we do identify explosions correctly
                robots[i].projectiles.pop(n)

    def hit_reg_line(self, robots, arena, line_start, line_end, dmg):
        for i in range(1, len(robots)):  # old hitreg should still work
            # now I will use https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line:
            # Line defined by two points
            if (
                self.distance_from_segment(
                    line_start[0], line_start[1], line_end[0], line_end[1], robots[i].posx, robots[i].posy
                )
                <= robots[i].radius
            ):  # if the distance from this line to the center of a robot
                # is smaller than it's radius, we have a hit and that robot takes some damage
                # print(i, "hit")
                robots[i].take_damage_debug(dmg)
                if robots[i].hit_cooldown <= 0:
                    self.recoil(arena, robots[i])

    def hit_reg_rect(self, robots, arena, rect, dmg, exception):
        # j is a placeholder, we use it to exclude one robot
        # if we change our collision to be a hit box, we could use some builtin functions
        tl = rect.topleft
        tr = rect.topright
        bl = rect.bottomleft
        br = rect.bottomright
        for i in range(0, len(robots)):  # check all robots
            if i != exception:  # except for j, use -1 for no exception
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
                ):  # or distance from robot to the sides of the rect is < robot radius
                    robots[i].take_damage_debug(dmg)
                    if robots[i].hit_cooldown <= 0:
                        self.recoil(arena, robots[i])

    def decrease_hit_cooldown(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def recoil(self, arena, robot):
        robot.hit_cooldown = 20  # setting this so the robot doesn't get launched into space
        # cause recoil
        robot.vertical_speed += -arena.map_size[1] / 50 * robot.recoil_percent  # recoil up
        # check if we face left, right or upwards
        if self.alpha > 315 or self.alpha == 0:  # facing right
            robot.change_acceleration(robot.accel + (arena.map_size[0] / 40) * robot.recoil_percent)
        elif self.alpha < 225:  # facing left
            robot.change_acceleration(robot.accel - (arena.map_size[0] / 40) * robot.recoil_percent)
        else:  # facing upwards
            robot.vertical_speed += -arena.map_size[1] / 100 * robot.recoil_percent  # recoil up again
        robot.recoil_percent += 0.05

    def handle_explosions(self, screen, arena, robots):
        for i in range(0, len(self.explosions) - 1):
            if self.explosions[i + 1] > 0:
                pygame.draw.rect(screen, "red", self.explosions[i], 1)
                self.hit_reg_rect(robots, arena, self.explosions[i], 5, -1)  # explosive damage is 5 for now
                self.explosions[i + 1] -= 1
            elif self.explosions[i + 1] == 0:
                self.explosions.pop(i + 1)
                self.explosions.pop(i)
            i = i + 1  # we want to jump 2 at a time

    def paint_robot(self, pygame, screen, direction_left):
        # Bild des Roboters zeichnen
        image_rect = self.first_robot.get_rect(center=(self.posx, self.posy))
        pn = self.player_number
        if pn == 0:
            if not direction_left:
                screen.blit(self.first_robot, image_rect)
            elif direction_left:
                screen.blit(self.first_robot_flipped, image_rect)
        elif pn == 1:
            if not direction_left:
                screen.blit(self.second_robot, image_rect)
            elif direction_left:
                screen.blit(self.second_robot_flipped, image_rect)
        elif pn == 2:
            if not direction_left:
                screen.blit(self.first_robot, image_rect)
            elif direction_left:
                screen.blit(self.first_robot_flipped, image_rect)
        elif pn == 3:
            if not direction_left:
                screen.blit(self.first_robot, image_rect)
            elif direction_left:
                screen.blit(self.first_robot_flipped, image_rect)
        self.draw_health_bar(screen, self.health, self.health_max, self.player_number, self.color)
        self.draw_recoil_text(screen, self.recoil_percent, self.player_number, self.color)
        # projectiles
        for i in self.projectiles:  # each robot will paint and update the projectiles it has created
            # print(self.player_number, i.player_number)  # why do all robots share the projectiles?
            if self.player_number == i.player_number:  # this should fix it
                i.paint_projectile(pygame, screen)
                i.move_projectile()

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
