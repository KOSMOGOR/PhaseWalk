import pygame
import sys
import os
from random import choice, randint


pygame.init()
pygame.key.set_repeat(200, 70)
FPS = 48
size = WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
MAP_COUNT = 0
font30 = pygame.font.Font('data\\18036.otf', 30)
font60 = pygame.font.Font('data\\18036.otf', 60)
songs = ['Nickelback - Burn it to the ground.mp3', 'Nickelback - Home.mp3', 'Shinedown - Devil.mp3',
         'Phaserland - Resemblance in Machine.mp3', 'Panda Eyes & Teminite - Highscore.mp3',
         "You reposted in everyone's neighorhood.mp3"]
song_index = 0
gravity = 0.25


def load_level(filename):
    filename = os.path.join('data', filename)
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


beforereturn = 0
buttonsremain = 0
ticks = FPS * 4
needrender = None
nowkey = None
lastkey = None
text = 'waiting'
def start_qte():
    global running
    buttons = [
        [pygame.transform.scale(load_image('W.png'), (100, 100)), pygame.K_w],
        [pygame.transform.scale(load_image('A.png'), (100, 100)), pygame.K_a],
        [pygame.transform.scale(load_image('S.png'), (100, 100)), pygame.K_s],
        [pygame.transform.scale(load_image('D.png'), (100, 100)), pygame.K_d],
        [pygame.transform.scale(load_image('M.png'), (100, 100)), pygame.K_m],
        [pygame.transform.scale(load_image('L.png'), (100, 100)), pygame.K_l],
    ]

    def get_new_button():
        global needrender, nowkey, lastkey
        key = choice(list(filter(lambda x: x[1] != nowkey, buttons)))
        needrender = [key[0], [250, 150]]# [randint(0, WIDTH - 100), randint(50, HEIGHT - 100)]]
        lastkey, nowkey = nowkey, key[1]

    def reset():
        global buttonsremain, needrender, nowkey, lastkey, beforereturn
        buttonsremain = 0
        needrender = None
        nowkey = None
        lastkey = None
        beforereturn = FPS * 2

    buttonsremain = 4
    ticks = FPS * 4
    beforereturn = 0
    get_new_button()
    while True:
        pygame.draw.rect(screen, 'black', [200, 100, 200, 200])
        for event in pygame.event.get():
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT or key[pygame.K_ESCAPE]:
                running = False
            if nowkey and key[nowkey]:
                buttonsremain -= 1
                if buttonsremain > 0:
                    get_new_button()
                else:
                    return True
            elif nowkey and any(key):
                if not lastkey or (lastkey and not key[lastkey]):
                    text = 'bad'
                    return False
        if beforereturn > 0:
            beforereturn -= 1
        elif buttonsremain > 0:
            ticks -= 1
        if ticks == 0:
            return False
        if needrender:
            screen.blit(needrender[0], needrender[1])
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    #    image = image.convert_alpha()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}

player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
phase_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
effect_group = pygame.sprite.Group()
tile_width = tile_height = 50
phase_staff = None


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, type1):
        super().__init__(enemy_group if type1 == 'enemy' else player_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.update_count = 4

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.update_count -= 1
        if self.update_count == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.update_count = 4


class Board:
    def __init__(self, width, height, player_pos, board, enemies):
        self.width = width
        self.height = height
        self.board = board
        self.left = 0
        self.top = 0
        self.xsize = len(board[0])
        self.ysize = len(board)
        self.cell_size = tile_width
        self.x, self.y = player_pos[0], player_pos[1]
        self.player = AnimatedSprite(pygame.transform.scale(load_image('hero_w.png'), [600, 50]), 12, 1, self.x * 50,
                                     self.y * 50, 'player')
        self.enemies = enemies

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        tiles_group.draw(screen)
        phase_group.draw(screen)
        effect_group.draw(screen)
        x, y = self.x * self.cell_size, self.y * self.cell_size
        self.player.rect.topleft = [x, y]
        player_group.draw(screen)

    def update(self):
        self.player.update()
        for i in self.enemies:
            i[0].update()

    def can_move(self, delta_x, delta_y):
        y, x = self.y + delta_y, self.x + delta_x
        if [x, y] in [x[1] for x in self.enemies]:
            return 'die'
        elif x >= WIDTH // self.cell_size or x < 0 or y >= HEIGHT // self.cell_size or y < 0 or self.board[y][x].can_move:
            return True
        return False

    def move(self, delta_x, delta_y):
        self.x, self.y = self.x + delta_x, self.y + delta_y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, can_move=True):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.can_move = can_move
        self.can_pick_up = False


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(effect_group)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = gravity

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 50
    # возможные скорости
    numbers = range(-6, 6)
    for _ in range(particle_count):
        Particle(position, choice(numbers), choice(numbers))


