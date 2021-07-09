# ASSETS FROM:
# https://evil-poisonbr.itch.io/ -- obstacle
# https://wallpapersafari.com/w/qiCQUB -- background
# https://tavino.itch.io/spaceship -- spaceship
# Sound from Zapsplat.com -- game theme
# https://gooseninja.itch.io/space-music-pack -- menu theme
# https://www.dafont.com/retro-gaming.font -- font

import pygame
import os
import random
from pygame.constants import USEREVENT

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(3)

side_power_timer = 0
speed = 2

#my events
BLOCKS = pygame.USEREVENT+1
HIT = pygame.USEREVENT+2
SCORE = pygame.USEREVENT+3
POWERUP = pygame.USEREVENT+4
TIMER = pygame.USEREVENT+5
CATCH_POWER = pygame.USEREVENT+6


pygame.time.set_timer(BLOCKS, random.randint(1500, 3000))

pygame.time.set_timer(TIMER, 1000)

#icon
icon = pygame.image.load(os.path.join('Assets', 'hero.png'))

clock = pygame.time.Clock()


FPS = 60
WIDTH, HEIGHT = 300, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE RUNNER")
pygame.display.set_icon(icon)


#font
DEF_FONT = pygame.font.Font(os.path.join('Assets', 'RetroGaming.ttf'), 25)
OVER_FONT = pygame.font.Font(os.path.join('Assets', 'RetroGaming.ttf'), 45)


#background image
background_image = pygame.image.load(os.path.join('Assets', 'back.png'))

#hero image

player_image_default = pygame.image.load(os.path.join('Assets', 'hero.png'))
player_image_left = pygame.image.load(os.path.join('Assets', 'heroL.png'))
player_image_right = pygame.image.load(os.path.join('Assets', 'heroR.png'))

#rules
rules_image = pygame.image.load(os.path.join('Assets', 'rules.png'))
credits_image = pygame.image.load(os.path.join('Assets', 'credits.png'))
about_image = pygame.image.load(os.path.join('Assets', 'about.png'))

#obstacle
obstacle = pygame.image.load(os.path.join('Assets', 'obstacle.png'))

objects = []
lines = []
powerups = []

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BACK = (13, 13, 72)

#power-ups
POWER = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'powerUp.png')), (30, 30))



#sounds
MENU_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'music/menu.wav'))
MOUSE_OVER = pygame.mixer.Sound(os.path.join('Assets', 'music/mouseOver.wav'))
MOUSE_CLICK = pygame.mixer.Sound(os.path.join('Assets', 'music/mouseClick.wav'))
GAME_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'music/game.wav'))
HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'music/crash.wav'))
GAME_OVER = pygame.mixer.Sound(os.path.join('Assets', 'music/gameOver.wav'))
SIDE_POWER_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'music/power.wav'))

pygame.mixer.Sound.set_volume(HIT_SOUND, 0.5)

class Background:
    def __init__(self, background, width, height):
        self.width = width
        self.height = height
        self.background = pygame.transform.scale(background, (width, height))
        self.y = 0
        self.y2 = HEIGHT

    def update(self):
        self.y2 += speed
        self.y += speed
        WIN.blit(self.background,(0, self.y))
        WIN.blit(self.background,(0, self.y2))
        if self.y > HEIGHT:
            self.y = HEIGHT * -1
        if self.y2 > HEIGHT:
            self.y2 = HEIGHT * -1

