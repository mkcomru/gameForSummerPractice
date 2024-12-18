import pygame

# Initialisation pygame
pygame.init()

# Create window of the game
WIDTH = 1200
HEIGHT = 750
# Y default for runner
Y = 375
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Astral Assault')
display = 1
# pygame.display.set_icon(pygame.image.load('./res/img/item/fish5.bmp'))

FPS = 60
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks()



# Surface for lose and win page
surff = pygame.Surface((1200, 750))
surff.set_alpha(100)

# Items
but_start_img = './res/img/item/button_start.png'
top_start_img = './res/img/item/top_frame.bmp'
but_menu_img = './res/img/item/main_menu_button.png'

bg_img = './res/img/background/bg.bmp'
fish_1 = './res/img/item/1.bmp'
fish_2 = './res/img/item/2.bmp'
fish_3 = './res/img/item/3.bmp'
fish_4 = './res/img/item/4.bmp'
fish_5 = './res/img/item/5.bmp'
runner1_ = './res/img/item/player2.bmp'
seaweed_bg_img = './res/img/background/seaweed.png'

# Background
background_image = pygame.transform.scale(pygame.image.load(bg_img), (WIDTH, HEIGHT))

# Entity
speed_1 = 1.5
health_1 = 4
fish1 = pygame.transform.scale(pygame.image.load(fish_1).convert_alpha(), (150, 72.4137932))

speed_2 = 1.85
health_2 = 6
fish2 = pygame.transform.scale(pygame.image.load(fish_2).convert_alpha(), (275, 87.5))

speed_3 = 2
health_3 = 5
fish3 = pygame.transform.scale(pygame.image.load(fish_3).convert_alpha(), (100, 51.36897))

speed_4 = 3
health_4 = 3
fish4 = pygame.transform.scale(pygame.image.load(fish_4).convert_alpha(), (125, 50.6282972))

speed_5 = 1
health_5 = 7
fish5 = pygame.transform.scale(pygame.image.load(fish_5).convert_alpha(), (132, 120))

runner_ = pygame.transform.scale(pygame.image.load(runner1_).convert_alpha(), (90, 36.25))

# Seaweed
seaweed_background_image = pygame.image.load(seaweed_bg_img)
