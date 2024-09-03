import pygame


class Explosion:

    duration: int
    damage: int
    rectangle: pygame.Rect

    def __init__(self, dur, dmg, rect):
        self.duration = dur
        self.damage = dmg
        self.rectangle = rect

    def reduce_duration(self):
        self.duration = self.duration - 1
