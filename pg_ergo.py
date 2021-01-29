# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 20:25:41 2021

@author: joshu

collection of classes/functions that make pygame making easier
 - Text 
 - Button
 - Text input box
"""
import pygame as pg

class Colours():
    def __init__(self):
        self.CYAN = (0, 255,255)
        self.BLUE = (0, 0, 255)
        self.ORANGE = (255, 128, 0)
        self.YELLOW = (255, 255, 0)
        self.DARKGREEN = (0, 128, 0)
        self.GREEN = (0,255,0)
        self.LIGHTGREEN = (128, 255, 128)
        self.PURPLE = (255,0,  255)
        self.DARKRED = (128, 0, 0)
        self.RED = (255, 0, 0)
        self.LIGHTRED = (255, 128, 128)
        self.BLACK = (0,0,0)
        self.WHITE = (255, 255, 255)
        self.GREY = (128, 128, 128)
        self.LIGHTGREY = (170, 170, 170)
    
    def __iter__(self):
        '''returns dict mapping str version of colours with the tuples'''
        for attr, value in self.__dict__.iteritems():
            yield attr, value

class Text():
    def __init__(self, text, pos, style, colour, align = 'center'):
        '''generates a text object. 
        text: str
        pos: (int, int) # relative to surface and alignmnet
            e.g. if centered, pos specifies the center of the text
        style: pg font style
        colour: colour tuple
        align: Text alignment on the surface, takes the virtual attributes of 
        the pg.Rect object as argument
        '''
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
        elif self.align == 'midleft':
            self.rect.midleft = self.pos
        elif self.align == 'bottomleft':
            self.rect.bottomleft = self.pos 
        surface.blit(self.surf, (self.rect.x, self.rect.y))
        

class Button():
    def __init__(self, rect, dark_shade, text, text_align = 'center', light_shade = (255, 255, 255)):
        '''
        (x,y,w,h): rect tuple
        light_shade, dark_shade: colour tuples
        text: pg_ergo.Text surface
        '''
        self.dim = (rect[2], rect[3]) # dimensions of button
        self.surf = pg.Surface(self.dim) 
        self.rect = pg.Rect(rect) # retrieves position information of BUTTON
        self.rect_abs = (0,0,0,0) # absolute position holder wrt topleft of DISPLAY WINDOW
        self.hovered = False
        self.light = light_shade
        self.dark = dark_shade
        self.text = text # Text object inherited
        self.text_align = text_align # change alignment
        # align the button rect as required
        self.rect.topleft = (rect[0], rect[1])
        
    def draw(self, surface):
        '''renders the button rects onto surface at position pos (tuple)'''
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

class Fonts():
    def __init__(self):
        ''' a collection of fonts'''
        #---------------fonts
        # init pygame font collection
        pg.font.init()
        self.font_large = pg.font.SysFont("Verdana",115)
        self.font = pg.font.SysFont("Verdana", 60)
        self.font_small = pg.font.SysFont("Verdana", 20) # different sized fonts
        self.font_button = pg.font.SysFont("Verdana", 35)

class InputBox():
    COLOUR_INACTIVE = (200, 200, 200)
    COLOUR_ACTIVE = (255, 255, 255)
    fonts = Fonts()
    def __init__(self, x, y, w, h, text=''):
        ''' box for user input'''
        self.rect = pg.Rect(x, y, w, h)
        self.colour = self.COLOUR_INACTIVE
        self.default_text = text
        self.text = text
        self.txt_surface = self.fonts.font_small.render(text, True, self.colour)
        self.active = False
        self.rect_abs = pg.Rect((0, 0, 0, 0))
        self.default_state = True

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect_abs.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                # clear input box if in default state
                if self.default_state:
                    self.text = '' 
                    # Re-render the text.   
                    self.txt_surface = self.fonts.font_small.render(self.text, True, self.colour)

            else:
                self.active = False
                
            # Change the current color of the input box.
            self.colour = self.COLOUR_ACTIVE if self.active else self.COLOUR_INACTIVE
        
        if event.type == pg.KEYDOWN:
            if self.active:
                # once you start typing then toggle default state so if you click off box is not cleared
                self.default_state = False
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = '' # clear box
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.fonts.font_small.render(self.text, True, self.colour)

    def resize(self):
        # Resize the box if the text is too long.
        width = max(self.rect.w, self.txt_surface.get_width()+10)
        self.rect.w = width 

    def draw(self, surface):
        # Blit the text.
        surface.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(surface, self.colour, self.rect, 2) # do borders only

class CheckBox():
    def __init__(self, dim, x, y, colour, rad, colour_toggle = (0, 0, 0)):
        '''x, y is topleft position Relative to draw surface
        text is perg.Text object'''
        self.surf = pg.Surface(dim)
        self.rect = self.surf.get_rect()
        self.rad = rad
        self.colour = colour
        self.colour_toggle = colour_toggle
        self.rect_abs = pg.Rect(0,0,0,0) #storer for pos in case draw surf is not display surf
        self.checked = False    
        
        # positions on surface
        self.x = x
        self.y = y 

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect_abs.collidepoint(event.pos):
                self.checked = not self.checked # toggle check
    
    def draw(self, surface):
        # draw base layer
        pg.draw.circle(self.surf, self.colour, self.rect.center, self.rad, 0)
        if self.checked:
            pg.draw.circle(self.surf, self.colour_toggle, self.rect.center, self.rad - 4, 0)
        
        # blit
        surface.blit(self.surf, (self.x, self.y))

        
    