import pygame
from .gui_object import GuiObject


class Button(GuiObject):
    def __init__(self,
                 pos: tuple[float, float],
                 image: pygame.Surface,
                 pressed_image: pygame.Surface) -> None:
        super().__init__(pos, image)
        self.original_image = image
        self.pressed_image = pressed_image

    def hover(self) -> None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def unhover(self) -> None:
        self.image = self.original_image
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def click(self) -> None:
        self.image = self.pressed_image

    def unclick(self) -> None:
        self.image = self.original_image
