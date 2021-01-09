import pygame
import os
from random import choice, randint

pygame.init()
pygame.display.set_caption('Phase walk')
size = WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode(size)
screen.fill('black')


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def render_text(string, num):
    global beforereturn
    font = pygame.font.Font(None, 30)

    string_rendered = font.render(str(num), 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.topleft = [10, 10]
    screen.blit(string_rendered, intro_rect)
    string_rendered = font.render(string, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.topleft = [60, 10]
    screen.blit(string_rendered, intro_rect)


def get_new_button():
    global needrender, nowkey
    key = choice(list(filter(lambda x: x[1] != nowkey, buttons)))
    needrender = [key[0], [randint(0, WIDTH - 100), randint(50, HEIGHT - 100)]]
    lastkey, nowkey = nowkey, key[1]


def reset():
    global buttonsremain, needrender, nowkey, lastkey, beforereturn
    buttonsremain = 0
    needrender = None
    nowkey = None
    lastkey = None
    beforereturn = fps * 2


buttons = [
    [pygame.transform.scale(load_image('W.png'), (100, 100)), pygame.K_w],
    [pygame.transform.scale(load_image('A.png'), (100, 100)), pygame.K_a],
    [pygame.transform.scale(load_image('S.png'), (100, 100)), pygame.K_s],
    [pygame.transform.scale(load_image('D.png'), (100, 100)), pygame.K_d],
    [pygame.transform.scale(load_image('M.png'), (100, 100)), pygame.K_m],
    [pygame.transform.scale(load_image('L.png'), (100, 100)), pygame.K_l],
]

fps = 12
beforereturn = 0
buttonsremain = 0
ticks = fps * 4
needrender = None
nowkey = None
lastkey = None
text = 'waiting'
clock = pygame.time.Clock()
running = True
while running:
    screen.fill('black')
    if beforereturn > 0:
        beforereturn -= 1
    elif buttonsremain == 0:
        text = 'waiting'
    elif buttonsremain > 0:
        ticks -= 1
    if ticks == 0:
        text = 'bad'
        reset()
    if needrender:
        screen.blit(needrender[0], needrender[1])


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            buttonsremain = 4
            ticks = fps * 4
            text = 'now qte'
            beforereturn = 0
            get_new_button()
        elif nowkey and key[nowkey]:
            buttonsremain -= 1
            if buttonsremain > 0:
                get_new_button()
            else:
                text = 'good'
                reset()
        elif lastkey and nowkey and any(key) and not key[nowkey] and not key[lastkey]:
            text = 'bad'
            reset()


    render_text(text, ticks)

    clock.tick(fps)
    pygame.display.flip()
pygame.quit()