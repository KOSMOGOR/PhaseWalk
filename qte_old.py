import pygame

pygame.init()
pygame.display.set_caption('Phase walk')
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
screen.fill('black')


def render_text(string, num):
    font = pygame.font.Font(None, 30)

    string_rendered = font.render(str(num), 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.topleft = [10, 10]
    screen.blit(string_rendered, intro_rect)
    string_rendered = font.render(string, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.topleft = [60, 10]
    screen.blit(string_rendered, intro_rect)


running = True
nowqte = False
fps = 12
ticks = -fps / 2
beforereturn = 0
text = 'waiting'
clock = pygame.time.Clock()
while running:
    screen.fill('black')
    if nowqte:
        ticks += 1
    if beforereturn > 0:
        beforereturn -= 1
    elif not nowqte:
        text = 'waiting'
        ticks = -fps / 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            nowqte = True
            ticks = -fps / 2
            beforereturn = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not nowqte:
                continue
            nowqte = False
            beforereturn = fps * 2
            if abs(ticks) <= 1:
                text = 'excellent'
            elif abs(ticks) <= 3:
                text = 'good'
            elif abs(ticks) <= 6:
                text = 'not good'
    if ticks > fps / 2:
        nowqte = False
        text = 'bad'
        ticks = -fps / 2
    render_text(text, ticks)

    clock.tick(fps)
    pygame.display.flip()
pygame.quit()