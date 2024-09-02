from projectiles import Projectile


class Movement:

    def __init__(self, gravity):
        self.gravity = gravity

    def move_robot(self, robot, x, arena, dt):
        dt_scaled = dt / 15.0

        # Bewegung in x-Richtung
        robot.posx += x * 0.6

        # Vertikale Bewegung
        robot.vertical_speed += self.gravity * 0.6

        # Bewegung in y-Richtung
        robot.posy += robot.vertical_speed

        # Kollisionen in y-Richtung überprüfen und behandeln
        if self.check_collision_y(robot, arena):
            if self.check_tile_type_y(robot, arena) == 1:  # if we touch lava-> take dmg and apply fire
                robot.take_damage_debug(2, 40)  # 2 damage instantly and 40 frames of fire
                if robot.hit_cooldown <= 0:
                    if robot.vertical_speed < 0:
                        direction = Projectile.Direction.DOWN
                    else:
                        direction = Projectile.Direction.UP
                    robot.recoil(arena, robot, direction, 0.05)
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
            robot.vertical_speed = float(0)

        # Kollisionen in x-Richtung überprüfen und behandeln
        if self.check_collision_x(robot, arena):
            if self.check_tile_type_x(robot, arena) == 1:  # if we touch lava-> take dmg
                robot.take_damage_debug(2, 40)
                if robot.hit_cooldown <= 0:
                    if x < 0:
                        direction = Projectile.Direction.RIGHT
                    else:
                        direction = Projectile.Direction.LEFT
                    robot.recoil(arena, robot, direction, 0.05)
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
            robot.change_acceleration(0)
            robot.change_velocity(0)

        # Sprung
        if robot.jump:
            robot.vertical_speed = (
                -arena.tile_size / 3.5
            ) * 0.6  # Vertikale Geschwindigkeit für den ersten Sprung setzen
            #  print(robot.vertical_speed, dt_scaled, dt, arena.tile_size, self.gravity)  # dt scaled changes
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
