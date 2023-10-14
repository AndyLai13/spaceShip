import os
import random

import pygame
from pygame import Surface
from pygame.mixer import Sound

from color import *
from config import *
from element import Power, Explosion, Rock, Player

# 定義全域變數
# 定義圖片變數
background_img: Surface
player_img: Surface
player_mini_img: Surface
bullet_img: Surface
bullet_img: Surface
rock_imgs: list[Surface]
expl_anim: dict[str, list]
power_imgs: dict[str, Surface]
# 定義聲音變數
shoot_sound: Sound
gun_sound: Sound
shield_sound: Sound
die_sound: Sound
expl_sounds: Sound
# 定義字體變數
font_name = str


def load_image():
    global background_img, player_img, player_mini_img, bullet_img, rock_imgs, expl_anim, power_imgs
    background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
    player_img_raw = pygame.image.load(os.path.join("img", "player.png")).convert()
    player_img = pygame.transform.scale(player_img_raw, (50, 38))
    player_img.set_colorkey(BLACK)  # 把黑色編框變成透明
    player_mini_img = pygame.transform.scale(player_img, (25, 19))
    player_mini_img.set_colorkey(BLACK)
    pygame.display.set_icon(player_mini_img)
    bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
    bullet_img.set_colorkey(BLACK)
    rock_imgs = []
    for j in range(7):
        rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{j}.png")).convert())
        rock_imgs[j].set_colorkey(BLACK)
    expl_anim = {
        'lg': [],
        'sm': [],
        'player': []
    }
    for j in range(9):
        expl_img = pygame.image.load(os.path.join("img", f"expl{j}.png")).convert()
        expl_img.set_colorkey(BLACK)
        expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
        expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
        player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{j}.png")).convert()
        player_expl_img.set_colorkey(BLACK)
        expl_anim['player'].append(player_expl_img)
    power_imgs = {
        'shield': pygame.image.load(os.path.join("img", "shield.png")).convert(),
        'gun': pygame.image.load(os.path.join("img", "gun.png")).convert()
    }


def load_music():
    global shoot_sound, gun_sound, shield_sound, die_sound, expl_sounds
    shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
    gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
    shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
    die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
    expl_sounds = [
        pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
        pygame.mixer.Sound(os.path.join("sound", "expl1.wav")),
    ]

    pygame.mixer.music.load(os.path.join("sound", "background.ogg")),
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)


def load_font():
    global font_name
    font_name = os.path.join("font.ttf")


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def new_rock():
    r = Rock(random.choice(rock_imgs))
    all_sprites.add(r)
    rocks.add(r)


def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, lives, img, x, y):
    for k in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * k
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, '太空生存戰！', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '← → 移動飛船 空白鍵發射子彈～ ', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, '按任意鍵開始遊戲', 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


def start_loop_running():
    while running:
        if show_init:
            close = draw_init()
            if close:
                break
            show_init = False
            all_sprites = pygame.sprite.Group()
            rocks = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            powers = pygame.sprite.Group()
            player = Player(player_img, bullet_img, shoot_sound, all_sprites, bullets)
            all_sprites.add(player)
            for i in range(8):
                new_rock()
            score = 0

        clock.tick(FPS)
        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        # 更新遊戲
        all_sprites.update()
        # 判斷石頭 子彈相撞
        hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
        for hit in hits:
            random.choice(expl_sounds).play()
            score += hit.radius
            expl = Explosion(hit.rect.center, expl_anim['lg'])
            all_sprites.add(expl)
            if random.random() > 0.9:
                type = random.choice(['shield', 'gun'])
                image = power_imgs[type]
                image.set_colorkey(BLACK)
                pow = Power(hit.rect.center, type, image)
                all_sprites.add(pow)
                powers.add(pow)
            new_rock()

        # 判斷石頭  飛船相撞
        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_rock()
            player.health -= hit.radius
            expl = Explosion(hit.rect.center, expl_anim['sm'])
            all_sprites.add(expl)
            if player.health <= 0:
                death_expl = Explosion(player.rect.center, expl_anim['player'])
                all_sprites.add(death_expl)
                die_sound.play()
                player.lives -= 1
                player.health = 100
                player.hide()

        # 判斷寶物 飛船相撞
        hits = pygame.sprite.spritecollide(player, powers, True)
        for hit in hits:
            if hit.type == 'shield':
                player.health += 20
                if player.health > 100:
                    player.health = 100
                shield_sound.play()
            elif hit.type == 'gun':
                player.gun_up()
                gun_sound.play()

        if player.lives == 0 and not death_expl.alive():
            show_init = True

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_health(screen, player.health, 5, 15)
        draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
        pygame.display.update()


# pygame initialize
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("第一個遊戲")
clock = pygame.time.Clock()
# load resources
load_image()
load_music()
load_font()
# object initialize
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()
player = Player(player_img, bullet_img, shoot_sound, all_sprites, bullets)
all_sprites.add(player)
for i in range(8):
    new_rock()
score = 0
# 遊戲迴圈
show_init = True
running = True
# 開始遊戲迴圈
start_loop_running()
pygame.quit()

