import pygame as pg
import sys, time
import pg_ergo as pergo


class Grid():
    '''grid object for storing maze structure'''
    def __init__(self, dim_x, dim_y):
        # create the container for the grid
        self.dim_x = dim_x
        self.dim_y = dim_y
        
        # init with just black
        self.arr = [[colours.BLACK for x in range(dim_x)] for y in range(dim_y)]


    def index(self, x, y):
        '''returns the grid element at pos: (x, y)'''
        return self.arr[y][x]
    
    def field(self):
        pass



def main():
    # vars
    s_width = 1000
    s_height = 800
    running = True
    fps = 60
    ticker = pg.time.Clock()
    # pergo init
    colours = pergo.Colours() 

    # setups
    pg.init()
    displaysurface = pg.display.set_mode((s_width, s_height))
    displaysurface.fill(colours.WHITE)
    pg.display.set_caption("Maze")



    # main refresh loop
    while running:

        # event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()



        # update 
        pg.display.update()
        # frame rate limiter
        ticker.tick(fps)



if __name__ == "__main__":
    main()
