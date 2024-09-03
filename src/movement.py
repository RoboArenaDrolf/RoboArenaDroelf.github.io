from src.projectiles import Projectile


class Movement:

    def __init__(self, gravity):
        self.gravity = gravity

    def move_robot(self, robot, x, arena, frames):

        dt_scaled = (sum(frames) / len(frames)) / 15
        # Bewegung in x-Richtung
        robot.posx += x * dt_scaled

        # Vertikale Bewegung
        robot.vertical_speed += self.gravity * dt_scaled

        # Bewegung in y-Richtung
        robot.posy += robot.vertical_speed
        no_reset = False

        # Kollisionen in y-Richtung überprüfen und behandeln
        if self.check_tile_type_y(robot, arena) == 1:  # if we touch lava-> take dmg and apply fire
            robot.take_damage_debug(2, 40)  # 2 damage instantly and 40 frames of fire
            if robot.hit_cooldown <= 0:
                if robot.vertical_speed < 0:
                    direction = Projectile.Direction.DOWN
                else:
                    direction = Projectile.Direction.UP
                robot.recoil(arena, robot, direction, 0.05)
                no_reset = True

        if self.check_collision_y(robot, arena):
            if robot.vertical_speed > 0:  # Kollision von oben
                # we stand on some tile -> find out which one
                if self.check_tile_type_y(robot, arena) == 1:  # lava
                    robot.tile_below = 1
                elif self.check_tile_type_y(robot, arena) == 2:  # ice
                    robot.tile_below = 2
                elif self.check_tile_type_y(robot, arena) == 3:  # sand
                    robot.tile_below = 3
                else:  # none of the above
                    robot.tile_below = 0

                robot.posy = (
                    ((robot.posy - arena.y_offset) // arena.tile_size + 1) * arena.tile_size
                    - robot.radius
                    + arena.y_offset
                )
                robot.jump_counter = 0
            else:  # Kollision von unten
                robot.posy = (
                    ((robot.posy - arena.y_offset) // arena.tile_size) * arena.tile_size + robot.radius + arena.y_offset
                )
            if no_reset:
                pass
            else:
                robot.vertical_speed = float(0)
            no_reset = False

        # Kollisionen in x-Richtung überprüfen und behandeln
        if self.check_tile_type_x(robot, arena) == 1:  # if we touch lava-> take dmg
            robot.take_damage_debug(2, 40)
            if robot.hit_cooldown <= 0:
                if x < 0:
                    direction = Projectile.Direction.RIGHT
                else:
                    direction = Projectile.Direction.LEFT
                robot.recoil(arena, robot, direction, 0.05)
                no_reset = True

        if self.check_collision_x(robot, arena):
            if x > 0:
                robot.posx = (
                    ((robot.posx - arena.x_offset) // arena.tile_size + 1) * arena.tile_size
                    - robot.radius
                    + arena.x_offset
                )
            elif x < 0:
                robot.posx = (
                    ((robot.posx - arena.x_offset) // arena.tile_size) * arena.tile_size + robot.radius + arena.x_offset
                )
            if no_reset:
                pass
            else:
                robot.change_acceleration(0)
                robot.change_velocity(0)
            no_reset = False

        # Sprung
        if robot.jump:
            robot.vertical_speed = (
                -arena.tile_size / 3.5
            ) * dt_scaled  # Vertikale Geschwindigkeit für den ersten Sprung setzen
            robot.jump_counter += 1
            robot.jump = False
            robot.tile_below = 0  # if we jump we no longer stand on a tile, might not be needed

    def check_collision_y(self, robot, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf y-Achse
        x_positions = [
            int((robot.posx - arena.x_offset) // arena.tile_size),
            int((robot.posx - arena.x_offset + robot.radius / 2) // arena.tile_size),
            int((robot.posx - arena.x_offset - robot.radius / 2) // arena.tile_size),
        ]
        y_positions = [
            int((robot.posy - arena.y_offset + robot.radius) // arena.tile_size),
            int((robot.posy - arena.y_offset - robot.radius) // arena.tile_size),
        ]
        return arena.is_solid(x_positions, y_positions)

    def check_collision_x(self, robot, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf x-Achse
        x_positions = [
            int((robot.posx - arena.x_offset + robot.radius) // arena.tile_size),
            int((robot.posx - arena.x_offset - robot.radius) // arena.tile_size),
        ]
        y_positions = [
            int((robot.posy - arena.y_offset) // arena.tile_size),
            int((robot.posy - arena.y_offset + robot.radius / 2) // arena.tile_size),
            int((robot.posy - arena.y_offset - robot.radius / 2) // arena.tile_size),
        ]
        return arena.is_solid(x_positions, y_positions)

    def check_tile_type_y(self, robot, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf y-Achse
        x_positions = [
            int((robot.posx - arena.x_offset) // arena.tile_size),
            int((robot.posx - arena.x_offset + robot.radius / 2) // arena.tile_size),
            int((robot.posx - arena.x_offset - robot.radius / 2) // arena.tile_size),
        ]
        y_positions = [
            int((robot.posy - arena.y_offset + robot.radius) // arena.tile_size),
            int((robot.posy - arena.y_offset - robot.radius) // arena.tile_size),
        ]
        if arena.is_lava(x_positions, y_positions):
            return 1
        elif arena.is_ice(x_positions, y_positions):
            return 2
        elif arena.is_sand(x_positions, y_positions):
            return 3
        else:
            return 0

    def check_tile_type_x(self, robot, arena):
        # Überprüfen, ob der Roboter mit einem festen Tile kollidiert auf x-Achse
        x_positions = [
            int((robot.posx - arena.x_offset + robot.radius) // arena.tile_size),
            int((robot.posx - arena.x_offset - robot.radius) // arena.tile_size),
        ]
        y_positions = [
            int((robot.posy - arena.y_offset) // arena.tile_size),
            int((robot.posy - arena.y_offset + robot.radius / 2) // arena.tile_size),
            int((robot.posy - arena.y_offset - robot.radius / 2) // arena.tile_size),
        ]
        if arena.is_lava(x_positions, y_positions):
            return 1
        elif arena.is_ice(x_positions, y_positions):
            return 2
        elif arena.is_sand(x_positions, y_positions):
            return 3
        else:
            return 0
