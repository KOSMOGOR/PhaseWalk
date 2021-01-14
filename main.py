import pygame
import sys
import os

pygame.init()
pygame.key.set_repeat(200, 70)
FPS = 50
size = WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
MAP_COUNT = 0


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

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
phase_group = pygame.sprite.Group()
tile_width = tile_height = 50
phase_staff = None


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def get_rect(self):
        return self.rect


class Board:
    def __init__(self, width, height, player_pos, board):
        self.width = width
        self.height = height
        self.board = board
        self.left = 0
        self.top = 0
        self.xsize = len(board[0])
        self.ysize = len(board)
        self.cell_size = tile_width
        self.player_pos = player_pos
        self.player = load_image("mar.png")

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        tiles_group.draw(screen)
        phase_group.draw(screen)
        x, y = self.player_pos[0] * self.cell_size + 15, self.player_pos[1] * self.cell_size + 5
        screen.blit(self.player, [x, y])

    def can_move(self, delta_x, delta_y):
        y, x = self.player_pos[1] + delta_y, self.player_pos[0] + delta_x
        if x >= WIDTH // self.cell_size or y >= HEIGHT // self.cell_size or self.board[y][x].can_move:
            return True
        return False

    def move(self, delta_x, delta_y):
        self.player_pos = [self.player_pos[0] + delta_x, self.player_pos[1] + delta_y]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, can_move=True):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.can_move = can_move
        self.can_pick_up = False


class Phase_staff(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(phase_group, all_sprites)
        self.pos_y = pos_y
        self.image = img
        self.pos_x = pos_x
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.can_pick_up = True

    def win_rule(self, board):
        if board.player_pos[0] == self.pos_x and board.player_pos[1] == self.pos_y:
            phase_group.empty()
            print('You win!')


def generate_level(level):
    global phase_staff
    new_player, x, y, board = None, None, None, []
    player_pos = [0, 0]
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
        board.append(a)
    # вернем игрока, а также размер поля в клетках
    return x, y, Board(WIDTH, HEIGHT, player_pos, board)


level_x, level_y, board = generate_level(load_level(f'map{MAP_COUNT}.txt'))
start_screen()


def player_moves(key):
    global board, MAP_COUNT, phase_staff
    if key[pygame.K_DOWN] and board.can_move(0, 1):
        board.move(0, 1)
        if phase_staff:
            phase_staff.win_rule(board)
    elif key[pygame.K_UP] and board.can_move(0, -1):
        board.move(0, -1)
        if phase_staff:
            phase_staff.win_rule(board)
    elif key[pygame.K_RIGHT] and board.can_move(1, 0):
        if board.player_pos[0] + 1 >= board.xsize:
            MAP_COUNT += 1
            level_x, level_y, board = generate_level(load_level(f'map{MAP_COUNT}.txt'))
        else:
            board.move(1, 0)
            if phase_staff:
                phase_staff.win_rule(board)
    elif key[pygame.K_LEFT] and board.can_move(-1, 0):
        if board.player_pos[0] <= 0:
            MAP_COUNT -= 1
            level_x, level_y, board = generate_level(load_level(f'map{MAP_COUNT}.txt'))
            phase_group.empty()
            phase_staff = None
        else:
            board.move(-1, 0)
            if phase_staff:
                phase_staff.win_rule(board)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        player_moves(key)
    screen.fill(pygame.Color("black"))
    board.render(screen)
    pygame.display.flip()
terminate()