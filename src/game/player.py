import pygame
from .game_object import GameObject


class Player(GameObject):
    max_velocity = 8
    velocity_add = 0.45

    def __init__(self, x: float, ground_y: float, image: pygame.Surface,
                 hold_image: pygame.Surface) -> None:
        super().__init__((x, ground_y-image.get_height()), image)
        self.original_image = image
        self.hold_image = hold_image
        self.ground_y = ground_y
        self.velocity = self.max_velocity
        self.holding = False

    def hold(self):
        self.holding = True
        self.image = self.hold_image
        self.pos.y = self.ground_y - self.image.get_height()

    def place(self):
        self.holding = False
        self.image = self.original_image
        self.pos.y = self.ground_y - self.image.get_height()
