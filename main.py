import sys
import pygame
import time
from pygame.locals import *
from pygame.mixer import music
from random import randint, choice
from items import *


# Connect to database
from db import DB
DB = DB('main.db')
# Music
pygame.init()
pygame.mixer.init()
music.load("./res/music/background_music.mp3")
music.set_volume(0.3)
def reset_level():
    DB.set_level(1)

FISH_SETTINGS = {
    1: {
        "fish_list": (fish1, fish2, fish3),
        "speed_list": (speed_1, speed_2, speed_3),
        "count": 18,
        "health": (3, 4, 3)
    },
    2: {
        "fish_list": (fish2, fish3, fish4),
        "speed_list": (speed_2, speed_3, speed_4),
        "count": 18,
        "health": (4, 3, 2)
    },
    3: {
        "fish_list": (fish3, fish4, fish5),
        "speed_list": (speed_3, speed_4, speed_5),
        "count": 19,
        "health": (3, 2, 3)
    },
    4: {
        "fish_list": (fish1, fish2, fish3, fish4),
        "speed_list": (speed_1, speed_2, speed_3, speed_4),
        "count": 20,
        "health": (3, 4, 3, 2)
    },
    5: {
        "fish_list": (fish1, fish2, fish3, fish4, fish5),
        "speed_list": (speed_1, speed_2, speed_3, speed_4, speed_5),
        "count": 20,
        "health": (3, 4, 3, 2, 3)
    }
}
def spawn_fishes():
    current_level = DB.get_level()
    if current_level <= 5:
        fish_list = FISH_SETTINGS[current_level]["fish_list"]
        speed_list = FISH_SETTINGS[current_level]["speed_list"]
        health_list = FISH_SETTINGS[current_level]["health"]
        count = FISH_SETTINGS[current_level]["count"]
    else:
        # "Бесконечный" режим
        fish_list = FISH_SETTINGS[5]["fish_list"]
        speed_list = FISH_SETTINGS[5]["speed_list"]
        health_list = FISH_SETTINGS[5]["health"]
        count = FISH_SETTINGS[5]["count"] + 5

    for i in range(count):
        x, y = randint(-1800, -400), randint(0, 630)
        fish = choice(fish_list)
        speed = choice(speed_list)
        health = health_list[fish_list.index(fish)]
        f = Fish(x, y, fish, speed, health)
        fish_sprites.add(f)

class Kill:
    def __init__(self, screen):
        self.screen = screen
        self.killed_fish = 0
        self.required_kills = 30
        self.font = pygame.font.Font("./res/fonts/minecraft.ttf", 24)

    def update_killed_fish(self):
        self.killed_fish += 1
        if self.killed_fish < self.required_kills and float(ELAPSED_TIME) >= 35:
            # Игрок не успел убить 30 рыб за i секунд
            self.health = 0
            Fish.final_time = ELAPSED_TIME
            DB.set_display(3)

    def draw_info(self):
        # Отображение количества убитых рыб
        kills_text = self.font.render(f"Разбито камней: {self.killed_fish}", 1, (255, 255, 255))
        self.screen.blit(kills_text, (10, 10))

        # Отображение требований для победы
        required_kills_text = self.font.render(f"Необходимо разбить 30 камней за 35 секунд, иначе игра закончится", 1, (255, 255, 255))
        self.screen.blit(required_kills_text, (10, 40))
