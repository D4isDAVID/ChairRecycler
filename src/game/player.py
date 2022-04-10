import pygame
from .game_object import GameObject


class Player(GameObject):
    max_velocity = 15
    velocity_add = 1
    slide_add = 0.1
    max_slide = 5

    def __init__(self, x: float, ground_y: float, image: pygame.Surface) -> None:
        super().__init__((x, ground_y-image.get_height()), image)
        self.ground_y = ground_y
        self.velocity = self.max_velocity
        self.slide_timer = self.max_slide
        self.jumping = False
        self.sliding = False

    def update(self):
        if self.jumping:
            self.pos.y -= self.velocity * 4
            self.velocity -= self.velocity_add
            if self.velocity < -self.max_velocity and self.ground_y < self.pos.y + self.image.get_height():
                self.pos.y = self.ground_y - self.image.get_height()
                self.jumping = False
                self.velocity = self.max_velocity
        if self.sliding:
            if self.slide_timer == self.max_slide:
                temp = self.hitbox.w
                self.hitbox.w = self.hitbox.h
                self.hitbox.h = temp
                self.pos.y += self.image.get_height()/2
            self.slide_timer -= self.slide_add
            if self.slide_timer <= 0:
                self.sliding = False
                self.slide_timer = self.max_slide
                self.pos.y -= self.image.get_height()/2
                temp = self.hitbox.w
                self.hitbox.w = self.hitbox.h
                self.hitbox.h = temp
