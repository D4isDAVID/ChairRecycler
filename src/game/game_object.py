import pygame


class GameObject:
    def __init__(self, pos: tuple[float, float],
                 image: pygame.Surface, hitbox: tuple[float, float, float, float] = None) -> None:
        self.pos = pygame.Vector2(*pos)
        self.image = image
        self.hitbox = hitbox and pygame.Rect(*hitbox) or pygame.Rect(0, 0, image.get_width(), image.get_height())

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.pos)
        # pygame.draw.rect(surface, (255, 0, 0),
        #                  (self.pos.x+self.hitbox.x, self.pos.y+self.hitbox.y, self.hitbox.w, self.hitbox.h), 4)

    def update(self) -> None:
        pass
