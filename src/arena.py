import json
from enum import Enum
from screens import Screens


class Arena:
    class TileType(Enum):
        """
        Enum of different tile types, value of tile represents its filename.
        """

        AIR = ("Air.png", False)
        GRASS = ("Grass.png", True)
        ICE = ("Ice.png", True)
        SAND = ("Sand.png", True)
        LAVA = ("Lava.png", True)
        BIRCH = ("Birch.png", True)
        LEAVES = ("Leaves.png", True)
        SPAWN = ("Spawn.png", False)

        def __init__(self, filename, solid):
            self.filename = filename
            self.solid = solid
            self.image = None

        @classmethod
        def set_values_to_pics(cls, pygame, base_path, tile_size):
            """
            Sets the images of the Enum TileType to the loaded pictures specified by their filename.
            :param pygame: instance of pygame
            :param base_path: base path of picture directory, for example ".\\Tiles\\"
            :param tile_size: size of the tiles
            """
            for member in cls:
                member.image = pygame.transform.scale(
                    pygame.image.load(base_path + member.filename).convert(), (tile_size, tile_size)
                )

    blocks_base_path = "../Tiles/"
    maps_base_path = "./../Maps/"

    def __init__(self, filename, pygame):
        self.load_map_from_json(filename, pygame)
        self.tile_size = int(
            min(
                pygame.display.get_window_size()[0] / len(self.tiles[0]),
                pygame.display.get_window_size()[1] / len(self.tiles),
            )
        )
        self.TileType.set_values_to_pics(pygame, self.blocks_base_path, self.tile_size)
        self.map_size = (self.tile_size * len(self.tiles[0]), self.tile_size * len(self.tiles))
        self._set_background_image(self._background_image_unscaled, pygame)
        self.x_offset = int((pygame.display.get_window_size()[0] - self.map_size[0]) / 2)
        self.y_offset = int((pygame.display.get_window_size()[1] - self.map_size[1]) / 2)
        self._calculate_spawn_positions()
        self.render_arena(pygame)

    def load_map_from_json(self, filename, pygame):
        try:
            self._load_map_from_json_helper(filename, pygame)
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            UnicodeDecodeError,
            ValueError,
        ):
            Screens.show_popup("File not found or Corrupted! Loading emptyMap.")
            self._load_map_from_json_helper("emptyMap.json", pygame)

    def _load_map_from_json_helper(self, filename, pygame):
        with open(self.maps_base_path + filename, "r") as f:
            data = json.load(f)
            self.num_tiles_x = data["num_tiles_x"]
            self.num_tiles_y = data["num_tiles_y"]
            self.tiles = [[Arena.TileType[tile] for tile in row] for row in data["tiles"]]
            self._background_image_unscaled = pygame.image.load(
                self.maps_base_path + data["background_image"]
            ).convert()
            self._background_image_filename = self.maps_base_path + data["background_image"]
            self._spawn_positions_unscaled = data["spawn_positions_unscaled"]

    def _calculate_spawn_positions(self):
        self.spawn_positions = []
        for pos in self._spawn_positions_unscaled:
            self.spawn_positions.append(
                [pos[0] * self.tile_size + self.x_offset, pos[1] * self.tile_size + self.y_offset]
            )

    def _set_background_image(self, image, pygame):
        self.background_image = pygame.transform.scale(image, self.map_size)

    def render_arena(self, pygame):
        # Erstelle eine Surface für das gerenderte Arena-Bild
        self.rendered_arena = pygame.Surface(self.map_size)

        # Blitte das Hintergrundbild auf die Surface
        self.rendered_arena.blit(self.background_image, (0, 0))

        # Blitte die Tiles auf die Surface
        y = 0
        for row in self.tiles:
            x = 0
            for tile in row:
                if tile.filename != "Air.png" and tile.filename != "Spawn.png":
                    self.rendered_arena.blit(tile.image, (x, y))
                x += self.tile_size
            y += self.tile_size

    def paint_arena(self, screen):
        """
        Paints the pre-rendered arena onto the screen.

        :param screen: screen element of pygame initialized with pygame.display.set_mode()
        """
        screen.blit(self.rendered_arena, (self.x_offset, self.y_offset))

    def is_solid(self, x_positions, y_positions):
        for x in x_positions:
            for y in y_positions:
                if x < 0 or y < 0 or x >= self.num_tiles_x or y >= self.num_tiles_y:
                    return False
                elif self.tiles[y][x].solid:
                    return True
        return False
