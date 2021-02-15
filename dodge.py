# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 22:47:06 2021

@author: joshu

full game, with classes
"""

import pygame as pg
import sys, random, time 
from pygame.locals import *


# colour constants, we don't need the extra functionality with pg.Color()_
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

#Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
ENEMY_SPEED = 5
SCORE = 0
PLAYER_LIVES = 3
PLAYER_INVULN = False
INVULN_TIME = 999999
ENEMY_COLOUR_INDEX = 0 
ENEMY_COLOUR_LIST = [RED, GREEN, BLACK, GREY] # enemy colour can't be same as background

# create classes to handle display objects
class Enemy(pg.sprite.Sprite): # child class of pg.sprite.Sprite
    def __init__(self):
        super().__init__() 
        # self.image = pg.image.load('download.png') # not using an image for now
        self.surf = pg.Surface((50,100)) # surface 
        self.surf.fill(RED)
        #pg.draw.rect(self.surf, RED, (0,0,50,100))
        self.image = self.surf #make it just red
        # retrieve rect object from surface and randomise its position
        self.rect = self.image.get_rect(center = (random.randint(40,SCREEN_WIDTH - 40),0)) 
        
                
    def move(self):
        global SCORE
        self.rect.move_ip(0, ENEMY_SPEED) #moves object by pixels, (x, y) per update
        if (self.rect.top > 600): # checks if rect has left edge of screen
            SCORE += 100     # add to score
            self.rect.top = 0 # wraps
            self.rect.center = (random.randint(40,SCREEN_WIDTH - 40), 0) # resets postition randomly
        
    def draw(self, surface): 
        # if using image, pass self.image to blit instead
        surface.blit(self.image, self.rect)  # note that blit takes surface as input
        # we have convoluted blit here--since we dont have image, can just use suraface

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pg.Surface((50,100))
        self.surf.fill(BLUE)
        self.image = self.surf # just use a filled shape
        self.rect = self.surf.get_rect(center = (150, 500))
        
    def move(self):
        # retrieves user input via boolean sequence
        pressed_keys = pg.key.get_pressed()
        
        # use rect as a hitbox for wrapping and keystroke movement
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]: # retrieve boolean
                self.rect.move_ip(-5,0) # move left
        if self.rect.right < SCREEN_WIDTH: #
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5,0)
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0,-5)
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0,5)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# initialise
pg.init()

# create object instances using classes
P1 = Player()
E1 = Enemy()


# create sprite groups. note we don't need player group
enemies = pg.sprite.Group() 
enemies.add(E1)

all_sprites = pg.sprite.Group()
all_sprites.add(P1, E1)


# user events
INC_SPEED = pg.USEREVENT + 1 # give custom event unique id
pg.time.set_timer(INC_SPEED, 2000) # every 1000 ms calls event

# spawn enemy
SPAWN_ENEMY = pg.USEREVENT + 2
pg.time.set_timer(SPAWN_ENEMY, 3000)

# assign fps
FPS = 60
FramePerSec = pg.time.Clock()

# fonts
font = pg.font.SysFont("Verdana", 60)
font_small = pg.font.SysFont("Verdana", 20) # different sized fonts
game_over = font.render("Game Over", True, BLACK) # actually generates text surface, blit onto another surface ot show
live_lost = font.render("-1 Lives", True, BLACK)
# setup display 
displaysurface = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)) # 300 x 300 px
displaysurface.fill(WHITE) # background 
pg.display.set_caption("Game")


# refresh loop
while True:
    # invuln timer
    if pg.time.get_ticks() - INVULN_TIME > 3000:
        PLAYER_INVULN = False
    
    # event handler
    for event in pg.event.get():
        if event.type == SPAWN_ENEMY:
            EN = Enemy()
            enemies.add(EN)
            all_sprites.add(EN)
            SCORE += 200 # get 200 points every time a new enemy spawns
        if event.type == INC_SPEED:
            ENEMY_SPEED += 1
            ENEMY_COLOUR_INDEX = (ENEMY_COLOUR_INDEX + 1) % len(ENEMY_COLOUR_LIST) 
            for sprite in enemies:
                sprite.surf.fill(ENEMY_COLOUR_LIST[ENEMY_COLOUR_INDEX])
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit() # terminate script
    
    
    displaysurface.fill(WHITE) # blank out screen
    scores = font_small.render(str(SCORE), True, BLACK) # render the scores constantly, as it changes
    lives = font_small.render("LIVES: "+str(PLAYER_LIVES), True, BLACK)
    displaysurface.blit(scores, (10,10))
    displaysurface.blit(lives, (SCREEN_WIDTH-130,10))
    # move and redraw all sprites
    for entity in all_sprites:
        displaysurface.blit(entity.image, entity.rect) #blit each 
        entity.move() # update pos
    
    # collision checker
    if pg.sprite.spritecollideany(P1, enemies) and PLAYER_INVULN == False:
        #pg.mixer.Sound('crash.wav').play() # use mixer library WE DONT HAVE SOUND
        displaysurface.blit(live_lost, (30, 250))
        PLAYER_LIVES -= 1
        PLAYER_INVULN = True
        INVULN_TIME = pg.time.get_ticks()
        pg.display.update()
        time.sleep(0.5) # delay a little
        # temporary invulnerability
        if PLAYER_LIVES == 0:
            displaysurface.fill(GREY) #make screen grey
            displaysurface.blit(game_over, (30,250)) # blit game over text
            pg.display.update()
            for entity in all_sprites:
                entity.kill() # remove all sprites
            # exit sequence
            time.sleep(2) # wait
            pg.quit()
            sys.exit()
    pg.display.update() # refresh
    # limit fps
    FramePerSec.tick(FPS)

