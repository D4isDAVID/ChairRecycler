import os
import random
import pygame
from game import GameObject, Player, Obstacle
from gui import Button, GuiObject


WIDTH, HEIGHT = RESOLUTION = 1920, 1080
FPS = 60
MULTIPLIER = 5
MAX_VELOCITY = 27

try:
    with open('highscore') as f:
        high_score = int(f.read())
except FileNotFoundError or OSError:
    high_score = 0
print(high_score)


def to_screen_scale(surface: pygame.Surface):
    return pygame.transform.scale(surface, (surface.get_width() * MULTIPLIER, surface.get_height() * MULTIPLIER))


pygame.init()
window = pygame.display.set_mode(RESOLUTION, vsync=1)
clock = pygame.time.Clock()
running = True

hover: GuiObject | None = None
scene: str | None = None
player: Player | None = None
bg_color: pygame.Color | None = None
game_objects: dict[str, GameObject] = {}
gui_objects: dict[str, GuiObject] = {}

sounds: dict[str, pygame.mixer.Sound] = {}
assets: dict[str, pygame.Surface] = {}


def load_assets(prefix: str = '', *paths: list[str]):
    global assets, sounds
    if prefix != '':
        prefix += '_'
    for file in os.scandir(os.path.join(os.path.dirname(__file__), 'assets', *paths)):
        name = file.name.split('.')[0]
        if file.is_dir():
            load_assets(f'{prefix}{name}', *paths, name)
            continue
        try:
            i = to_screen_scale(pygame.image.load(file.path).convert_alpha())
            assets[f'{prefix}{name}'] = i
        except pygame.error:
            sounds[name] = pygame.mixer.Sound(file.path)


load_assets()


def stop_game():
    global running
    running = False


def unload_scene():
    global game_objects, gui_objects, hover
    hover = None
    game_objects = {}
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
    gui_objects['aharaitech'] = GuiObject((WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2), text)
    text2 = font_small.render('Presents...', True, (255, 255, 255))
    gui_objects['presents'] = GuiObject((WIDTH / 2 + text2.get_width(), HEIGHT / 2 + text.get_height() / 3), text2)
    gui_objects['aharaitech'].image.set_alpha(0)


def main_menu():
    global scene, bg_color, gui_objects
    unload_scene()
    scene = 'main_menu'
    bg_color = pygame.Color(125, 125, 125)
    gui_objects['logo'] = GuiObject((WIDTH / 2 - assets['logo'].get_width() / 2,
                                     HEIGHT / 3 - assets['logo'].get_height() / 2),
                                    assets['logo'])
    gui_objects['play'] = Button(
        (WIDTH / 2 - assets['button_play'].get_width() / 2, HEIGHT / 2),
        assets['button_play'],
        assets['button_play_pressed']
    )
    gui_objects['info'] = Button(
        (gui_objects['play'].pos.x, HEIGHT / 2 + gui_objects['play'].image.get_height() + 10),
        assets['button_info'],
        assets['button_info_pressed']
    )
    gui_objects['options'] = Button(
        (gui_objects['play'].pos.x
         + gui_objects['play'].image.get_width() / 2
         - assets['button_options'].get_width() / 2,
         HEIGHT / 2 + gui_objects['play'].image.get_height() + 10),
        assets['button_options'],
        assets['button_options_pressed']
    )
    gui_objects['exit'] = Button(
        (gui_objects['play'].pos.x + gui_objects['play'].image.get_width() - assets['button_exit'].get_width(),
         HEIGHT / 2 + gui_objects['play'].image.get_height() + 10),
        assets['button_exit'],
        assets['button_exit_pressed']
    )
    gui_objects['play'].after_click = game
    gui_objects['exit'].after_click = stop_game
    grey_box = pygame.Surface((WIDTH, HEIGHT / MULTIPLIER))
    grey_box.fill((75, 75, 75))
    game_objects['ground'] = GameObject((0, HEIGHT - HEIGHT / MULTIPLIER), grey_box)
    game_objects['player'] = GameObject((WIDTH / MULTIPLIER,
                                         game_objects['ground'].pos.y - assets['player_front'].get_height()),
                                        assets['player_front'])
    sounds['main_menu'].play(-1)


def game():
    global scene, bg_color, gui_objects, game_objects, player, game_started, score, high_score, high_score_text
    high_score_text = game_font_small.render(f'High Score: {str(round(high_score))}', True, (255, 255, 255))
    score = 0
    Obstacle.velocity = 10
    game_started = pygame.time.get_ticks()
    unload_scene()
    scene = 'game'
    bg_color = pygame.Color(125, 125, 125)
    grey_box = pygame.Surface((WIDTH, HEIGHT / MULTIPLIER))
    grey_box.fill((75, 75, 75))
    game_objects['ground'] = GameObject((0, HEIGHT - HEIGHT / MULTIPLIER), grey_box)
    player = game_objects['player'] = Player(WIDTH / MULTIPLIER, game_objects['ground'].pos.y, assets['player_side'],
                                             assets['player_side'], pygame.transform.rotate(assets['player_side'], 90))
    sounds['go'].play(-1)


obstacles: tuple[Obstacle, ...] = (
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_chair_side'].get_height()),
             assets['obstacle_chair_side'], (4 * MULTIPLIER,
                                             6 * MULTIPLIER,
                                             12 * MULTIPLIER,
                                             37 * MULTIPLIER)),
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_chair_side'].get_height()),
             pygame.transform.flip(assets['obstacle_chair_side'], True, False),
             (1 * MULTIPLIER,
              6 * MULTIPLIER,
              12 * MULTIPLIER,
              37 * MULTIPLIER)),
)
intro_alpha = 1
delta_alpha = 3
intro()
game_started = 0
score = 0
game_font_big = pygame.font.SysFont('Arial', 100)
game_font_medium = pygame.font.SysFont('Arial', 75)
game_font_small = pygame.font.SysFont('Arial', 40)
high_score_text: pygame.Surface | None = None
while running:
    delta_time = clock.tick() / 1000 * FPS
    window.fill(bg_color)

    for k, obj in list(game_objects.items()):
        obj.update(delta_time)
        obj.draw(window)
        if obj.pos.x + obj.image.get_width() < 0:
            del game_objects[k]
        if isinstance(obj, Obstacle):
            if obj.collides_with(player):
                main_menu()
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
    elif scene == 'game':
        score += delta_time
        score_text = game_font_medium.render(f'Score: {str(round(score))}', True, (255, 255, 255))
        if score > high_score:
            high_score = score
            high_score_text = game_font_small.render(f'High Score: {str(round(high_score))}', True, (255, 255, 255))
        window.blit(score_text, (WIDTH/2-score_text.get_width()/2, HEIGHT/7))
        window.blit(high_score_text, (WIDTH/2-high_score_text.get_width()/2, HEIGHT/7+score_text.get_height()))

    if scene == 'game' and (time := (pygame.time.get_ticks() - game_started) // 1000) % 2 == 0:
        if f'obs{str(time)}' not in game_objects.keys():
            game_objects[f'obs{str(time)}'] = random.choice(obstacles).copy()
            if Obstacle.velocity < MAX_VELOCITY:
                Obstacle.velocity += 0.1

    fps = game_font_big.render(str(round(clock.get_fps())), True, (255, 255, 255))
    window.blit(fps, (WIDTH-fps.get_width(), HEIGHT-fps.get_height()))
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
                    if obj.pos.x < x < obj.pos.x + obj.image.get_width() \
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


with open('highscore', 'w') as f:
    f.write(str(round(high_score)))
pygame.quit()
