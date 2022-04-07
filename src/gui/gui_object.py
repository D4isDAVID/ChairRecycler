import pygame


class GuiObject:
    def __init__(self,
                 pos: tuple[int, int],
                 image: pygame.Surface) -> None:
        self.pos = pygame.Vector2(*pos)
        self.image = image

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.pos)

    def hover(self) -> None:
        pass

    def unhover(self) -> None:
        pass

    def click(self) -> None:
        pass

    def unclick(self) -> None:
        pass
