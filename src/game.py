import os
import random
import pygame
import json
from game import GameObject, Player, Obstacle
from gui import Button, GuiObject


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+/,.`~;\\ '
WIDTH, HEIGHT = RESOLUTION = 1280, 720
FPS = 60
MULTIPLIER = 4

high_score = 0
try:
    with open('highscore') as f:
        high_scores: list = json.load(f)
        f = True
        for s in high_scores:
            sc = int(s[1])
            if f:
                f = False
                high_score = sc
            if sc > high_score:
                high_score = sc
except FileNotFoundError or OSError:
    high_scores = []


def to_screen_scale(surface: pygame.Surface):
    return pygame.transform.scale(surface, (surface.get_width() * MULTIPLIER, surface.get_height() * MULTIPLIER))


rates = {
    'obstacle': 2,
    'recycle': 2
}

max_values = {
    'chair': 8,
    'bottle': 8
}

pygame.init()
window = pygame.display.set_mode(RESOLUTION, vsync=1)
clock = pygame.time.Clock()
running = True

game_font_big = pygame.font.SysFont('Arial', 100)
game_font_medium = pygame.font.SysFont('Arial', 50)
game_font_small = pygame.font.SysFont('Arial', 25)

high_score_text: pygame.Surface | None = None
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
            i = pygame.transform.flip(i, True, False)
            assets[f'{prefix}{name}2'] = i
        except pygame.error:
            try:
                sounds[name] = pygame.mixer.Sound(file.path)
            except pygame.error:
                pass


load_assets()

obstacles: tuple[Obstacle, ...] = (
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_chair_side'].get_height()),
             assets['obstacle_chair_side'], 'chair'),
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_chair_side2'].get_height()),
             assets['obstacle_chair_side2'], 'chair'),
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_table_side'].get_height()),
             assets['obstacle_table_side'], 'table'),
    Obstacle((WIDTH+Obstacle.velocity, HEIGHT - HEIGHT / MULTIPLIER - assets['obstacle_table_side2'].get_height()),
             assets['obstacle_table_side2'], 'table'),
)
recycle_obs: tuple[Obstacle, ...] = (
    Obstacle((WIDTH+Obstacle.velocity*1.5*100, HEIGHT - HEIGHT / MULTIPLIER - assets['bottle_bottle'].get_height()),
             assets['bottle_bottle'], 'bottle'),
    Obstacle((WIDTH+Obstacle.velocity*1.5*100, HEIGHT - HEIGHT / MULTIPLIER - assets['bottle_can'].get_height()),
             assets['bottle_can'], 'bottle'),
    Obstacle((WIDTH+Obstacle.velocity*1.5*100, HEIGHT - HEIGHT / MULTIPLIER - assets['recycle_bin'].get_height()),
             assets['recycle_bin'], 'bin')
)


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
    gui_objects['info'].after_click = leaderboard
    gui_objects['exit'].after_click = stop_game
    grey_box = pygame.Surface((WIDTH, HEIGHT / MULTIPLIER))
    grey_box.fill((75, 75, 75))
    game_objects['ground'] = GameObject((0, HEIGHT - HEIGHT / MULTIPLIER), grey_box)
    game_objects['player'] = GameObject((WIDTH / MULTIPLIER,
                                         game_objects['ground'].pos.y - assets['player_front'].get_height()),
                                        assets['player_front'])
    sounds['main_menu'].play(-1)


def game():
    global scene, bg_color, gui_objects, game_objects, player, game_started, score, high_score, high_score_text,\
        bottles, chairs, lives, bottles_recycled, chairs_flipped, name
    name = ''
    bottles_recycled = 0
    chairs_flipped = 0
    high_score_text = game_font_small.render(f'High Score: {str(round(high_score))}', True, (255, 255, 255))
    chairs = 0
    bottles = 0
    lives = 3
    score = 0
    game_started = pygame.time.get_ticks() - 1000
    unload_scene()
    scene = 'game'
    bg_color = pygame.Color(125, 125, 125)
    grey_box = pygame.Surface((WIDTH, HEIGHT / MULTIPLIER))
    grey_box.fill((75, 75, 75))
    game_objects['ground'] = GameObject((0, HEIGHT - HEIGHT / MULTIPLIER), grey_box)
    player = game_objects['player'] = Player(WIDTH / MULTIPLIER, game_objects['ground'].pos.y, assets['player_side'],
                                             assets['player_holding'])
    sounds['go'].play(-1)


def lose():
    global gui_objects, scene
    scene = 'lose'
    for k in list(game_objects.keys()):
        obj = game_objects[k]
        if isinstance(obj, Obstacle):
            obj.velocity = 0
    bottles_recycled_text = game_font_small.render(f'Bottles Recycled: {bottles_recycled}', True, (255, 255, 255))
    chairs_flipped_text = game_font_small.render(f'Chairs Flipped: {chairs_flipped}', True, (255, 255, 255))
    gui_objects = {
        'high_score': GuiObject((WIDTH/2-high_score_text.get_width()/2, HEIGHT/6), high_score_text),
        'bottles': GuiObject((WIDTH/2-bottles_recycled_text.get_width()/2, HEIGHT/6-high_score_text.get_height()),
                             bottles_recycled_text),
        'chairs': GuiObject((WIDTH/2-chairs_flipped_text.get_width()/2,
                             HEIGHT/6-high_score_text.get_height()-bottles_recycled_text.get_height()),
                            chairs_flipped_text),
        'retry': Button((WIDTH / 2 + assets['button_retry'].get_width(), HEIGHT / 2),
                        assets['button_retry'], assets['button_retry_pressed']),
        'back': Button((WIDTH / 2 - assets['button_back'].get_width()*1.5, HEIGHT / 2),
                       assets['button_back'], assets['button_back_pressed'])
    }
    gui_objects['retry'].after_click = game
    gui_objects['back'].after_click = main_menu


def leaderboard():
    global gui_objects, scene
    unload_scene()
    scene = 'leaderboard'
    gui_objects = {
        'back': Button((0, 0),
                       assets['button_back'], assets['button_back_pressed'])
    }
    gui_objects['back'].after_click = main_menu
    xl = 0
    yl = HEIGHT/8
    i = 0

    for names, score in high_scores:
        t = game_font_medium.render(f'{names}: {score}', True, (255, 255, 255))
        gui_objects[f'score{i}'] = GuiObject((xl, yl), t)
        yl += game_font_medium.get_height()
        i += 1


intro_alpha = 1
delta_alpha = 3
game_started = 0
score = 0
lives = 3
bottles = 0
chairs = 0
bottles_recycled = 0
chairs_flipped = 0
name = ''

intro()
while running:
    delta_time = clock.tick(FPS) / 1000 * FPS
    window.fill(bg_color)

    colliding = None
    for k, obj in list(game_objects.items()):
        obj.update(delta_time)
        obj.draw(window)
        if obj.pos.x + obj.image.get_width() < 0:
            if isinstance(obj, Obstacle):
                if obj.type == 'chair':
                    lives -= 1
                    if lives <= 0:
                        lose()
                elif obj.type == 'bottle':
                    score -= 150
            del game_objects[k]
        if isinstance(obj, Obstacle) and (colliding is None) and obj.collides_with(player):
            colliding = k
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
        offset = 0
        for i in range(chairs - 1):
            offset += 4 * MULTIPLIER
            window.blit(
                assets['obstacle_chair_side2'],
                (player.pos.x + player.image.get_width(), player.pos.y - offset)
            )
        player.max_velocity = Player.max_velocity - (player.velocity_add * bottles)
        score_text = game_font_medium.render(f'Score: {str(round(score))}', True, (255, 255, 255))
        bottles_text = game_font_small.render(f'Bottles: {str(bottles)}', True, (255, 255, 255))
        chairs_text = game_font_small.render(f'Chairs: {str(chairs)}', True, (255, 255, 255))
        lives_text = game_font_small.render(f'Lives: {str(lives)}', True, (255, 255, 255))
        name_text = game_font_small.render(f'Name: {str(name)}', True, (255, 255, 255))
        if score > high_score:
            high_score = score
            high_score_text = game_font_small.render(f'High Score: {str(round(high_score))}', True, (255, 255, 255))
        window.blit(bottles_text, (WIDTH/2-bottles_text.get_width(), HEIGHT/7))
        window.blit(chairs_text, (WIDTH/2+chairs_text.get_width(), HEIGHT/7))
        window.blit(score_text, (WIDTH/2-score_text.get_width()/2, HEIGHT/7+bottles_text.get_height()))
        window.blit(high_score_text, (WIDTH/2-high_score_text.get_width()/2, HEIGHT/7+bottles_text.get_height()+score_text.get_height()))
        window.blit(lives_text, (player.pos.x-lives_text.get_width()/2, player.pos.y-lives_text.get_height()))
    elif scene == 'lose':
        name_text = game_font_small.render(f'Name: {name}', True, (255, 255, 255))
        window.blit(name_text, (WIDTH/4, HEIGHT-HEIGHT/4))

    if scene == 'game' and (time := (pygame.time.get_ticks() - game_started) // 1000) % rates['obstacle'] == 0:
        if f'obs{str(time)}' not in game_objects.keys():
            game_objects[f'obs{str(time)}'] = random.choice(obstacles).copy()

    if scene == 'game' and (time := (pygame.time.get_ticks() - game_started) // 1000) % rates['recycle'] == 0:
        if f'bottle{str(time)}' not in game_objects.keys():
            game_objects[f'bottle{str(time)}'] = random.choice(recycle_obs).copy()

    # fps = game_font_big.render(str(round(clock.get_fps())), True, (255, 255, 255))
    # window.blit(fps, (WIDTH-fps.get_width(), HEIGHT-fps.get_height()))
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
                if scene == 'lose':
                    if event.key == pygame.K_RETURN and name != '':
                        high_scores.append([name, str(score)])
                        main_menu()
                    elif event.key == pygame.K_ESCAPE:
                        main_menu()
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode in ALPHABET:
                        name += event.unicode
                elif scene == 'main_menu' and event.key == pygame.K_SPACE:
                    gui_objects['play'].after_click()
                elif scene == 'main_menu' and event.key == pygame.K_ESCAPE:
                    gui_objects['exit'].after_click()
                elif scene == 'intro':
                    main_menu()
                elif scene == 'game' and colliding is not None and event.key == pygame.K_SPACE:
                    if game_objects[colliding].type == 'chair' and chairs < max_values['chair']:
                        del game_objects[colliding]
                        player.hold()
                        if 'holding' not in list(game_objects.keys()):
                            game_objects['holding'] = GameObject(
                                (player.pos.x+player.image.get_width(), player.pos.y),
                                assets['obstacle_chair_side2']
                            )
                        chairs += 1
                    elif game_objects[colliding].type == 'bottle' and bottles < max_values['bottle']:
                        del game_objects[colliding]
                        bottles += 1
                    elif game_objects[colliding].type == 'table' and 'holding' in game_objects.keys():
                        score += 100
                        chairs -= 1
                        col = game_objects[colliding].copy()
                        hol = game_objects['holding'].copy()
                        game_objects['table'] = Obstacle(col.pos, col.image, '')
                        game_objects['placed'] = Obstacle(
                            (col.pos.x-4*MULTIPLIER, col.pos.y-18*MULTIPLIER),
                            pygame.transform.flip(hol.image, False, True), ''
                        )
                        if chairs <= 0:
                            chairs = 0
                            player.place()
                            del game_objects['holding']
                        del game_objects[colliding]
                    elif game_objects[colliding].type == 'bin':
                        score += 25 * bottles
                        bottles = 0


with open('highscore', 'w') as f:
    json.dump(high_scores, f)
pygame.quit()