class Player:
    TURBO = 6
    GRAVITY = 4
    def __init__(self, name, width, height, image, left, right, speed):
        self.name = name
        self.width = width
        self.height = height
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.image_default = pygame.transform.scale(image, (self.width, self.height))
        self.imageL = pygame.transform.scale(left, (self.width, self.height))
        self.imageR = pygame.transform.scale(right, (self.width, self.height))
        self.speed = speed

    def spawn_player(self, INITIAL_X, INITIAL_Y):
        self.rect = pygame.Rect(INITIAL_X, INITIAL_Y, self.width, self.height)
        WIN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.display.update()

    def handle(self, keys_pressed):
        
        if keys_pressed[pygame.K_a] and self.rect.x - self.speed > 0: # LEFT (A is pressed)
            self.image = self.imageL
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d] and self.rect.x + self.speed + self.rect.width < WIDTH: # RIGHT
            self.image = self.imageR
            self.rect.x += self.speed
        if keys_pressed[pygame.K_SPACE] and self.rect.y - Player.TURBO > 0: # UP
            self.rect.y -= Player.TURBO
        elif not keys_pressed[pygame.K_SPACE] and self.rect.y + self.rect.height + Player.GRAVITY < HEIGHT:
            self.rect.y += Player.GRAVITY
        if not any(keys_pressed):
            self.image = self.image_default

    def update(self):
        WIN.blit(self.image, (self.rect.x, self.rect.y))

class Lines:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Obstacle:
    def __init__(self, x, y, width, height, image):
        if x + width > WIDTH:
            x -= x + width - WIDTH
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = (x, y, width, height) 
        self.img = pygame.transform.scale(image, (self.width, self.height))

    def draw(self):
        self.hitbox = (self.x + 5, self.y + 5, self.width - 10, self.height)
        WIN.blit(self.img, (self.x, self.y))
        self.imgRect = self.img.get_rect(topleft=(self.x, self.y))


class POWER_UPS:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self):
        self.hitbox = (self.x + 5, self.y + 5, self.width - 10, self.height)
        WIN.blit(self.image, (self.x, self.y))
        self.imgRect = self.image.get_rect(topleft=(self.x, self.y))      

    def side(player):
        if side_power_timer:
            player.speed = 10
        else:
            player.speed = 2

def ObstacleUpdate():
    for q in objects:
        q.y += speed
        if q.y > HEIGHT:
            objects.pop(objects.index(q))
    for x in objects:
        x.draw()
    for q in lines:
        q.y += speed
        if q.y > HEIGHT:
            lines.pop(lines.index(q))
    for a in powerups:
        a.y += 3
        if a.y > HEIGHT:
            powerups.pop(powerups.index(a))
    for a in powerups:
        a.draw()
        

def LineUpdate():
    for x in lines:
        x.line = pygame.draw.rect(WIN, BACK, (0, x.y, WIDTH, 1), 1)


#create a Background object
background = Background(background_image, WIDTH, HEIGHT)

#create a Player object
hero = Player("Main", 48, 72, player_image_default, player_image_left, player_image_right, 3)


def collide():
    for z in objects:
        if z.imgRect.colliderect(hero.rect):
            pygame.event.post(pygame.event.Event(HIT))
    for a in powerups:
        if a.imgRect.colliderect(hero.rect):
            powerups.pop(powerups.index(a))
            pygame.mixer.Channel(2).play(SIDE_POWER_SOUND)
            pygame.event.post(pygame.event.Event(CATCH_POWER))


            
def score(point):
    myScore = DEF_FONT.render("Points: " + str(point), 1, RED)
    WIN.blit(myScore, (10, 10))
    for z in lines:
        if z.line.colliderect(hero.rect):
            pygame.event.post(pygame.event.Event(SCORE))
            lines.pop(lines.index(z))

def show_time(sec):
    myTime = DEF_FONT.render("time: " + str(sec), 1, RED)
    WIN.blit(myTime, (150, 10))

def show_speed():
    spd = DEF_FONT.render("speed: " + str(speed), 1, RED)
    WIN.blit(spd, (10, 40))

def coord(px, py, lx, ly):
    print((px, py), (lx, ly))



