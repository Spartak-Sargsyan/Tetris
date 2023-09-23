import pygame
from copy import deepcopy
from random import choice, randrange

import os

W, H = 10, 20
TILE = 39
GAME_RASE = W * TILE, H * TILE
RES = 750, 800
FPS = 60

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RASE)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figure_pos = [
               [(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]
              ]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figure_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]


anim_count, anim_speed, anim_limit = 0, 60, 2000


#
bg = pygame.image.load('./img/bg.jpg').convert()
game = pygame.image.load('./img/bg2.jpg').convert()

main_font_path = os.path.join(os.path.dirname(__file__), './font', 'font.ttf')

main_font = pygame.font.Font('./font/font.ttf', 65)
font = pygame.font.Font('./font/font.ttf', 45)

pygame.mixer.music.load("./music/1Shot2.mp3")

title_teris = main_font.render("TETRIS", True, pygame.Color("darkorange"))
title_score = font.render("score:", True, pygame.Color("green"))
title_record = font.render("record:", True, pygame.Color("purple"))


get_color = lambda : (randrange(30, 56), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {
    0: 0,
    1: 100,
    2: 300,
    3: 700,
    4: 1500
}

def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

def get_record():
    try:
        with open("record") as f:
            return  f.readline()
    except FileNotFoundError:
        with open("record", "w") as f:
            f.write("0")

def set_record(record, score):
    rec = max(int(record), score)
    with open("record", "w") as f:
        f.write(str(rec))

pygame.mixer.music.play()
while True:
    record = get_record()
    dx, rotate = 0, False

    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game, (0, 0))

    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_SPACE:
                anim_limit = 150
            elif event.key == pygame.K_UP:
                rotate = True

    #move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break

    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break

    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1

    # compute score
    score += scores[lines]

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)

    # draw titles
    sc.blit(title_teris, (485, 0))
    sc.blit(title_score, (485, 600))
    sc.blit(font.render(str(score), True, pygame.Color("white")), (550, 660))
    sc.blit(title_record, (485, 450))
    sc.blit(font.render(record, True, pygame.Color("gold")), (550, 510))

    # gmae over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)


    pygame.display.flip()
    clock.tick(FPS)

