import tkinter as tk
from tkinter import messagebox


class Screens:
    class MenuItem:
        def __init__(self, text, textcolor, font, dist_mult, display_resolution):
            dist_between_elements = display_resolution[1] / 20
            self.text = font.render(text, True, textcolor)
            self.rect = self.text.get_rect(
                center=(display_resolution[0] // 2, display_resolution[1] // 2 + dist_mult * dist_between_elements)
            )
            self.selected = False
            self.pressed = False

        def draw(self, screen, pygame, color, display_resolution):
            rect_inflate_x = display_resolution[0] / 50
            rect_inflate_y = display_resolution[1] / 50
            if self.selected:
                color = (130, 130, 130)
            pygame.draw.rect(screen, color, self.rect.inflate(rect_inflate_x, rect_inflate_y))
            screen.blit(self.text, self.rect)

    _black = (0, 0, 0)
    _white = (255, 255, 255)

    def __init__(self, pygame, available_resolutions, json_filenames):
        self._display_resolution = pygame.display.get_window_size()
        self._dist_between_elements = self._display_resolution[1] / 20
        self._input_fields_x_size = self._display_resolution[0] / 12
        self._input_fields_y_size = self._display_resolution[1] / 33
        self._input_text_offset_x = self._display_resolution[0] / 200
        self._input_text_offset_y = self._display_resolution[1] / 200
        self._rect_inflate_x = self._display_resolution[0] / 50
        self._rect_inflate_y = self._display_resolution[1] / 50
        self._font_size_big = int(self._display_resolution[1] / 16)
        self._font_size_small = int(self._display_resolution[1] / 25)
        self._initialize_menu_items(pygame, available_resolutions, json_filenames)

    def _initialize_menu_items(self, pygame, available_resolutions, json_filenames):
        font = pygame.font.Font(None, self._font_size_small)
        self.death_screen_items = [
            self.MenuItem("Main Menu", self._black, font, 2, self._display_resolution),
            self.MenuItem("Quit Game", self._black, font, 3, self._display_resolution),
        ]
        self.pause_screen_items = [
            self.MenuItem("Resume", self._white, font, 1, self._display_resolution),
            self.MenuItem("Main Menu", self._white, font, 2, self._display_resolution),
            self.MenuItem("Quit Game", self._white, font, 3, self._display_resolution),
        ]
        self.main_menu_items = [
            self.MenuItem("Play", self._white, font, 1, self._display_resolution),
            self.MenuItem("Build Arena", self._white, font, 2, self._display_resolution),
            self.MenuItem("Settings", self._white, font, 3, self._display_resolution),
            self.MenuItem("Exit", self._white, font, 4, self._display_resolution),
        ]
        self.settings_menu_items = []
        self.settings_menu_items.append(
            self.MenuItem("Controller On/Off", self._white, font, -1, self._display_resolution)
        )
        for i, res in enumerate(available_resolutions):
            self.settings_menu_items.append(
                self.MenuItem(f"{res[0]}x{res[1]}", self._white, font, i, self._display_resolution)
            )
        self.settings_menu_items.append(self.MenuItem("Fullscreen", self._white, font, 4, self._display_resolution))
        self.settings_menu_items.append(self.MenuItem("Back", self._white, font, 5, self._display_resolution))
        self.build_arena_menu_items = [self.MenuItem("Start Building", self._white, font, 3, self._display_resolution)]
        self.start_screen_items = [
            self.MenuItem("1", self._white, font, 1, self._display_resolution),
            self.MenuItem("2", self._white, font, 2, self._display_resolution),
            self.MenuItem("3", self._white, font, 3, self._display_resolution),
            self.MenuItem("4", self._white, font, 4, self._display_resolution),
        ]
        self.level_menu_items = []
        for i, filename in enumerate(json_filenames):
            self.level_menu_items.append(self.MenuItem(filename, self._white, font, i, self._display_resolution))
        self.win_screen_items = [
            self.MenuItem("Main Menu", self._white, font, 2, self._display_resolution),
            self.MenuItem("Quit Game", self._white, font, 3, self._display_resolution),
        ]

    def death_screen(self, pygame, screen):
        screen.fill(self._black)

        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("You Died!", True, (101, 28, 50))
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2,
            ),
        )

        for item in self.death_screen_items:
            item.draw(screen, pygame, self._white, self._display_resolution)

        return self.death_screen_items

    def pause_screen(self, pygame, screen):
        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Paused Game", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2,
            ),
        )

        for item in self.pause_screen_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.pause_screen_items

    def main_menu_screen(self, pygame, screen):
        screen.fill(self._white)

        for item in self.main_menu_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.main_menu_items

    def settings_screen(self, pygame, screen):
        screen.fill(self._white)

        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Settings", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2 - 3 * self._dist_between_elements,
            ),
        )

        for item in self.settings_menu_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.settings_menu_items

    def build_arena_screen(self, pygame, screen, x_tiles, y_tiles):
        screen.fill(self._white)

        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Number x tiles:", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2 - 2 * self._dist_between_elements,
            ),
        )

        # Set up text input field for number x tiles
        input_rect_x_tiles = pygame.Rect(
            self._display_resolution[0] // 2 - text.get_width() // 2,
            self._display_resolution[1] // 2 - text.get_height() // 2 - self._dist_between_elements,
            self._input_fields_x_size,
            self._input_fields_y_size,
        )

        pygame.draw.rect(screen, self._black, input_rect_x_tiles)
        text_surface = pygame.font.SysFont(None, 24).render(x_tiles, True, self._white)
        screen.blit(
            text_surface,
            (input_rect_x_tiles.x + self._input_text_offset_x, input_rect_x_tiles.y + self._input_text_offset_y),
        )

        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Number y tiles:", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2,
            ),
        )

        # Set up text input field for number y tiles
        input_rect_y_tiles = pygame.Rect(
            self._display_resolution[0] // 2 - text.get_width() // 2,
            self._display_resolution[1] // 2 - text.get_height() // 2 + self._dist_between_elements,
            self._input_fields_x_size,
            self._input_fields_y_size,
        )

        pygame.draw.rect(screen, self._black, input_rect_y_tiles)
        text_surface = pygame.font.SysFont(None, 24).render(y_tiles, True, self._white)
        screen.blit(
            text_surface,
            (input_rect_y_tiles.x + self._input_text_offset_x, input_rect_y_tiles.y + self._input_text_offset_y),
        )

        for item in self.build_arena_menu_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return input_rect_x_tiles, input_rect_y_tiles, self.build_arena_menu_items

    def start_screen(self, pygame, screen):
        screen.fill(self._white)
    
        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Wie viele Spieler?", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2 - 2 * self._dist_between_elements,
            ),
        )

        for item in self.start_screen_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.start_screen_items

    def maps_screen(self, pygame, screen):
        screen.fill(self._white)

        font = pygame.font.Font(None, self._font_size_big)
        text = font.render("Welches Level möchten Sie spielen?", True, self._black)
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2 - 3 * self._dist_between_elements,
            ),
        )

        # Anzeige der JSON-Dateinamen
        for item in self.level_menu_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.level_menu_items

    def win_screen(self, pygame, screen, robot):

        font = pygame.font.Font(None, self._font_size_big)

        text = font.render("Player " + str(robot.player_number + 1) + " hat gewonnen!", True, f"{robot.color}")
        screen.blit(
            text,
            (
                self._display_resolution[0] // 2 - text.get_width() // 2,
                self._display_resolution[1] // 2 - text.get_height() // 2 - 3 * self._dist_between_elements,
            ),
        )

        # Anzeige der JSON-Dateinamen
        for item in self.win_screen_items:
            item.draw(screen, pygame, self._black, self._display_resolution)

        return self.win_screen_items

    @staticmethod
    def show_popup(message):
        root = tk.Tk()
        root.withdraw()  # Verstecke das Haupt-Tkinter-Fenster
        messagebox.showinfo("", message)
        root.destroy()