def game_over(point):
    pygame.mixer.Channel(2).play(GAME_OVER)
    Game_Over = OVER_FONT.render("GAME OVER", 1, RED)
    WIN.blit(Game_Over, ((300-Game_Over.get_width())//2, (500-Game_Over.get_height())//2))
    pygame.display.update()
    f= open("scores.txt","a")
    f.write('\n' + str(point))
    f.close()

def clear():
    global objects
    global lines
    global powerups
    global speed
    objects = []
    lines = []
    powerups = []
    speed = 2
    hero.spawn_player(150, 420)

def Menu():
        
    click = False
    running = True
    played = False


    PLAY = DEF_FONT.render("PLAY", 1, BLACK)
    RULES = DEF_FONT.render("RULES", 1, BLACK)
    CREDITS = DEF_FONT.render("CREDITS", 1, BLACK)
    ABOUT = DEF_FONT.render("ABOUT", 1, BLACK)
    QUIT = DEF_FONT.render("QUIT", 1, BLACK)

    while running:

        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(MENU_SOUND)

        WIN.fill(BLACK)

        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 170, 200, 50)
        button_3 = pygame.Rect(50, 240, 200, 50)
        button_4 = pygame.Rect(50, 310, 200, 50)
        button_5 = pygame.Rect(50, 380, 200, 50)

        if button_1.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            PLAY = DEF_FONT.render("PLAY", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                Game()
        elif button_2.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            RULES = DEF_FONT.render("RULES", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                rules.display()
        elif button_3.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            CREDITS = DEF_FONT.render("CREDITS", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                creditss.display()
        elif button_4.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            ABOUT = DEF_FONT.render("ABOUT", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                about.display()
        elif button_5.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            QUIT = DEF_FONT.render("QUIT", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                running = False
                pygame.quit()
                quit()
        else:
            played = False
            PLAY = DEF_FONT.render("PLAY", 1, BLACK)
            RULES = DEF_FONT.render("RULES", 1, BLACK)
            CREDITS = DEF_FONT.render("CREDITS", 1, BLACK)
            ABOUT = DEF_FONT.render("ABOUT", 1, BLACK)
            QUIT = DEF_FONT.render("QUIT", 1, BLACK)
        
        pygame.draw.rect(WIN, RED, button_1, 0, 15)
        pygame.draw.rect(WIN, RED, button_2, 0, 15)
        pygame.draw.rect(WIN, RED, button_3, 0, 15)
        pygame.draw.rect(WIN, RED, button_4, 0, 15)
        pygame.draw.rect(WIN, RED, button_5, 0, 15)

        
        WIN.blit(PLAY, (50+(200-PLAY.get_width())//2, 100+(50-PLAY.get_height())//2))
        WIN.blit(RULES, (50+(200-RULES.get_width())//2, 170+(50-RULES.get_height())//2))
        WIN.blit(CREDITS, (50+(200-CREDITS.get_width())//2, 240+(50-CREDITS.get_height())//2))
        WIN.blit(ABOUT, (50+(200-ABOUT.get_width())//2, 310+(50-ABOUT.get_height())//2))
        WIN.blit(QUIT, (50+(200-QUIT.get_width())//2, 380+(50-QUIT.get_height())//2))


        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            
                    

        pygame.display.update()
        clock.tick(FPS)

def Retry():
    pygame.mixer.Channel(1).stop()
    

    click = False
    running = True
    played = False

    RETRY = DEF_FONT.render("RETRY", 1, BLACK)
    RULES = DEF_FONT.render("RULES", 1, BLACK)
    QUIT = DEF_FONT.render("QUIT", 1, BLACK)

    while running:

        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(MENU_SOUND)

        WIN.fill(BLACK)

        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 200, 200, 50)
        button_3 = pygame.Rect(50, 300, 200, 50)

        if button_1.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            RETRY = DEF_FONT.render("RETRY", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                Game()
        elif button_2.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            RULES = DEF_FONT.render("RULES", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                rules.display()
        elif button_3.collidepoint((mx, my)):
            if not played:
                played = True
                pygame.mixer.Channel(2).play(MOUSE_OVER)
            QUIT = DEF_FONT.render("QUIT", 1, GREEN)
            if click:
                pygame.mixer.Channel(2).play(MOUSE_CLICK)
                running = False
                pygame.quit()
                quit()
        else:
            played = False
            RETRY = DEF_FONT.render("RETRY", 1, BLACK)
            RULES = DEF_FONT.render("RULES", 1, BLACK)
            QUIT = DEF_FONT.render("QUIT", 1, BLACK)
                

        pygame.draw.rect(WIN, RED, button_1, 0, 15)
        pygame.draw.rect(WIN, RED, button_2, 0, 15)
        pygame.draw.rect(WIN, RED, button_3, 0, 15)

        WIN.blit(RETRY, (50+(200-RETRY.get_width())//2, 100+(50-RETRY.get_height())//2))
        WIN.blit(RULES, (50+(200-RULES.get_width())//2, 200+(50-RULES.get_height())//2))
        WIN.blit(QUIT, (50+(200-QUIT.get_width())//2, 300+(50-QUIT.get_height())//2))

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            
                    

        pygame.display.update()
        clock.tick(FPS)

class menuButton:
    def __init__ (self, image):
        self.image = image

    def display(self):
        click = False
        running = True
        played = False
        MENU = DEF_FONT.render("MENU", 1, BLACK)
        while running:

            if not pygame.mixer.Channel(1).get_busy():
                pygame.mixer.Channel(1).play(MENU_SOUND)

            WIN.fill(BLACK)

            mx, my = pygame.mouse.get_pos()
            button_1 = pygame.Rect(50, 50, 200, 50)

            if button_1.collidepoint((mx, my)):
                if not played:
                    played = True
                    pygame.mixer.Channel(2).play(MOUSE_OVER)
                MENU = DEF_FONT.render("MENU", 1, GREEN)
                if click:
                    pygame.mixer.Channel(2).play(MOUSE_CLICK)
                    Menu()
            else:
                played = False
                MENU = DEF_FONT.render("MENU", 1, BLACK)

            pygame.draw.rect(WIN, RED, button_1, 0, 15)
            WIN.blit(self.image, (50, 150))

            WIN.blit(MENU, (50+(200-MENU.get_width())//2, 50+(50-MENU.get_height())//2))

            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                        quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
            
            pygame.display.update()
            clock.tick(FPS)

creditss = menuButton(credits_image)
about = menuButton(about_image)
rules = menuButton(rules_image)

def Game():
    pygame.mixer.Channel(1).stop()

    hero.spawn_player(150, 420)
    clear()
    global side_power_timer
    global speed
    power_time = 0
    #block_time = 0
    run = True
    point = 0
    sec = 0
    while run:

        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(GAME_SOUND)

        if power_time <= 0:
            power_time = random.randint(10000, 20000)
            pygame.time.set_timer(POWERUP, power_time)
        #if block_time <= 0:
        #    block_time = random.randint(1500, 3000)
        #    pygame.time.set_timer(BLOCKS, block_time)
        #create a Obstacle object
        obs_width = random.randint(100, 200)
        obs_height = random.randint(40, 50)
        obs_x = random.choice([0, random.randint(0, 300)])

        px = random.randint(0, 300)

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == BLOCKS:
                objects.append(Obstacle(obs_x, -16, obs_width, obs_height, obstacle))
                lines.append(Lines(obs_x, -16))
            if event.type == HIT:
                pygame.mixer.Channel(1).play(HIT_SOUND)
                game_over(point)
                pygame.time.delay(2000)
                Retry()
            if event.type == SCORE:
                point += 1
            if event.type == POWERUP:
                powerups.append(POWER_UPS(px, -16, POWER))
            if event.type == TIMER:
                sec += 1
                power_time -= 1000
                #block_time -= 1000
                if side_power_timer:
                    side_power_timer -= 1
            if event.type == CATCH_POWER:
                side_power_timer = 3
                POWER_UPS.side(hero)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    quit()
        if side_power_timer == 0:
            hero.speed = 2
        keys_pressed = pygame.key.get_pressed()
        hero.handle(keys_pressed)
        LineUpdate()
        background.update()
        hero.update()
        ObstacleUpdate()
        collide()
        score(point)
        #show_time(sec)
        #show_speed()
        #print((power_time, block_time))
        speed = 2 + 0.5*point
        pygame.display.update()
    
Menu()