import pygame
from .game_object import GameObject


class Player(GameObject):
    max_velocity = 8
    velocity_add = 0.40

    def __init__(self, x: float, ground_y: float, image: pygame.Surface,
                 jump_image: pygame.Surface, slide_image: pygame.Surface) -> None:
        super().__init__((x, ground_y-image.get_height()), image)
        self.original_image = image
        self.original_hitbox = self.hitbox
        self.jump_image = jump_image
        self.slide_image = slide_image
        self.slide_hitbox = pygame.Rect(0, 0, slide_image.get_width(), slide_image.get_height())
        self.ground_y = ground_y
        self.velocity = self.max_velocity
        self.jumping = False
        self.sliding = False

    def jump(self):
        self.jumping = True
        self.image = self.jump_image

    def stop_jumping(self):
        self.jumping = False
        self.image = self.original_image
        self.velocity = self.max_velocity
        self.pos.y = self.ground_y - self.image.get_height()

    def slide(self):
        self.sliding = True
        self.image = self.slide_image
        self.hitbox = self.slide_hitbox
        self.pos.y = self.ground_y - self.image.get_height()

    def stop_sliding(self):
        self.sliding = False
        self.image = self.original_image
        self.hitbox = self.original_hitbox
        self.pos.y = self.ground_y - self.image.get_height()

    def update(self, delta_time: float):
        if self.jumping:
            self.pos.y -= self.velocity * 4 * delta_time
            self.velocity -= self.velocity_add * delta_time
            if self.ground_y < self.pos.y + self.image.get_height():
                self.stop_jumping()
