import pygame


class Movement:

    def __init__(self, gravity):
        self.gravity = gravity

    def move_robot(self, robot, screen_height, screen_width, x, arena):
        keys = pygame.key.get_pressed()

        # Bewegung in x-Richtung
        robot.posx += x

        # Vertikale Bewegung
        robot.vertical_speed += self.gravity

        # Bewegung in y-Richtung
        robot.posy += robot.vertical_speed

        # Überprüfen, ob der Roboter die seitlichen Grenzen der Arena erreicht hat
        if robot.posx < robot.radius + arena.x_offset:
            robot.posx = robot.radius + arena.x_offset
            robot.change_velocity(0)
            robot.change_acceleration(0)
        elif robot.posx > screen_width - robot.radius - arena.x_offset:
            robot.posx = screen_width - robot.radius - arena.x_offset
            robot.change_velocity(0)
            robot.change_acceleration(0)

        # Überprüfen, ob der Roboter die oberen und unteren Grenzen der Arena erreicht hat
        if robot.posy - robot.radius < arena.y_offset:
            robot.posy = robot.radius + arena.y_offset
            if robot.vertical_speed < 0:
                robot.vertical_speed = float(0)
        elif robot.posy + robot.radius > screen_height - arena.y_offset:
            robot.posy = screen_height - robot.radius - arena.y_offset
            if robot.vertical_speed > 0:
                robot.vertical_speed = float(0)

        # Kollisionen in y-Richtung überprüfen und behandeln
        if self.check_collision_y(robot, arena):
            if robot.vertical_speed > 0:  # Kollision von oben
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

        # Tastatureingaben verarbeiten
        if keys[pygame.K_UP]:
            if robot.jump_counter == 0:
                robot.vertical_speed = (
                    -arena.map_size[1] / 100
                )  # Vertikale Geschwindigkeit für den ersten Sprung setzen
                robot.jump_counter = 1
            elif robot.can_jump_again:
                robot.vertical_speed = -arena.map_size[1] / 100  # Vertikale Geschwindigkeit für den Doppelsprung setzen
                robot.can_jump_again = False
                robot.jump_counter = 2

        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP and robot.jump_counter == 1:
                    robot.can_jump_again = True

    def move_bot(self, robot, screen_height, screen_width, x, arena, jump):

        # Bewegung in x-Richtung
        robot.posx += x

        # Vertikale Bewegung
        robot.vertical_speed += self.gravity

        # Bewegung in y-Richtung
        robot.posy += robot.vertical_speed

        # Überprüfen, ob der Roboter die seitlichen Grenzen der Arena erreicht hat
        if robot.posx < robot.radius + arena.x_offset:
            robot.posx = robot.radius + arena.x_offset
            robot.change_velocity(0)
            robot.change_acceleration(0)
        elif robot.posx > screen_width - robot.radius - arena.x_offset:
            robot.posx = screen_width - robot.radius - arena.x_offset
            robot.change_velocity(0)
            robot.change_acceleration(0)

        # Überprüfen, ob der Roboter die oberen und unteren Grenzen der Arena erreicht hat
        if robot.posy - robot.radius < arena.y_offset:
            robot.posy = robot.radius + arena.y_offset
            if robot.vertical_speed < 0:
                robot.vertical_speed = float(0)
        elif robot.posy + robot.radius > screen_height - arena.y_offset:
            robot.posy = screen_height - robot.radius - arena.y_offset
            if robot.vertical_speed > 0:
                robot.vertical_speed = float(0)

        # Kollisionen in y-Richtung überprüfen und behandeln
        if self.check_collision_y(robot, arena):
            if robot.vertical_speed > 0:  # Kollision von oben
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

        # Tastatureingaben verarbeiten
        if jump:
            robot.vertical_speed = -arena.map_size[1] / 100  # Vertikale Geschwindigkeit für Sprung setzen

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