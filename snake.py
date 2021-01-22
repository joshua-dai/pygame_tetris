# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 18:31:44 2021

@author: joshu
"""

import pygame as pg
import sys, time, random


s_width = 800
s_height = 800

play_rect = (100, 100, 600, 600)
p_width = play_rect[2]
p_height = play_rect[3]


# 20 x 20 grid, 30px each
block_size = 30

fps = 60
framerate = pg.time.Clock()

# colours

CYAN = (0, 255,255)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
DARKGREEN = (0, 128, 0)
GREEN = (0,255,0)
LIGHTGREEN = (128, 255, 128)
PURPLE = (255,0,  255)
DARKRED = (128, 0, 0)
RED = (255, 0, 0)
LIGHTRED = (255, 128, 128)
BLACK = (0,0,0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
LIGHTGREY = (170, 170, 170)

class Snake():
    def __init__(self, x, y, length, colour, ini_heading_x, ini_heading_y):
        '''pos in grid coords. NOTE THAT only the head moves'''
        self.heading_x = ini_heading_x
        self.heading_y = ini_heading_y
        self.col = x
        self.row = y
        self.colour = colour
        self.length = length
        self.body = [(x,y)] # add in the current snake position
        
    def move_hor(self, dx):
        self.col += dx
        if self.collision():
            gameover()
            return 0
        self.body.append((self.col, self.row))
        if not eats():
            self.body.pop(0) # pop the oldest entry
        grid.locked = self.body
        
    def move_ver(self, dy):
        self.row += dy
        if self.collision():
            gameover()
            return 0
        self.body.append((self.col, self.row))
        if not eats():
            self.body.pop(0) # pop the oldest entry
        # update the grid
        grid.locked = self.body
        # def parse_to_grid(self, grid):
        #     grid.locked = self.body

    def collision(self):
        '''checks if snake collides with wall or itself'''
        if (not (0 <= self.col <= 19)) or (not(0 <= self.row <= 19)) : # first check walls
            return True
        else:
            for tup in self.body:
                if self.col == tup[0] and self.row == tup[1]: # matching row/col coords
                    return True
        return False
    
class Fruit():
    def __init__(self, colour):
        ava_cols = [i for i in range(20)]
        ava_cols.pop(snake.col)
        ava_rows = [i for i in range(20)]
        ava_rows.pop(snake.row)
        
        
        self.col = random.randint(0, 19)
        self.row = random.randint(0, 19)
        self.colour = colour
    def parse_to_grid(self, grid):
        grid.obj = [(self.col, self.row), self.colour]
        
class Grid():
    def __init__(self, locked_pos):
        self.cols = 20
        self.rows = 20
        self.field = [[BLACK for x in range(self.cols)] for y in range(self.rows)]
        self.locked = locked_pos
        self.obj = [0, 0]
        
    def draw_borders(self, surface):
        '''creates outer borders for the play area. SHOULD ALWAYS
        BE CALLED AFTER THE GRID HAS BEEN FILLED'''
        # outside border
        pg.draw.rect(surface, GREY, play_rect, 5) # thickness 5
        
        # inner borders
        for i in range(self.rows): 
            for j in range(self.cols): # cols
                pg.draw.rect(surface, GREY, (play_rect[0] + j * block_size, play_rect[1] + i * block_size,
                                              block_size, block_size), 2) # thickness 2
        
    
    def update_field(self):
        '''uses the locked array to update the entire colour field'''
        for i in range(self.rows):
            for j in range(self.cols):
                if (j , i) in self.locked:
                    self.field[i][j] = snake.colour
                elif (j, i) in self.obj:
                    self.field[i][j] = self.obj[1] # fruit colour
                else:
                    self.field[i][j] = BLACK
        
    def draw_grid(self, surface):
        ''' fills in the screen with the corresponding colours from the field'''
        
        for i in range(self.rows):
            for j in range(self.cols):
                grid_rect = pg.Rect(play_rect[0] + j * block_size, 
                                                   play_rect[1] + i * block_size,
                                          block_size, block_size)                
                pg.draw.rect(surface, self.field[i][j], grid_rect , 0)
        self.draw_borders(surface) # draw outer border on as well
        

class Scoring():
    '''object for storing scores, lines, and level conditions'''
    def __init__(self, dim):
        '''takes in the dimension ote scoring area'''
        self.surf = pg.Surface(dim)
        self.rect = self.surf.get_rect()
        self.score = 0
        self.highscore = 0
        self.speed = 1
        
    def update(self, surface):
        '''updates and blits scoring information, using rect surface underneath 
        to clear old info'''
        # update area
        self.surf.fill(WHITE)
        
        # fonts 
        self.text_score = font_small.render("Score: " + str(self.score), True, BLACK)
        # self.text_high = font_small.render("High Score: " + str(self.highscore), True, BLACK)
        self.text_speed = font_small.render("SPEED: " + str(self.speed), True, BLACK)
        
        # show scores
        self.surf.blit(self.text_score, (0, 0))
        #self.surf.blit(self.text_high, (0, 30))
        self.surf.blit(self.text_speed, (100, 0 ))
        
        # blit
        surface.blit(self.surf, (50, 50))
        
    def draw(self, surface, pos):
        '''simply draws the scores onto a surface at topleft = pos'''
        # self.surf.fill(GREY) # fill background of scores surface with the surface underneath
        
        # blit scores
        surface.blit(self.surf, pos)

class Text():
    def __init__(self, text, pos, style, colour, align = 'center'):
        '''generates a text object. 
        text: str
        pos: (int, int) # relative to surface and alignmnet
            e.g. if centered, pos specifies the center of the text
        style: pg font style
        colour: colour tuple'''
        self.surf = style.render(text, True, colour)
        self.rect = self.surf.get_rect()
        self.pos = pos
        # self.rect.topleft = pos #align rect to desired pos
        self.align = align
        
    def draw(self, surface):
        '''draws text onto surface'''
        if self.align == 'center':
            self.rect.center = self.pos
        elif self.align == 'topleft':
            self.rect.topleft = self.pos
        surface.blit(self.surf, (self.rect.x, self.rect.y))


class Button():
    def __init__(self, rect, light_shade, dark_shade, text, text_align = 'center', *func):
        '''
        (x,y,w,h): rect tuple
        light_shade, dark_shade: colour tuples
        text: Text surface
        
        Inherits position from text position
        '''
        self.dim = (rect[2], rect[3]) # dimensions of button
        self.surf = pg.Surface(self.dim) 
        self.rect = pg.Rect(rect) # retrieves position information
        self.hovered = False
        self.light = light_shade
        self.dark = dark_shade
        self.text = text # Text object inherited
        self.text_align = text_align # change alignment
        #self.render() # immediately render button rects
    def draw(self, surface):
        '''renders the button rects onto surface'''
        if self.hovered:  # hovered
            self.surf.fill(self.light)        
            #pg.draw.rect(self.surf, self.light, self.rect) # draw rect onto itself
        else: # is not hovered
            self.surf.fill(self.dark)
            #pg.draw.rect(self.surf, self.dark, self.rect)
        
        if self.text_align == 'center':
            self.text.rect.center = ((self.dim[0]/2), (self.dim[1]/2)) # put in middle of button surf
        # display button fill and text
        self.text.draw(self.surf)# first blit text onto button surface, always at same
        # pos as the button
        surface.blit(self.surf, (self.rect.x, self.rect.y))
def eats():
    '''checks if the snake eats the fruit'''
    global fruit
    if snake.col == fruit.col:
        if snake.row == fruit.row:
            scores.score += 1
            scores.speed = scores.score //5 + 1
            fruit = Fruit(RED)
            
            return True
        
    return False
    
def gameover():
    '''function for initialising gameover conditions'''
    over = True
    # make background all grey
    displaysurface.fill(GREY)
    
    # render the text
    text_gameover = Text('Game Over', (s_width/2, s_height/2), font, BLACK, align = 'center')
    text_gameover.draw(displaysurface)
    
    #display final scores
    scores.draw(displaysurface, (s_width/2 + 100 , s_height/2 + 100))
    
    # retry button 
    retry_text = Text('Retry', (170/2, 50/2), font_button, WHITE, align = 'center') 
    retry_button = Button((160, s_height/2 + 100, 170, 50), LIGHTGREEN, DARKGREEN, retry_text, 'center')
    retry_button.draw(displaysurface)
    
    # render the center score text
    # enter another loop
    while over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if retry_button.rect.collidepoint(mouse_pos):
                    over = False
                    reset()
        
        # manage the hovering over of button
        mouse = pg.mouse.get_pos()
        if retry_button.rect.collidepoint(mouse):
            retry_button.hovered = True
            retry_button.draw(displaysurface)
        else:
            retry_button.hovered = False
            retry_button.draw(displaysurface)
        pg.display.update()
        framerate.tick(15)

def reset():
    ''' renews game state to initial'''
    global snake
    
    # reset scores
    scores.score = 0
    scores.speed = 1
    # reshow instructions
    # show_instructions(displaysurface)
    
    # reset grid states. Removes all previously frozen pieces
    grid.__init__({})
    
    # reset moving piece
    snake = Snake(9, 9, 0, WHITE, 0, -1)
    
    # reset display
    displaysurface.fill(WHITE)
    time.sleep(0.5) # delay
    
    
    
# --------------game setup
# initialisation
pg.init()

locked_pos = []
grid = Grid(locked_pos)
# initial heading is upwards
snake = Snake(9, 9, 0, WHITE, 0, -1)
fruit = Fruit(RED)
scores = Scoring((200, 50))


#---------------fonts
font_large = pg.font.SysFont("Verdana",115)
font = pg.font.SysFont("Verdana", 60)
font_small = pg.font.SysFont("Verdana", 20) # different sized fonts
font_button = pg.font.SysFont("Verdana", 35)

# ---------------create the scren 
displaysurface = pg.display.set_mode((s_width,s_height)) # 300 x 300 px
displaysurface.fill(WHITE) # background 
pg.display.set_caption("Snake")
pg.display.update()


#---------------------
move_timer = 500
last_move = 0 # pause bfore start game with a move
# userevents
# MOVE_SNAKE = pg.USEREVENT + 1
# pg.time.set_timer(MOVE_SNAKE, 500)


#-----------------control loop
while True:
    
    for event in pg.event.get(): 
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            # manual
            if event.type == pg.KEYDOWN: # limit input rate
            
                # -----------------linear
                if event.key == pg.K_LEFT:
                    snake.heading_y = 0
                    snake.heading_x = -1
                if event.key == pg.K_RIGHT:
                    snake.heading_y = 0
                    snake.heading_x = 1
                if event.key == pg.K_DOWN:
                    snake.heading_y = 1
                    snake.heading_x = 0
                if event.key == pg.K_UP:
                    snake.heading_y = -1
                    snake.heading_x = 0         
            
                # # ----------------special
        # if event.key == pg.K_SPACE:
        #     current_piece.move_space() # piece hits bottom no matter what
        #     current_piece = new_piece()
        # if event.key == pg.K_p:
        #     paused()
        
        # # ---------------cheats/diagnostics
        # if event.key == pg.K_q:
        #     scores.score += 5000
    
    # automatic events
    if pg.time.get_ticks() - last_move > move_timer - 5 * scores.speed:
        last_move = pg.time.get_ticks()
        if snake.heading_x != 0:
            snake.move_hor(snake.heading_x)
        elif snake.heading_y != 0: 
            snake.move_ver(snake.heading_y)
            
    # -------------------render
    # update scores
    scores.update(displaysurface)
    # update the fruit position
    fruit.parse_to_grid(grid) # note that snake parsing is done in move function
    
    #update the grid
    grid.update_field()
    
    grid.draw_grid(displaysurface)
    #update display
    pg.display.update()

framerate.tick(fps)