# Sprites
class Fish(pygame.sprite.Sprite):

    def __init__(self, x, y, item, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = item
        self.rect = self.image.get_rect(x=x, y=y)
        self.speed = speed

        self.x = x
        self.y = y
        self.max_health = health
        self.health = self.max_health  # Начальное здоровье рыбы

    def update(self, lasers, player, kill):
        # Move via self.speed speed
        if self.rect.left < 1200:
            self.rect.x += self.speed
        else:
            self.kill()  # Удаляем рыбу, если она вышла за пределы экрана

        # Check for collision with lasers
        for laser in lasers:
            if pygame.sprite.collide_mask(self, laser):
                self.health -= 1  # Урон лазера
                laser.kill()  # Удаляем лазер после попадания
                if self.health <= 0:
                    self.kill()  # Удаляем рыбу, если она умерла
                    kill.update_killed_fish()  # Вызываем метод для обновления количества убитых рыб


    def draw_health_bar(self, screen):
        # Рисуем полоску здоровья над рыбой
        health_bar_width = 50
        health_bar_height = 5
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - 10
        health_percentage = self.health / self.max_health  # Максимальное здоровье
        health_bar_width_scaled = int(health_bar_width * health_percentage)

        # Фон полоски здоровья
        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Полоска здоровья
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width_scaled, health_bar_height))

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, x=555, y=375):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('./res/img/item/player2.bmp').convert_alpha(), (90, 36.25))
        self.image = pygame.transform.rotate(self.image, 90)
        self.x = x
        self.y = y
        self.screen = screen
        self.rect = self.image.get_rect(x=self.x, y=self.y)
        self.lasers = pygame.sprite.Group()
        self.laser_cooldown = 20  # через какое время начинает стрелять
        self.laser_damage = 1  # Урон лазера
        self.health = 3  # Начальное здоровье игрока
        self.last_hit_time = 0  # Время последнего попадания
        self.hit_cooldown = 2  # Кулдаун урона в секундах


    def player_blit(self):
        # Blit the player
        self.rect = self.image.get_rect(x=self.x, y=self.y)
        self.screen.blit(self.image, self.rect)

        self.click_update()
        self.shoot_lasers()
        self.lasers.update()
        self.lasers.draw(self.screen)
        self.check_collision(fish_sprites)
        self.draw_health_bar()

    def draw_health_bar(self):
        # Рисуем полоску здоровья в правом верхнем углу
        health_bar_width = 100
        health_bar_height = 20
        health_bar_x = self.screen.get_width() - health_bar_width - 10
        health_bar_y = 10
        health_percentage = self.health / 3  # Максимальное здоровье - 3
        health_bar_width_scaled = int(health_bar_width * health_percentage)

        # Фон полоски здоровья
        pygame.draw.rect(self.screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Полоска здоровья
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (health_bar_x, health_bar_y, health_bar_width_scaled, health_bar_height))

    def check_collision(self, fish_sprites):
        player_hit = pygame.sprite.spritecollide(self, fish_sprites, False)
        if player_hit:
            current_time = time.time()
            if current_time - self.last_hit_time >= self.hit_cooldown:
                self.health -= 1
                self.last_hit_time = current_time
            if self.health <= 0:
                # Игрок умирает
                Fish.final_time = ELAPSED_TIME
                DB.set_display(3)

    def click_update(self, *args):
        # Keyboard control
        if pygame.key.get_pressed()[K_UP] or pygame.key.get_pressed()[K_w]:
            self.y -= 4
            if self.y < 0:
                self.y = 0
            Yy = self.y
        if pygame.key.get_pressed()[K_DOWN] or pygame.key.get_pressed()[K_s]:
            self.y += 4
            if self.y > 609.875:
                self.y = 609.875
            Yy = self.y
        if pygame.key.get_pressed()[K_LEFT] or pygame.key.get_pressed()[K_a]:
            self.x -= 4
            if self.x < 0:
                self.x = 0
            Xx = self.x
        if pygame.key.get_pressed()[K_RIGHT] or pygame.key.get_pressed()[K_d]:
            self.x += 4
            if self.x > 1100:
                self.x = 1100
            Xx = self.x

    def shoot_lasers(self):
        if self.laser_cooldown <= 0:
            laser = Laser(self.rect.left, self.rect.centery, 8, self.laser_damage)
            self.lasers.add(laser)
            self.laser_cooldown = 1.8
        else:
            self.laser_cooldown -= 0.1


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([30, 5])
        self.image.fill((255, 0, 0))  # Красный цвет лазера
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.damage = damage

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -10:
            self.kill()


# UI
class Button_Start:
    def __init__(self, screen, pos=((1200-250)/2, (750-217.241379)/2), scale=(250, 167.241379), image=''):
        # Init to Button class. Set self's vars
        self.screen = screen
        self.pos = pos
        self.scale = scale
        self.image = pygame.image.load(image)
        self.rect = None

    def blit(self):
        # Bliting button
        self.image_edited = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image_edited.get_rect(x=self.pos[0], y=self.pos[1])
        self.screen.blit(self.image_edited, self.rect)

        # Function `click` is active via `blit`
        self.click()

    def click(self):
        # Mouse click def
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and mouse[0]:
            Fish.final_time = -1
            timer_.start_time = None
            DB.set_display(2)


