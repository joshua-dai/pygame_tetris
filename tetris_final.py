# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 15:20:59 2021

@author: joshu
let's make tetris!

10 x 20 grid spaces
7 shapes

"""

# --------------imports
import pygame as pg
import sys, time, random


# --------------game settings
# aesthetics
s_width = 800
s_height = 900
play_width = 300
play_height = 600
play_rect = (50, 150, play_width, play_height) # define the play area rect
block_size = 30 # 30x30px for each block

fps = 60
framerate = pg.time.Clock()

# starting settings
ini_move_timer = 1000
ini_level = 1
level_multiplier = 50 



# --------------game backend
# set up game constants
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

# make this into a colour list for the shapes
colours = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# tetromino 
I = [[2,6,10,14], [9,10,11,12]]
L = [[6, 10, 11, 12], [6, 7, 10, 14], [5, 6, 7, 11], [3, 7, 10, 11]]
J = [[7, 9, 10, 11], [2, 6, 10, 11], [6, 7, 8, 10], [6, 7, 11, 15]]
O = [[6, 7, 10, 11]]
S = [[6, 7, 9, 10], [6, 10, 11, 15]]
T = [[6, 9, 10, 11], [6, 10, 11, 14], [9, 10, 11, 14], [6, 9, 10, 14]]
Z = [[5, 6, 10, 11], [7, 10, 11, 14]]

shapes = [I, L, J, O, S, T, Z]

# ---------------making objects
class Piece():
    rows = 20
    cols = 10
    def __init__(self, col, row):
        self.col = col
        self.row = row # grid coords
        self.shape = random.choice(shapes) # randomly select a shape
        self.colour = colours[shapes.index(self.shape)]
        self.rotation = 0 # we init with default orientation
        
        
    def draw(self, surface):
        '''
        draws itself onto a surface. Note that all pieces
        are defined in a 4x4 grid
        '''
        c = 0
        for i in range(4):
            for j in range(4):
                c += 1
                if c in self.shape[self.rotation]:
                    sub_rect = pg.Rect(play_rect[0] + (self.col + j) * block_size,
                              play_rect[1] + (self.row + i) * block_size,
                              block_size, block_size)
                    
                    if sub_rect.colliderect(play_rect) == True: # only draw if shape square is in play area
                        pg.draw.rect(surface, self.colour, sub_rect, 0)
                    
        
    def move_hor(self, dx):
        self.col += dx
        if intersects(self):
            self.col -= dx
            
    def move_space(self):
        while not intersects(self):
            self.row += 1
        self.row -= 1
        freeze(self)
       
    def move_ver(self, dy):
        self.row += dy
        if intersects(self):
            self.row -= dy
            freeze(self)
            return 1
    
    def rotate(self, dr):
        self.rotation = (self.rotation + dr) % len(self.shape)
        if intersects(self):
            self.rotation = (self.rotation - dr) % len(self.shape)
        # wrap around the orientation if needed
    
class Grid():
    cols = 10
    rows = 20
    def __init__(self, locked_pos):
        '''create grid of colours (default black) with given number of columns 
        c (int) and rows r (int)
        Also initialise with a locked_pos (dict)
        '''
        self.field = [[BLACK for x in range(self.cols)] for y in range(self.rows)]
        self.locked = locked_pos
        
    def draw_borders(self, surface):
        '''creates inner and outer borders for the play area. SHOULD ALWAYS
        BE CALLED AFTER THE GRID HAS BEEN FILLED'''
        # outside border
        pg.draw.rect(surface, GREY, play_rect, 5) # thickness 5
        
        # inner borders
        for i in range(self.rows): 
            for j in range(self.cols): # cols
                pg.draw.rect(surface, GREY, (play_rect[0] + j * block_size, play_rect[1] + i * block_size,
                                              block_size, block_size), 2) # thin edges
        
    def update_locked(self, new_lock_pos, new_lock_colour):
        '''uses new_lock_pos (pos tuple in play grid) and new_lock_colour (colour tuple) to update 
        the locked_pos dict and then also the field
        '''
        self.locked[new_lock_pos] = new_lock_colour
    
    def update_field(self):
        '''uses the locked_pos dict to update the entire colour field'''
        for i in range(self.rows):
            for j in range(self.cols):
                if (j , i) in self.locked.keys():
                    self.field[i][j] = self.locked[(j,i)]
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

class Scoring():
    '''object for storing scores, lines, and level conditions'''
    def __init__(self, dim):
        '''takes in the dimension ote scoring area'''
        self.surf = pg.Surface(dim)
        self.rect = self.surf.get_rect()
        self.score = 0
        self.lines = 0
        self.count_tetris = 0 
        self.highscore = 0
        self.level = ini_level
        
    def update(self, surface):
        '''updates and blits scoring information, using rect surface underneath 
        to clear old info'''
        # update area
        self.surf.fill(WHITE)
        # pg.draw.rect(self.surf, WHITE, self.rect)
        
        #-----
        # update the level
        # NOTE: this should be in tetris function for optimisation
        if scores.level < 11: # max level at 500 ms per move tick    
            scores.level = scores.score // 10000  + 1 # update the level
        #------
        
        # fonts 
        self.text_score = font_small.render("Score: " + str(self.score), True, BLACK)
        self.text_lines = font_small.render("Total Lines: " + str(self.lines), True, BLACK)
        self.text_tetris = font_small.render("Total Tetris: " + str(self.count_tetris), True, BLACK)
        self.text_high = font_small.render("High Score: " + str(self.highscore), True, BLACK)
        self.text_level = font_small.render("LEVEL: " + str(self.level), True, BLACK)
        
        # show scores
        self.surf.blit(self.text_score, (0, 0))
        self.surf.blit(self.text_high, (0, 30))
        self.surf.blit(self.text_lines, (0, 60))
        self.surf.blit(self.text_tetris, (0, 90))
        self.surf.blit(self.text_level, (0,120))
        
        # blit
        surface.blit(self.surf, (450, 70))
        
    def draw(self, surface, pos):
        '''simply draws the scores onto a surface at topleft = pos'''
        # self.surf.fill(GREY) # fill background of scores surface with the surface underneath
        
        # # show scores
        # self.surf.blit(self.text_score, (0, 0))
        # self.surf.blit(self.text_high, (0, 30))
        # self.surf.blit(self.text_lines, (0, 60))
        # self.surf.blit(self.text_tetris, (0, 90))
        
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
        
        
            
def intersects(piece):
    '''checks for intersect between a given piece, any of the walls, and a locked 
    grid section'''
    intersection = False
    c = 0
    for i in range(4):
        for j in range(4):
            c += 1
            if c in piece.shape[piece.rotation]: # shape is in this grid loc
                if i + piece.row > 19 or \
                    j + piece.col < 0 or \
                        j + piece.col > 9 or \
                            (piece.col + j, piece.row + i) in grid.locked.keys():
                    intersection = True
    return intersection

def freeze(piece):
    ''' freeze the current piece in place '''
    
    c = 0
    for i in range(4):
        for j in range(4):
            c+=1
            if c in piece.shape[piece.rotation]:
                grid.update_locked((piece.col + j, piece.row + i), piece.colour)
    grid.update_field() # update field for tetris detection
    tetris() # check for tetris
    
    grid.update_field() # update field after updating locked
    
def tetris():
    '''checks if there is a complete row in the grid.field, and if so updates the 
    locked dictionary in grid'''
    c_lines = 0 
    complete_rows = [] # index of complete row
    
    for i in range(grid.rows-1, 0, -1):
        sq = 0 # 10 squares in a row
        temp_dict = {}        
        for j in range(grid.cols):
            if grid.field[i][j] == BLACK:
                sq += 1
        if sq == 0: # no black squares
            c_lines += 1 # completed line
            complete_rows.append(i) 
            
            # remove all complete rows 
            for j1 in range(grid.cols):
                grid.locked.pop((j1, i))
    
    # sort complete_rows so we always go from top to bottom
    complete_rows = sorted(complete_rows)
    if len(complete_rows) > 0: # there is a complete line
        # now update the locked pos dictionary so all rows are shifted down one
        temp_dict = {}
        for k, v in grid.locked.items():
            it = 0
            for comp_row in complete_rows:
                if k[1] < comp_row:
                    it += 1
            temp_dict[(k[0], k[1] + it)] = v # shift down rows as required
        grid.locked = temp_dict
    
        # handle scoring
    scores.lines += c_lines    
    if c_lines < 4: # only possible to complete 4 rows in one go
        scores.score += 100 * c_lines * scores.level # multiplier            
    else:
        scores.count_tetris += 1 
        scores.score += 1000 * c_lines * scores.level # tetris special multiplier
    
    if scores.score >= scores.highscore: # if we have a new highscore
        scores.highscore = scores.score
    
def new_piece():
    new = Piece(spawn_x, spawn_y) # make it in the required location
    # check if we lost, as only lose in tetris if spawn piece intersects
    if intersects(new):
       gameover()
    return new

def gameover():
    '''function for initialising gameover conditions'''
    over = True
    # make background all grey
    displaysurface.fill(GREY)
    
    # render the text
    text_gameover = Text('Game Over', (s_width/2, s_height/2), font, BLACK)
    text_gameover.draw(displaysurface)
    
    #display final scores
    scores.draw(displaysurface, (s_width/2 + 100 , s_height/2 + 100))
    
    # retry button 
    retry_text = Text('Retry', (170/2, 50/2), font_button, WHITE, align = 'center') 
    retry_button = Button((160, 600, 170, 50), LIGHTGREEN, DARKGREEN, retry_text, 'center')
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

        
def show_instructions(surface):
    '''shows/rerenders the instructions'''
    
    text_instructions1 = Text('Use (Up, C)/V for CW/ACW rotation.', 
                              (400, 700), font_small, BLACK, align = 'topleft')
    text_instructions2 = Text('Use P to pause.', 
                              (400, 750), font_small, BLACK, align = 'topleft')
    text_instructions3 = Text('Every 10000 points game gets harder.',
                              (400, 800), font_small, BLACK, align = 'topleft')
    text_instructions1.draw(surface)
    text_instructions2.draw(surface)
    text_instructions3.draw(surface)
    
def paused():
    '''pause game'''
    pause = True
    
    # make screen opaque
    blank_surf = pg.Surface((s_width, s_height))
    blank_surf.set_alpha(128)
    pg.draw.rect(blank_surf, WHITE, blank_surf.get_rect(), 10 ) # draw the rect on surf
    displaysurface.blit(blank_surf, (0,0)) # make transparent underlay
    
    # pause text
    text_surf = font_large.render("Paused", True, RED)
    text_rect = text_surf.get_rect()
    text_rect.center = ((s_width/2),(s_height/2))
    displaysurface.blit(text_surf, (text_rect.x, text_rect.y))
    
    # make the buttons
    unpause_text = Text('Continue', (170/2, 50/2), font_button, WHITE, align = 'center') # text pos is relative to button
    unpause_button = Button((130, 600, 170, 50), LIGHTGREEN, DARKGREEN, unpause_text)
    unpause_button.draw(displaysurface)
    
    restart_text = Text('Restart', (170/2, 50/2), font_button, WHITE, align = 'center')
    restart_button = Button((500, 600, 170, 50), LIGHTRED, DARKRED, restart_text)
    restart_button.draw(displaysurface)
    
    while pause:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            # check if the mouse has been clicked
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos # retrieve mouse position
                
                if unpause_button.rect.collidepoint(mouse_pos): 
                    pause = False # terminate pause screen
                    unpause() # return to normal game conditions
                
                if restart_button.rect.collidepoint(mouse_pos):
                    pause = False
                    reset()
                    
                    
            if event.type == pg.KEYDOWN: # alternative unpause
                if event.key == pg.K_p:
                    pause = False
                    unpause()
                    
        # retrieve the position of the mouse
        mouse = pg.mouse.get_pos()
        
        # if mouse is hovered over button then the button changes colour
        if unpause_button.rect.collidepoint(mouse):
            unpause_button.hovered = True
            unpause_button.draw(displaysurface)
        elif restart_button.rect.collidepoint(mouse):
            restart_button.hovered = True
            restart_button.draw(displaysurface)
        else:
            unpause_button.hovered = False
            restart_button.hovered = False
            restart_button.draw(displaysurface)
            unpause_button.draw(displaysurface)
            
        pg.display.update()
        framerate.tick(15) # slow down timer to save resources

def unpause():
    '''return to normal game loop. Currently does nothing'''
    
    # cover everything with white background
    # displaysurface.fill(WHITE)
    # redisplay instructions
    # show_instructions(displaysurface)
    pass 
def reset():
    ''' renews game state to initial'''
    global current_piece
    
    # cover everything with white background
    # displaysurface.fill(WHITE)
    # pg.draw.rect(displaysurface, WHITE, (0, 0, s_width, s_height))
    
    # reset scores
    scores.score = 0
    scores.lines = 0
    scores.count_tetris = 0 
    
    # reshow instructions
    # show_instructions(displaysurface)
    
    # reset grid states. Removes all previously frozen pieces
    grid.__init__({})
    
    # reset moving piece
    current_piece = new_piece()
    
    time.sleep(0.5) # delay
    
    

# --------------game setup
# initialisation
pg.init()
running = True
# game_state = 'normal'

# -------------- init scores
scores = Scoring((170, 160))
scores.level = 1 # start on easiest
#---------------fonts
font_large = pg.font.SysFont("Verdana",115)
font = pg.font.SysFont("Verdana", 60)
font_small = pg.font.SysFont("Verdana", 20) # different sized fonts
font_button = pg.font.SysFont("Verdana", 35)

# ---------------create the scren 
displaysurface = pg.display.set_mode((s_width,s_height)) # 300 x 300 px
displaysurface.fill(WHITE) # background 
pg.display.set_caption("Tetris")
pg.display.update()

# show instructions
show_instructions(displaysurface)

# -------------- grid setup

# initialise filled grid spaces dict
locked_pos = {}    

# initialise grid
grid = Grid(locked_pos)

# fill the blank grid
grid.draw_grid(displaysurface)

# draw grid borders on
grid.draw_borders(displaysurface)


# --------------- shape setup
spawn_x = 3
spawn_y = -2 # control new piece spawn location
current_piece = Piece(spawn_x, spawn_y)


#----------------- event setup

# # timer for changing level/increasing speed
# LEVEL_TIMER = pg.USEREVENT + 2
last_move = 0

while running:
    # automatic events
    if pg.time.get_ticks() - last_move > ini_move_timer - level_multiplier * scores.level:
        c = current_piece.move_ver(1)
        last_move = pg.time.get_ticks()
        if c == 1:
            current_piece = new_piece()
    
    for event in pg.event.get(): 
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        
        # # automatic events
        # if event.type == MOVE_CURRENT:
        #     c = current_piece.move_ver(1)
        #     if c == 1:
        #         #print(grid.locked)
        #         current_piece = new_piece()
        # player input
        if event.type == pg.KEYDOWN: # limit input rate
        
            # -----------------linear
            if event.key == pg.K_LEFT:
                current_piece.move_hor(-1)
            if event.key == pg.K_RIGHT:
                current_piece.move_hor(1)
            if event.key == pg.K_DOWN:
                c = current_piece.move_ver(1)
                if c == 1: # intersection
                    #print(grid.locked)
                    current_piece = new_piece()
            
            # -----------------rotation
            if event.key == pg.K_UP:
                current_piece.rotate(1)
            if event.key == pg.K_c:
                current_piece.rotate(-1)
            if event.key == pg.K_v:
                current_piece.rotate(1)
            
            # ----------------special
            if event.key == pg.K_SPACE:
                current_piece.move_space() # piece hits bottom no matter what
                current_piece = new_piece()
            if event.key == pg.K_p:
                paused()
            
            # ---------------cheats/diagnostics
            if event.key == pg.K_q:
                scores.score += 5000
    
    # -------------------render
    # completely clear display
    displaysurface.fill(WHITE)
    
    # reshow instructions
    show_instructions(displaysurface)
    
    # display scoring
    scores.update(displaysurface)
    
    # remove previous moving shape images
    grid.draw_grid(displaysurface)
    
    # refresh the field with new locked pos
    grid.draw_grid(displaysurface) 
    
    # draw in the current moving piece
    current_piece.draw(displaysurface)
    
    # draw borders over the top
    grid.draw_borders(displaysurface)
    
    #update display
    pg.display.update()

framerate.tick(fps)