class Phase_staff(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(phase_group)
        self.pos_y = pos_y
        self.image = img
        self.pos_x = pos_x
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.can_pick_up = True

    def win_rule(self, board):
        if board.x == self.pos_x and board.y == self.pos_y:
            create_particles((board.x * board.cell_size, board.y * board.cell_size))
            phase_group.empty()
            self.pos_x = self.pos_y = 0


def generate_level(level):
    global phase_staff
    new_player, x, y, board = None, None, None, []
    player_pos = [0, 0]
    enemies = []
    for y in range(len(level)):
        a = []
        for x in range(len(level[y])):
            if level[y][x] == '.':
                a.append(Tile('empty', x, y))
            elif level[y][x] == '#':
                a.append(Tile('wall', x, y, False))
            elif level[y][x] == '@':
                a.append(Tile('empty', x, y))
                player_pos = [x, y]
            elif level[y][x] == '*':
                a.append(Tile('empty', x, y))
                phase_staff = Phase_staff(load_image('phase_art.png'), x, y)
            elif level[y][x] == '1':
                a.append(Tile('empty', x, y))
                enemies.append([AnimatedSprite(pygame.transform.scale(load_image('phase_enemy_1_w.png'),
                                                              [600, 50]), 12, 1, x * 50, y * 50, 'enemy'), [x, y]])
        board.append(a)
    # вернем игрока, а также размер поля в клетках
    return x, y, Board(WIDTH, HEIGHT, player_pos, board, enemies)


level_x, level_y, board = generate_level(load_level(f'map{MAP_COUNT}.txt'))
start_screen()


def player_moves(key):
    global board, MAP_COUNT, phase_staff, dead
    delta_x, delta_y = 0, 0
    if key[pygame.K_s]:
        delta_x, delta_y = 0, 1
    elif key[pygame.K_w]:
        delta_x, delta_y = 0, -1
    elif key[pygame.K_d]:
        delta_x, delta_y = 1, 0
    elif key[pygame.K_a]:
        delta_x, delta_y = -1, 0

    a = board.can_move(delta_x, delta_y)
    if a == 'die':
        board.move(delta_x, delta_y)
        dead = True
    elif not a:
        return
    elif delta_x and board.x <= 0 or board.x + 1 >= board.xsize:
        MAP_COUNT += delta_x
        enemy_group.empty()
        player_group.empty()
        phase_group.empty()
        phase_staff = None
        level_x, level_y, board = generate_level(load_level(f'map{MAP_COUNT}.txt'))
    else:
        board.move(delta_x, delta_y)
        if phase_staff:
            phase_staff.win_rule(board)
        


screen_rect = (0, 0, WIDTH, HEIGHT)


is_playing = False
onpause = False
spacedown = False
pausedown = False
running = True
dead = False
while running:
    for event in pygame.event.get():
        key = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not onpause:
                player_moves(key)
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p and not pausedown:
                onpause = not onpause
                pausedown = True
            elif event.key == pygame.K_q:
                dead = not start_qte()
            elif onpause:
                if key[pygame.K_UP] and song_index + 1 < len(songs):
                    song_index += 1
                elif key[pygame.K_DOWN] and song_index > 0:
                    song_index -= 1
            elif key[pygame.K_SPACE] and not spacedown and onpause:
                if not is_playing:
                    # print('playing')
                    spacedown = True
                    pygame.mixer.music.load(f'data\\{songs[song_index]}')
                    pygame.mixer.music.play(0)
                    is_playing = True
                else:
                    # print('stopped')
                    pygame.mixer.music.stop()
                    is_playing = False
                    spacedown = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                pausedown = False
            if event.key == pygame.K_SPACE:
                spacedown = False
    screen.fill('black')
    board.render(screen)
    enemy_group.draw(screen)
    if dead:
        text = font60.render('Вы умерли', False, (255, 255, 255))
        screen.blit(text, [170, 150, 0, 0])
    elif not onpause:
        board.update()
        effect_group.update()
    else:
        pygame.draw.rect(screen, 'black', [10, 10, 580, 90])
        text = font30.render(songs[song_index], False, (255, 255, 225))
        screen.blit(text, (10, 10, 580, 90))
        pygame.display.update()
        # print(is_playing, spacedown)
    clock.tick(FPS)
    pygame.display.flip()
terminate()
