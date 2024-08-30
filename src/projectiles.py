from enum import Enum
import pygame


class Projectile:

    class Direction(Enum):
        """
        Enum of different directions of a projectile or a melee attack for recoil.
        """

        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4

    x: int
    y: int
    radius: int
    color: str
    x_speed: int
    y_speed: int
    damage: int
    type: str
    bounce_count: int
    player_number: int

    def __init__(self, x, y, c, r, xs, ys, d, pn, b, t):
        self.x = x
        self.y = y
        self.color = c
        self.radius = r
        self.x_speed = xs
        self.y_speed = ys
        self.damage = d
        self.player_number = pn
        self.bounce_count = b
        self.type = t

        missle = pygame.image.load('../Animation/missle.png')
        scale_factor = self.radius * 3 / missle.get_width()
        self.missle = pygame.transform.scale(missle,(int(self.radius * 3), int(missle.get_height() * scale_factor)))

    def move_projectile(self):
        self.x = self.x + self.x_speed
        self.y = self.y + self.y_speed

    def bounce(self):
        self.bounce_count = self.bounce_count - 1
        self.x_speed = -self.x_speed
        self.y_speed = -self.y_speed

    def paint_projectile(self, pygame, screen):
        # if self.type == "small":
        #pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        projectile = pygame.image.load('../Animation/projektil.png')
        projectile = pygame.transform.scale(projectile, (10,10))
        screen.blit(projectile,(self.x, self.y))
        # if self.type == "big":

    def paint_missle(self, pygame, screen):
        if self.x_speed < 0 and self.y_speed == 0:
            missle = pygame.transform.rotate(self.missle,90)
        elif self.x_speed == 0 and self.y_speed < 0:
            missle = pygame.transform.rotate(self.missle,0)
        elif self.x_speed == 0 and self.y_speed > 0:
            missle = pygame.transform.rotate(self.missle,180)
        elif self.x_speed > 0 and self.y_speed == 0:
            missle = pygame.transform.rotate(self.missle,-90)
        top_left_x = self.x - self.missle.get_width() // 2
        top_left_y = self.y - self.missle.get_height() // 2
        screen.blit(missle, (top_left_x, top_left_y))



    def paint_bounce(self,pygame,screen):
        bounce = pygame.image.load('../Animation/bounce.png')
        bounce = pygame.transform.scale(bounce, (20,20))
        screen.blit(bounce,(self.x, self.y))


    def check_collision_y(self, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf y-Achse
        x_positions = [
            int((self.x - arena.x_offset) // arena.tile_size),
            int((self.x - arena.x_offset + self.radius / 2) // arena.tile_size),
            int((self.x - arena.x_offset - self.radius / 2) // arena.tile_size),
        ]
        y_positions = [
            int((self.y - arena.y_offset + self.radius) // arena.tile_size),
            int((self.y - arena.y_offset - self.radius) // arena.tile_size),
        ]
        return arena.is_solid(x_positions, y_positions)

    def check_collision_x(self, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf x-Achse
        x_positions = [
            int((self.x - arena.x_offset + self.radius) // arena.tile_size),
            int((self.x - arena.x_offset - self.radius) // arena.tile_size),
        ]
        y_positions = [
            int((self.y - arena.y_offset) // arena.tile_size),
            int((self.y - arena.y_offset + self.radius / 2) // arena.tile_size),
            int((self.y - arena.y_offset - self.radius / 2) // arena.tile_size),
        ]
        return arena.is_solid(x_positions, y_positions)
