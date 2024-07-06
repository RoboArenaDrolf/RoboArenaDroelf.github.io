import json
from tkinter import filedialog, Tk
import shutil
import os
from arena import Arena
from screens import Screens


class ArenaBuilder(Arena):

    # Set up colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 200, 0)
    GREY = (100, 100, 100)
    RED = (255, 0, 0)

    def __init__(self, num_tiles_x, num_tiles_y, pygame):
        filename = self._set_up_empty_map(num_tiles_x, num_tiles_y)
        self._set_up_basics(filename, pygame)
        self._set_up_paint_related()

    def _set_up_empty_map(self, num_tiles_x, num_tiles_y):
        self.num_tiles_x = num_tiles_x
        self.num_tiles_y = num_tiles_y
        self.tiles = [[self.TileType.AIR for _ in range(self.num_tiles_x)] for _ in range(self.num_tiles_y)]
        self._spawn_positions_unscaled = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self._background_image_filename = super().maps_base_path + "emptyMap.png"
        filename = "emptyMap.json"
        self.save_to_json(filename)
        return filename

    def _set_up_basics(self, filename, pygame):
        screen_size = pygame.display.get_window_size()
        flags = pygame.display.get_surface().get_flags()
        self._legend_space = screen_size[0] / 5
        pygame.display.set_mode((screen_size[0] - self._legend_space, screen_size[1]))
        super().__init__(filename, pygame)
        self.x_offset = 0
        self.y_offset = 0
        self._calculate_spawn_positions()
        self.pygame = pygame
        if bool(flags & pygame.FULLSCREEN):
            self.screen = self.pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
        else:
            self.screen = self.pygame.display.set_mode(screen_size)
        if filename == "emptyMap.json":
            self._reset_spawn_positions()

    def _set_up_paint_related(self):
        # Set up scaled sizes
        display_resolution = self.pygame.display.get_window_size()
        self._max_x_of_map = self.num_tiles_x * self.tile_size
        self._max_y_of_map = self.num_tiles_y * self.tile_size
        self._x_of_legend = self._max_x_of_map + display_resolution[0] / 50
        self._y_of_legend_end = display_resolution[0] / 5
        self._dist_between_elements = display_resolution[1] / 20
        elements_x_size = display_resolution[0] / 6
        input_fields_y_size = display_resolution[1] / 33
        buttons_y_size = display_resolution[1] / 25
        self._button_text_x_offset = display_resolution[0] / 100
        self._button_text_y_offset = display_resolution[1] / 100
        self._input_text_x_offset = display_resolution[0] / 200
        self._input_text_y_offset = display_resolution[1] / 200
        self._legend_spacing = display_resolution[1] / 50
        # Set up font
        self._font = self.pygame.font.SysFont(None, int(display_resolution[1] / 40))
        self._text_color = self.WHITE
        # Set up reset spawn positions button
        self._reset_button_text = self._font.render("Reset Spawns", True, self.WHITE)
        self._reset_button_rect = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end, elements_x_size, buttons_y_size
        )
        # Set up text input field for saving
        self._input_text_saving = ""
        self._input_active_saving = False
        self._input_rect_saving = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end + self._dist_between_elements, elements_x_size, input_fields_y_size
        )
        # Set up save button
        self._save_button_text = self._font.render("Save Map", True, self.WHITE)
        self._save_button_rect = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end + 2 * self._dist_between_elements, elements_x_size, buttons_y_size
        )
        # Set up text input field for loading map
        self._input_text_loading_map = ""
        self._input_active_loading_map = False
        self._input_rect_loading_map = self.pygame.Rect(
            self._x_of_legend,
            self._y_of_legend_end + 3 * self._dist_between_elements,
            elements_x_size,
            input_fields_y_size,
        )
        # Set up load map button
        self._load_map_button_text = self._font.render("Load Map", True, self.WHITE)
        self._load_map_button_rect = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end + 4 * self._dist_between_elements, elements_x_size, buttons_y_size
        )
        # Set up load background image button
        self._load_background_button_text = self._font.render("Load Image", True, self.WHITE)
        self._load_background_button_rect = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end + 5 * self._dist_between_elements, elements_x_size, buttons_y_size
        )
        # Set up exit button
        self._exit_button_text = self._font.render("Exit", True, self.WHITE)
        self._exit_button_rect = self.pygame.Rect(
            self._x_of_legend, self._y_of_legend_end + 6 * self._dist_between_elements, elements_x_size, buttons_y_size
        )

    def main(self):
        running = True
        current_tile = self.TileType.GRASS
        mouse_pressed = False
        save_button_clicked = False
        load_map_button_clicked = False
        load_background_button_clicked = False
        reset_button_clicked = False
        button_click_time_saving = 0
        button_click_time_loading_map = 0
        button_click_time_loading_background = 0
        button_click_time_reset = 0

        # Main loop
        while running:
            # Clear the self.screen
            self.screen.fill(self.BLACK)

            # Paint the arenaBuilder
            self._paint_arena_builder(
                save_button_clicked, load_map_button_clicked, load_background_button_clicked, reset_button_clicked
            )

            # Update the display
            self.pygame.display.flip()

            current_time = self.pygame.time.get_ticks()

            # Handle events
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
                elif event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    (
                        button_click_time_loading_map,
                        button_click_time_saving,
                        load_map_button_clicked,
                        mouse_pressed,
                        save_button_clicked,
                        running,
                        load_background_button_clicked,
                        button_click_time_loading_background,
                        reset_button_clicked,
                        button_click_time_reset,
                    ) = self._handle_mouse_button_down(
                        button_click_time_loading_map,
                        button_click_time_saving,
                        current_time,
                        load_map_button_clicked,
                        save_button_clicked,
                        running,
                        load_background_button_clicked,
                        button_click_time_loading_background,
                        reset_button_clicked,
                        button_click_time_reset,
                    )
                elif event.type == self.pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button released
                    mouse_pressed = False
                elif event.type == self.pygame.KEYDOWN:
                    current_tile = self._handle_key_down(current_tile, event)

            if mouse_pressed:
                self._paint_tile(current_tile)

            if save_button_clicked and current_time - button_click_time_saving >= 200:
                save_button_clicked = False

            if load_map_button_clicked and current_time - button_click_time_loading_map >= 200:
                load_map_button_clicked = False

            if load_background_button_clicked and current_time - button_click_time_loading_background >= 200:
                load_background_button_clicked = False

            if reset_button_clicked and current_time - button_click_time_reset >= 200:
                reset_button_clicked = False

    def _paint_tile(self, current_tile):
        x, y = self.pygame.mouse.get_pos()
        x //= self.tile_size
        y //= self.tile_size
        if x < self.num_tiles_x and y < self.num_tiles_y:
            if current_tile == self.TileType.SPAWN and [x, y] not in self._spawn_positions_unscaled:
                self.set_spawn_position(x, y)
            else:
                self.set_tile(x, y, current_tile)
            self.render_arena(self.pygame)

    def set_tile(self, x, y, tile_type):
        self.tiles[y][x] = tile_type

    def set_spawn_position(self, x, y):
        if len(self.spawn_positions) < 4:
            self._spawn_positions_unscaled.append([x, y])
            self.spawn_positions.append([x * self.tile_size + self.x_offset, y * self.tile_size + self.y_offset])

    def _reset_spawn_positions(self):
        self._spawn_positions_unscaled = []
        self.spawn_positions = []

    def _handle_key_down(self, current_tile, event):
        if self._input_active_saving:
            if event.key == self.pygame.K_RETURN:
                self._input_active_saving = False
                self._save_map()
            elif event.key == self.pygame.K_BACKSPACE:
                self._input_text_saving = self._input_text_saving[:-1]
            else:
                self._input_text_saving += event.unicode
        elif self._input_active_loading_map:
            if event.key == self.pygame.K_RETURN:
                self._input_active_loading_map = False
                self._load_map()
            elif event.key == self.pygame.K_BACKSPACE:
                self._input_text_loading_map = self._input_text_loading_map[:-1]
            else:
                self._input_text_loading_map += event.unicode
        elif event.key == self.pygame.K_1:
            current_tile = self.TileType.AIR
        elif event.key == self.pygame.K_2:
            current_tile = self.TileType.GRASS
        elif event.key == self.pygame.K_3:
            current_tile = self.TileType.ICE
        elif event.key == self.pygame.K_4:
            current_tile = self.TileType.SAND
        elif event.key == self.pygame.K_5:
            current_tile = self.TileType.LAVA
        elif event.key == self.pygame.K_6:
            current_tile = self.TileType.BIRCH
        elif event.key == self.pygame.K_7:
            current_tile = self.TileType.LEAVES
        elif event.key == self.pygame.K_8:
            current_tile = self.TileType.SPAWN
        return current_tile

    def _handle_mouse_button_down(
        self,
        button_click_time_loading_map,
        button_click_time_saving,
        current_time,
        load_map_button_clicked,
        save_button_clicked,
        running,
        load_background_button_clicked,
        button_click_time_loading_background,
        reset_button_clicked,
        button_click_time_reset,
    ):
        mouse_pressed = True
        mouse_pos = self.pygame.mouse.get_pos()
        if self._reset_button_rect.collidepoint(mouse_pos):
            reset_button_clicked = True
            button_click_time_reset = current_time
            self._reset_spawn_positions()
        elif self._save_button_rect.collidepoint(mouse_pos):
            save_button_clicked = True
            button_click_time_saving = current_time
            self._save_map()
        elif self._load_map_button_rect.collidepoint(mouse_pos):
            load_map_button_clicked = True
            button_click_time_loading_map = current_time
            self._load_map()
        elif self._exit_button_rect.collidepoint(mouse_pos):
            running = False
        elif self._load_background_button_rect.collidepoint(mouse_pos):
            load_background_button_clicked = True
            button_click_time_loading_background = current_time
            self._load_background()
        elif self._input_rect_saving.collidepoint(mouse_pos):
            self._input_active_saving = True
            self._input_active_loading_map = False
        elif self._input_rect_loading_map.collidepoint(mouse_pos):
            self._input_active_loading_map = True
            self._input_active_saving = False
        else:
            self._input_active_saving = False
            self._input_active_loading_map = False
        return (
            button_click_time_loading_map,
            button_click_time_saving,
            load_map_button_clicked,
            mouse_pressed,
            save_button_clicked,
            running,
            load_background_button_clicked,
            button_click_time_loading_background,
            reset_button_clicked,
            button_click_time_reset,
        )

    def _load_map(self):
        map_name = self._input_text_loading_map
        filename = map_name + ".json"
        self._set_up_basics(filename, self.pygame)
        self._set_up_paint_related()
        self._input_text_saving = map_name

    def _save_map(self):
        if len(self.spawn_positions) == 4:
            self.save_to_json(self._input_text_saving + ".json")
        else:
            Screens.show_popup("You need to set all 4 Spawn positions first!")

    def _paint_arena_builder(
        self, save_button_clicked, load_map_button_clicked, load_background_button_clicked, reset_button_clicked
    ):
        """
        Paints the arena defined by tiles with a grid
        and a legend of possible tiles as well as other fields
        """
        self.paint_arena(self.screen)
        self._draw_grid()
        self._draw_legend()
        self._draw_input_fields()
        self._draw_buttons(
            load_map_button_clicked, save_button_clicked, load_background_button_clicked, reset_button_clicked
        )
        self._draw_spawn_positions()

    def _draw_buttons(
        self, load_map_button_clicked, save_button_clicked, load_background_button_clicked, reset_button_clicked
    ):
        # Draw reset spawn positions button
        if reset_button_clicked:
            self.pygame.draw.rect(self.screen, self.DARK_GREEN, self._reset_button_rect)
        else:
            self.pygame.draw.rect(self.screen, self.GREEN, self._reset_button_rect)
        self.screen.blit(
            self._reset_button_text,
            (
                self._reset_button_rect.x + self._button_text_x_offset,
                self._reset_button_rect.y + self._button_text_y_offset,
            ),
        )
        # Draw save button
        if save_button_clicked:
            self.pygame.draw.rect(self.screen, self.DARK_GREEN, self._save_button_rect)
        else:
            self.pygame.draw.rect(self.screen, self.GREEN, self._save_button_rect)
        self.screen.blit(
            self._save_button_text,
            (
                self._save_button_rect.x + self._button_text_x_offset,
                self._save_button_rect.y + self._button_text_y_offset,
            ),
        )
        # Draw load map button
        if load_map_button_clicked:
            self.pygame.draw.rect(self.screen, self.DARK_GREEN, self._load_map_button_rect)
        else:
            self.pygame.draw.rect(self.screen, self.GREEN, self._load_map_button_rect)
        self.screen.blit(
            self._load_map_button_text,
            (
                self._load_map_button_rect.x + self._button_text_x_offset,
                self._load_map_button_rect.y + self._button_text_y_offset,
            ),
        )
        # Draw load background button
        if load_background_button_clicked:
            self.pygame.draw.rect(self.screen, self.DARK_GREEN, self._load_background_button_rect)
        else:
            self.pygame.draw.rect(self.screen, self.GREEN, self._load_background_button_rect)
        self.screen.blit(
            self._load_background_button_text,
            (
                self._load_background_button_rect.x + self._button_text_x_offset,
                self._load_background_button_rect.y + self._button_text_y_offset,
            ),
        )
        # Draw exit button
        self.pygame.draw.rect(self.screen, self.RED, self._exit_button_rect)
        self.screen.blit(
            self._exit_button_text,
            (
                self._exit_button_rect.x + self._button_text_x_offset,
                self._exit_button_rect.y + self._button_text_y_offset,
            ),
        )

    def _draw_input_fields(self):
        # Draw text input field saving
        self.pygame.draw.rect(self.screen, self.BLACK, self._input_rect_saving)
        self.pygame.draw.rect(self.screen, self._text_color, self._input_rect_saving, 2)
        text_surface = self._font.render(self._input_text_saving, True, self._text_color)
        self.screen.blit(
            text_surface,
            (
                self._input_rect_saving.x + self._input_text_x_offset,
                self._input_rect_saving.y + self._input_text_y_offset,
            ),
        )
        # Draw text input field loading
        self.pygame.draw.rect(self.screen, self.BLACK, self._input_rect_loading_map)
        self.pygame.draw.rect(self.screen, self._text_color, self._input_rect_loading_map, 2)
        text_surface = self._font.render(self._input_text_loading_map, True, self._text_color)
        self.screen.blit(
            text_surface,
            (
                self._input_rect_loading_map.x + self._input_text_y_offset,
                self._input_rect_loading_map.y + self._input_text_y_offset,
            ),
        )

    def _draw_legend(self):
        legend_surface = self.pygame.Surface((self._legend_space, self.screen.get_height()))
        legend_surface.fill((0, 0, 0))
        legend_pos = (self._x_of_legend, self._button_text_y_offset)
        for idx, tile_type in enumerate(self.TileType):
            legend_text = f"{idx + 1}: {tile_type.name}"
            text_surface = self._font.render(legend_text, True, self._text_color)
            legend_surface.blit(text_surface, (self._button_text_x_offset, legend_pos[1] + idx * self._legend_spacing))
        self.screen.blit(legend_surface, (self._max_x_of_map, 0))

    def _draw_grid(self):
        for x in range(0, self._max_x_of_map, self.tile_size):
            self.pygame.draw.line(self.screen, self.GREY, (x, 0), (x, self._max_y_of_map))
        for y in range(0, self._max_y_of_map + self.tile_size, self.tile_size):
            self.pygame.draw.line(self.screen, self.GREY, (0, y), (self._max_x_of_map, y))

    def _draw_spawn_positions(self):
        FONT_SIZE = int(self.tile_size)
        font = self.pygame.font.SysFont(None, FONT_SIZE)
        for i, pos in enumerate(self.spawn_positions):
            text = font.render(str(i + 1), True, self.BLACK)  # Rendere den Text (Schwarz)
            text_rect = text.get_rect(center=(pos[0] + self.tile_size // 2, pos[1] + self.tile_size // 2))
            self.screen.blit(text, text_rect)

    def _load_background(self):
        filename = self._open_file_dialog()
        if filename != "":
            self._background_image_filename = filename
            image = self.pygame.image.load(self._background_image_filename).convert()
            self._set_background_image(image, self.pygame)

    def _open_file_dialog(self):
        root = Tk()
        root.withdraw()  # Versteckt das Hauptfenster

        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")], title="Select an Image"
        )
        return file_path

    # Speichere die Daten in einer JSON-Datei
    def save_to_json(self, filename):
        _, file_extension = os.path.splitext(self._background_image_filename)
        map_name, _ = os.path.splitext(filename)
        try:
            shutil.copy(self._background_image_filename, os.getcwd() + self.maps_base_path + map_name + file_extension)
        except shutil.SameFileError:
            shutil.move(self._background_image_filename, os.getcwd() + self.maps_base_path + map_name + file_extension)
        data = {
            "num_tiles_x": self.num_tiles_x,
            "num_tiles_y": self.num_tiles_y,
            "background_image": map_name + file_extension,
            "spawn_positions_unscaled": self._spawn_positions_unscaled,
            "tiles": [[tile.name for tile in row] for row in self.tiles],
        }
        with open(self.maps_base_path + filename, "w") as f:
            json.dump(data, f)
