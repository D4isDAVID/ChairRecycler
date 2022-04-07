import os
import pygame
from gui import Button, GuiObject


def to_screen_scale(surface: pygame.Surface):
    global multiplier
    return pygame.transform.scale(surface, (surface.get_width()*multiplier, surface.get_height()*multiplier))


width, height = resolution = (1920, 1080)
multiplier = width/384

pygame.init()
window = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
running = True

assets: dict[str, pygame.Surface] = {}
for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', 'buttons')):
    name = file.name.split('.')[0]
    assets[f'button_{name}'] = to_screen_scale(pygame.image.load(file.path).convert_alpha())

sounds: dict[str, pygame.mixer.Sound] = {}
for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', 'sounds')):
    name = file.name.split('.')[0]
    sounds[name] = pygame.mixer.Sound(file.path)

gui: dict[str, GuiObject] = {}
gui['play'] = Button(
    (width/2-assets['button_play'].get_width()/2, height/2),
    assets['button_play'],
    assets['button_play_pressed']
)
gui['info'] = Button(
    (gui['play'].pos.x, height/2+gui['play'].image.get_height()+10),
    assets['button_info'],
    assets['button_info_pressed']
)
gui['options'] = Button(
    (gui['play'].pos.x+gui['play'].image.get_width()/2-assets['button_options'].get_width()/2,height/2+gui['play'].image.get_height()+10),
    assets['button_options'],
    assets['button_options_pressed']
)
gui['exit'] = Button(
    (gui['play'].pos.x+gui['play'].image.get_width()-assets['button_exit'].get_width(), height/2+gui['play'].image.get_height()+10),
    assets['button_exit'],
    assets['button_exit_pressed']
)

hover: GuiObject | None = None

sounds['main menu'].play(-1)
while running:
    window.fill((255, 255, 255))

    for obj in gui.values():
        obj.draw(window)

    clock.tick(60)
    pygame.display.flip()

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.MOUSEMOTION:
                x = event.pos[0]
                y = event.pos[1]
                new_hover = None
                for obj in gui.values():
                    if obj.pos.x < x < obj.pos.x+obj.image.get_width() \
                            and obj.pos.y < y < obj.pos.y + obj.image.get_height():
                        new_hover = obj
                        obj.hover()
                        break
                if hover and hover is not new_hover:
                    hover.after_hover()
                hover = new_hover
            case pygame.MOUSEBUTTONDOWN:
                if hover:
                    hover.click()
            case pygame.MOUSEBUTTONUP:
                if hover:
                    hover.after_click()

pygame.quit()
