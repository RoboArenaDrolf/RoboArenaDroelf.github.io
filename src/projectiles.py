from enum import Enum


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
    recoil: int

    def __init__(self, x, y, c, r, xs, ys, d, pn, b, t, rec):
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
        self.recoil = rec

    def move_projectile(self, dt_scaled):
        self.x = self.x + self.x_speed * dt_scaled
        self.y = self.y + self.y_speed * dt_scaled

    def bounce(self):
        self.bounce_count = self.bounce_count - 1
        self.x_speed = -self.x_speed
        self.y_speed = -self.y_speed

    def paint_projectile(self, pygame, screen):
        # if self.type == "small":
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # if self.type == "big":

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