class Button:
    def __init__(self, screen, pos, scale, image, on_click):
        self.screen = screen
        self.pos = pos
        self.scale = scale
        self.image = pygame.image.load(image)
        self.rect = None
        self.on_click = on_click

    def blit(self):
        self.image_edited = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image_edited.get_rect(x=self.pos[0], y=self.pos[1])
        self.screen.blit(self.image_edited, self.rect)

        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                self.on_click()


class Button_Menu:
    def __init__(self, screen, pos=(378, 406.5), scale=(445, 150.687256), image=''):
        # Init to Button class. Set self's vars
        self.screen = screen
        self.pos = pos
        self.scale = scale
        self.image = pygame.image.load(image)
        self.rect = None


    def blit(self):
        # Bliting button
        self.image_edited = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image_edited.get_rect(x=self.pos[0], y=self.pos[1])
        self.screen.blit(self.image_edited, self.rect)

        # Function `click` is active via `blit`
        self.click()

    def click(self):
        # Mouse click def
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and mouse[0]:
            Fish.final_time = -1
            timer_.start_time = None
            DB.set_display(1)

class Top:
    def __init__(self, screen, pos=(750+162,110), image='', scale=(162, 162)):
        # Init to Top class. Set self's vars
        self.screen = screen
        self.pos = pos
        self.image = pygame.image.load(image)
        self.scale = scale

    def blit(self, top1=0.0, top2=0.0, top3=0.0):
        # Blitting Top3
        self.top1 = top1
        self.top2 = top2
        self.top3 = top3
        self.image_edited = pygame.transform.scale(self.image, self.scale)
        self.screen.blit(self.image_edited, self.pos)

        font = "./res/fonts/minecraft.ttf"
        self.font = pygame.font.Font(font, 24)
        self.text1 = self.font.render(f'{self.top1}', 1, (255, 255, 255))
        self.screen.blit(self.text1, (self.pos[0]+40, self.pos[1]+61))
        self.text2 = self.font.render(f'{self.top2}', 1, (255, 255, 255))
        self.screen.blit(self.text2, (self.pos[0]+40, self.pos[1]+61+36))
        self.text3 = self.font.render(f'{self.top3}', 1, (255, 255, 255))
        self.screen.blit(self.text3, (self.pos[0]+40, self.pos[1]+61+72))

class Timer:
    def __init__(self, screen, start_time, pos=(545, 725), elapsed_time=0):
        self.screen = screen
        self.pos = pos
        self.font11 = pygame.font.Font("./res/fonts/minecraft.ttf", 36)
        self.start_time = start_time
        self.elapsed_time = elapsed_time
        self.ELAPSED_TIME = '{:.1f}'.format(self.elapsed_time)

    def blit(self):
        if self.start_time is None:
            self.start_time = time.time()
        else:
            self.elapsed_time += time.time() - self.start_time
            global ELAPSED_TIME
            ELAPSED_TIME = '{:.1f}'.format(self.elapsed_time)
            self.ELAPSED_TIME = '{:.1f}'.format(self.elapsed_time)
            self.start_time = None
        dicti = {1: 10, 2: 20, 3: 30, 4: 60, 5: 120}
        if DB.get_level() <= 5:
            text1 = self.font11.render("{:.2f}\{}".format(self.elapsed_time, dicti[DB.get_level()]), True, (255, 255, 255))
        else:
            text1 = self.font11.render("{:.2f}".format(self.elapsed_time), True, (255, 255, 255))
        self.screen.blit(text1, (self.pos[0], self.pos[1]-text1.get_height()))

# Create START-Button and Top3 list
but_start, top_start, but_menu, f1 = Button_Start(screen, image=but_start_img), Top(screen, image=top_start_img), Button_Menu(screen, image=but_menu_img), Fish(0, 0, fish2, speed_4, 4)

