import pygame as pg
import sys, time
import pg_ergo as pergo

# retrieve the colour container
colours = pergo.Colours() 


class Grid():
    def __init__(self, dim_x, dim_y):
        # create the container for the grid
        self.dim_x = dim_x
        self.dim_y = dim_y
        
        # init with just black
        self.arr = [[colours.BLACK for x in range(dim_x)] for y in range(dim_y)]


    def index(self, x, y):
        '''returns the grid element at pos: (x, y)'''
        return self.arr[y][x]
    
