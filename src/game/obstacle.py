import pygame
from .game_object import GameObject


class Obstacle(GameObject):
    velocity = 10

    def __init__(self, pos: tuple[float, float], image: pygame.Surface, obs_type: str) -> None:
        super().__init__(pos, image)
        self.type = obs_type

    def collides_with(self, other: GameObject):
        return self.get_world_hitbox().colliderect(other.get_world_hitbox())

    def update(self, delta_time: float) -> None:
        self.pos.x -= self.velocity * delta_time

    def copy(self):
        obs = Obstacle(self.pos, self.image, self.hitbox)
        obs.collide = self.collide
        obs.type = self.type
        return obs

    def collide(self, *args, **kwargs):
        pass