# Set default display's value
DB.set_display(1)
fish_sprites = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            DB.close()
            pygame.quit()
            sys.exit()
    # Display
    screen.blit(background_image, (0, 0))
    # Music
    if not music.get_busy():
        music.play()
    if DB.get_display() == 1:
        # Home page | Blit button and player's top
        timer_ = Timer(screen=screen, start_time=None)
        wrm = Player(screen)
        kill = Kill(screen)  # Создаем экземпляр класса Kill
        # Sprites' list
        fish_sprites = pygame.sprite.Group()

        # Blit
        but_start.blit()
        top_start.blit(top1=DB.get_top(1), top2=DB.get_top(2), top3=DB.get_top(3))

        reset_level()
        spawn_fishes()




    elif DB.get_display() == 2:
        # Fishes start swim (game page)
        # Timer
        timer_.blit()
        elap_time = float(timer_.ELAPSED_TIME)
        player = Player(screen)
        kill.draw_info()  # Вызываем метод для отображения информации
        for f in fish_sprites:
            screen.blit(f.image, f.rect)
            f.update(wrm.lasers, player, kill)
            f.draw_health_bar(screen)
            if f.final_time != -1:
                fish_sprites.remove(f)
                DB.set_display(3)
            if f.rect.left >= 1200:
                fish_sprites.remove(f)
                ls = (fish1, fish2, fish3, fish4, fish5)
                sp_ls = (speed_1, speed_2, speed_3, speed_4, speed_5)
                for i in range(1):
                    x_coord, y_coord = randint(-1600, -400), randint(0, 500)
                    ELAPSED_TIME = float(ELAPSED_TIME)
                    rnd_index = 0
                    if 20 > ELAPSED_TIME >= 10:
                        rnd_index = randint(0, 1)
                    elif 30 > ELAPSED_TIME >= 20:
                        rnd_index = randint(0, 2)
                    elif 60 > ELAPSED_TIME >= 30:
                        rnd_index = randint(0, 3)
                    elif ELAPSED_TIME >= 60:
                        rnd_index = randint(0, 4)
                    health = FISH_SETTINGS[DB.get_level()]["health"][rnd_index]
                    f_sprt = Fish(x_coord, y_coord, ls[rnd_index], sp_ls[rnd_index], health)
                    fish_sprites.add(f_sprt)

        # Blit Worm as wrm

        wrm.player_blit()

        # Level detector
        dicti = {1: 10, 2: 20, 3: 30, 4: 60, 5: 120}
        elap_time = float(timer_.ELAPSED_TIME)
        kill.draw_info()  # Вызываем метод для отображения информации
        if 10 <= elap_time <= 10.4 and DB.get_level() == 1:
            DB.level_up()
            spawn_fishes()
        elif 20 <= elap_time <= 20.4 and DB.get_level() == 2:
            DB.level_up()
            spawn_fishes()
        elif 30 <= elap_time <= 30.4 and DB.get_level() == 3:
            DB.level_up()
            spawn_fishes()
        elif 60 <= elap_time <= 60.4 and DB.get_level() == 4:
            DB.level_up()
            spawn_fishes()
        elif 120 <= elap_time and DB.get_level() == 5:
            DB.level_up()
            if current_level > 5:
                # Переход в "Бесконечный" режим
                current_level = 6
            spawn_fishes()

        # Blit level num
        ffont = pygame.font.Font('./res/fonts/minecraft.ttf', 30)
        current_level = DB.get_level()
        if current_level <= 5:
            level_text = ffont.render(f'Уровень №{current_level}', 1, (255, 255, 255))
        else:
            level_text = ffont.render('Бесконечность', 1, (255, 255, 255))
        screen.blit(level_text, (200, (725 - level_text.get_height())))



    elif DB.get_display() == 3:
        # Lose page


        surff.fill((255, 0, 0))
        screen.blit(surff, (0, 0))
        ffont = pygame.font.Font('./res/fonts/minecraft.ttf', 36)
        final__time = float(ELAPSED_TIME)
        lose_text = ffont.render(f'Твой результат: {final__time}', 1, (255, 255, 255))
        screen.blit(lose_text, ((1200 - lose_text.get_width())/2, (750 - lose_text.get_height())/2))


        # Update Top-3 via DB
        if DB.get_top(1) < final__time:
            DB.set_top(2, DB.get_top(1))
            DB.set_top(1, final__time)
        elif DB.get_top(1) != final__time and DB.get_top(2) < final__time:
            DB.set_top(3, DB.get_top(2))
        elif DB.get_top(1) != final__time and DB.get_top(2) != final__time and DB.get_top(3) < final__time:
            DB.set_top(3, final__time)

        final__time = None
        # Main menu button
        but_menu.blit()
        button_menu_txt = ffont.render('На главную', 1, (255, 255, 255))
        screen.blit(button_menu_txt, (475, 466.5))

        reset_level()
        spawn_fishes()

        # Update
    clock.tick(FPS)
    pygame.display.update()