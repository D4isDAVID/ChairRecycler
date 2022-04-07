import pygame


class GuiObject:
    def __init__(self,
                 pos: tuple[float, float],
                 image: pygame.Surface) -> None:
        self.pos = pygame.Vector2(*pos)
        self.image = image

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.pos)

    def hover(self) -> None:
        pass

    def after_hover(self) -> None:
        pass

    def click(self) -> None:
        pass

    def after_click(self) -> None:
        pass
