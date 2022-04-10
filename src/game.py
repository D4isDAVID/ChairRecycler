import os
import pygame
from game import GameObject, Player
from gui import Button, GuiObject


WIDTH, HEIGHT = RESOLUTION = (1920, 1080)
FPS = 60
MULTIPLIER = 5


def to_screen_scale(surface: pygame.Surface):
    return pygame.transform.scale(surface, (surface.get_width()*MULTIPLIER, surface.get_height()*MULTIPLIER))


pygame.init()
window = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
running = True

hover: GuiObject | None = None
scene: str | None = None
player: Player | None = None
obstacles: Player | None = None
bg_color: pygame.Color | None = None
game_objects: dict[str, GameObject] = {}
gui_objects: dict[str, GuiObject] = {}

assets: dict[str, pygame.Surface] = {}
for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', 'buttons')):
    name = file.name.split('.')[0]
    assets[f'button_{name}'] = to_screen_scale(pygame.image.load(file.path).convert_alpha())
for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', 'player')):
    name = file.name.split('.')[0]
    assets[f'player_{name}'] = to_screen_scale(pygame.image.load(file.path).convert_alpha())

sounds: dict[str, pygame.mixer.Sound] = {}
for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', 'sounds')):
    name = file.name.split('.')[0]
    sounds[name] = pygame.mixer.Sound(file.path)


def stop_game():
    global running
    running = False


def unload_scene():
    global gui_objects, hover
    hover = None
    gui_objects = {}
    pygame.mixer.stop()
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


def intro():
    global scene, bg_color, gui_objects
    unload_scene()
    scene = 'intro'
    bg_color = pygame.Color(0, 0, 0)
    font_big = pygame.font.SysFont('Arial', 100, True)
    font_small = pygame.font.SysFont('Arial', 50)
    text = font_big.render('AharaiTech Tel-Aviv', True, (255, 255, 255))
    gui_objects['aharaitech'] = GuiObject((WIDTH/2-text.get_width()/2, HEIGHT/2-text.get_height()/2), text)
    text2 = font_small.render('Presents...', True, (255, 255, 255))
    gui_objects['presents'] = GuiObject((WIDTH/2+text2.get_width(), HEIGHT/2+text.get_height()/3), text2)
    gui_objects['aharaitech'].image.set_alpha(0)


def main_menu():
    global scene, bg_color, gui_objects
    unload_scene()
    scene = 'main_menu'
    bg_color = pygame.Color(255, 255, 255)
    gui_objects['play'] = Button(
        (WIDTH/2-assets['button_play'].get_width()/2, HEIGHT/2),
        assets['button_play'],
        assets['button_play_pressed']
    )
    gui_objects['info'] = Button(
        (gui_objects['play'].pos.x, HEIGHT/2+gui_objects['play'].image.get_height()+10),
        assets['button_info'],
        assets['button_info_pressed']
    )
    gui_objects['options'] = Button(
        (gui_objects['play'].pos.x+gui_objects['play'].image.get_width()/2-assets['button_options'].get_width()/2,
         HEIGHT/2+gui_objects['play'].image.get_height()+10),
        assets['button_options'],
        assets['button_options_pressed']
    )
    gui_objects['exit'] = Button(
        (gui_objects['play'].pos.x+gui_objects['play'].image.get_width()-assets['button_exit'].get_width(),
         HEIGHT/2+gui_objects['play'].image.get_height()+10),
        assets['button_exit'],
        assets['button_exit_pressed']
    )
    gui_objects['play'].after_click = game
    gui_objects['exit'].after_click = stop_game
    sounds['main_menu'].play(-1)


def game():
    global scene, bg_color, gui_objects, game_objects, player
    unload_scene()
    scene = 'game'
    bg_color = pygame.Color(255, 255, 255)
    grey_box = pygame.Surface((WIDTH, HEIGHT/MULTIPLIER))
    grey_box.fill((100, 100, 100))
    game_objects['ground'] = GameObject((0, HEIGHT-HEIGHT/MULTIPLIER), grey_box)
    player = game_objects['player'] = Player(WIDTH/MULTIPLIER, game_objects['ground'].pos.y, assets['player_side'],
                                             assets['player_side'], pygame.transform.rotate(assets['player_side'], 90))
    sounds['go'].play(-1)


intro_alpha = 1
delta_alpha = 3
intro()
while running:
    delta_time = clock.tick(FPS) / 1000 * FPS
    window.fill(bg_color)

    for obj in game_objects.values():
        obj.update(delta_time)
        obj.draw(window)
    for obj in gui_objects.values():
        obj.draw(window)

    if scene == 'intro':
        intro_alpha += delta_alpha * delta_time
        gui_objects['aharaitech'].image.set_alpha(intro_alpha)
        gui_objects['presents'].image.set_alpha(intro_alpha)
        if intro_alpha >= 255:
            delta_alpha = -delta_alpha
        if intro_alpha <= -10:
            main_menu()

    pygame.display.flip()

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                stop_game()
            case pygame.MOUSEMOTION:
                x = event.pos[0]
                y = event.pos[1]
                new_hover = None
                for obj in gui_objects.values():
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
            case pygame.KEYDOWN:
                if scene == 'intro':
                    main_menu()
                if scene == 'game' and event.key == pygame.K_UP and not player.jumping:
                    if player.sliding:
                        player.stop_sliding()
                    player.jump()
            case pygame.KEYUP:
                if scene == 'game' and event.key == pygame.K_DOWN and player.sliding:
                    player.stop_sliding()
    if scene == 'game' and pygame.key.get_pressed()[pygame.K_DOWN] and not player.jumping and not player.sliding:
        player.slide()

pygame.quit()
