'''
2d simulation of charge interactions

'''

import pygame as pg
import sys, time, random, math
import pg_ergo as perg

# -----   setting up ergonomics. see pg_ergo for deets
# extract colour list
colours = perg.Colours()

# import fonts
fonts = perg.Fonts()


class Simulation():
    '''container for the simulation surface and related functionalities'''
    def __init__(self, dim, timestep, fps = 60):
        ''' Creates a simulation surface with dimensions dim (tuple)'''
        # sim control
        self.running = False # init with a freeze
        
        # display
        self.surf = pg.Surface(dim)
        self.rect = self.surf.fill(colours.WHITE)
        self.fps = fps
        self.default_fps = fps # store defaults


        # simulation elements
        self.particles = pg.sprite.Group()
        self.time_step = timestep
    
    def new_particle(self, mass, x, y, v_x, v_y, charge):
        # all particles have the same timestep, synced with the simulation value
        self.particles.add(Particle(mass, x, y, v_x, v_y, charge, self.time_step)) 

    def clear(self):
        ''' refills surface with white (refreshes frame) '''
        self.rect = self.surf.fill(colours.WHITE)

    def reset(self):
        '''resets simulation state'''
        self.running = False # pause game
        self.particles.empty() # empty all particles
        self.fps = self.default_fps

    def particle_event_handle(self, event):
        '''allows dragging around of particles for ease of repositioning'''
        if self.running == False: # only allow dragging in pause state
            for particle in self.particles:
                particle.handle_event(event)

    def draw(self, surface):
        '''draw the simulation upon the destination surface'''
        speed_text = perg.Text(f"Current fps: {self.fps}", (0, 0), 
                                        fonts.font_small, colours.BLACK, align = 'topleft') # fps counter
        speed_text.draw(self.surf) # draw fps counter
        
        # sim status text
        if self.running:
            state_text = perg.Text("Running", (200, 0), 
                                fonts.font_small, colours.BLACK, align = 'topleft')
        else:
            state_text = perg.Text("Paused", (200, 0),
                                fonts.font_small, colours.BLACK, align = 'topleft')

        # timstep display
        ts_text = perg.Text(f'Timestep: {self.time_step}', (300, 0), 
                                            fonts.font_small, colours.BLACK, align = 'topleft')
        ts_text.draw(self.surf)
        state_text.draw(self.surf)

        # update main sim surface
        surface.blit(self.surf, (100, 100)) # constant offset


class Controller():
    '''container for the options panel and related functionalities'''
    def __init__(self, dim):
        self.surf = pg.Surface(dim)
        self.rect = self.surf.fill(colours.GREY)
        self.buttons = {}
        self.text_input = {}
        self.info = {}
        self.checkboxes = {}
        self.rect.topleft = (1000, 100) # position controller wrt display window
        

    def clear(self):
        '''resets controller surface state'''
        self.surf.fill(colours.GREY)

    def reset(self):
        '''resets all controller options'''
        self.load() # overrides current input states
        

    def load_buttons(self):
        '''creates the menu for text input + buttons, and shows text info'''
        
        # fast forward/slow down buttons ------
        ff_text = perg.Text(">>", (25,25), fonts.font_small, colours.BLACK)
        ff_button = perg.Button((200, 500, 50, 50), colours.WHITE, ff_text)                                   
        self.buttons['ff'] = ff_button

        sd_text = perg.Text("<<", (25,25), fonts.font_small, colours.BLACK)
        sd_button = perg.Button((100, 500, 50, 50), colours.WHITE, sd_text)
        self.buttons['sd'] = sd_button
        
        # add particle (randomised) button -----------
        add_text = perg.Text('Random', (12,10), fonts.font_small, 
                colours.BLACK, align = 'topleft')
        add_button = perg.Button((30, 200, 120, 50), colours.YELLOW, add_text,
                         text_align='topleft')
        self.buttons['random'] = add_button

        # add particle (text input) button ----------
        add_spec_text = perg.Text('Add Particle', (17, 10), fonts.font_small, 
                    colours.BLACK, align = 'topleft')
        add_spec_button = perg.Button((220, 200, 150, 50), colours.YELLOW, add_spec_text, 
                        text_align = 'topleft')
        self.buttons['add'] = add_spec_button

        # pause button -----------------
        pause_text = perg.Text('Pause', (17, 10), fonts.font_small, colours.BLACK,
                     align = 'topleft')
        pause_button = perg.Button((40, 400, 150, 50), colours.RED, pause_text,
                     text_align='topleft')
        self.buttons['pause'] = pause_button

        # play button -----------------
        play_text = perg.Text('Play', (17, 10), fonts.font_small, colours.BLACK,
                     align = 'topleft')
        play_button = perg.Button((240, 400, 150, 50), colours.GREEN, play_text,
                     text_align='topleft')
        self.buttons['play'] = play_button

        # reset button -----------------
        reset_text = perg.Text('Reset', (17, 10), fonts.font_small, colours.BLACK, 
                    align = 'topleft')
        reset_button = perg.Button((50, 600, 100, 50), colours.WHITE, reset_text)
        self.buttons['reset'] = reset_button


        # get the abs positions for all the buttons saved
        for button in self.buttons.values():
            button.rect_abs = pg.Rect(button.rect.x + self.rect.x, 
                                        button.rect.y + self.rect.y,
                                        button.rect.w,
                                        button.rect.h)



    def load_text_inp(self):
        '''generates the text input surfaces'''
        # initial position fields
        in_pos_x = perg.InputBox(50, 50, 50, 50, text = 'x')
        in_pos_y = perg.InputBox(120, 50, 50, 50, text = 'y')


        # initial velocity 
        in_vel_x = perg.InputBox(190, 50, 50, 50, text = 'vx')
        in_vel_y = perg.InputBox(260, 50, 50, 50, text = 'vy')


        # other properties
        in_mass = perg.InputBox(50, 105, 50, 50, text = 'm')
        in_charge = perg.InputBox(120, 105, 50, 50, text = 'Q')

        # add to dict
        self.text_input.update(x = in_pos_x, y = in_pos_y, vx = in_vel_x, vy = in_vel_y,
                                m = in_mass, q = in_charge)
        
        # define the appropriate absolute positions
        for box in self.text_input.values():
            box.rect_abs = pg.Rect(box.rect.x + self.rect.x, 
                                    box.rect.y + self.rect.y, 
                                    box.rect.w, 
                                    box.rect.h)

    def load_checkbox(self):
        #wall_text = perg.Text('Wall', (20, 0), fonts.font_small, colours.BLACK)
        wall_radio = perg.CheckBox((50, 20), 100, 750, colours.WHITE, 10)
        
        self.checkboxes.update(wall = wall_radio)

        # define the abs position
        for radio in self.checkboxes.values():
            radio.rect_abs = pg.Rect(radio.x + self.rect.x,
                                    radio.y + self.rect.y, 
                                    radio.rect.w, 
                                    radio.rect.h)
    def draw(self, surface):
        for b in self.buttons.values():
            b.draw(self.surf) #draw buttons onto controller surface
        #for box in self.text_input.values():
        #    box.draw(self.surf) # draw input boxes
        surface.blit(self.surf, self.rect.topleft) 


class Particle(pg.sprite.Sprite): # make this into a pg.sprite child class
    '''container for a charged point particle'''
    # constants
    k = 8.99e9 # coulomb 
    # scaling of force
    rescaler = 0.0001

    def __init__(self, mass, x, y, v_x, v_y, charge, dt):
        ''' mass (float)
            pos = [x, y] the positions of the particle 
                in SIMULATION SURFACE COORDS
            vel = [v_x, v_y] is the velocity of the particle 
            charge = signed float
            '''
        super().__init__() # init the pg.sprite parent class
        
        # physics
        self.inv_mass = 1/mass # store only the inverse mass for convenience
        self.dt = dt

        self.x = x
        self.y = y
        
        self.v_x = v_x
        self.v_y = v_y
        
        self.q = charge

        self.coeff = self.k * self.q * self.inv_mass # calculate the acceleration coefficient

        
        # display
        self.surf = pg.Surface((20,20), pg.SRCALPHA) # 20x20 px surface
        self.surf.set_colorkey((255, 255, 255))
        self.surf.fill(colours.WHITE)

        if self.q < 0: # -ve chaarge
            self.rect = pg.draw.circle(self.surf, colours.BLUE, (10, 10), 10)
        elif self.q > 0: # +ve charge
            self.rect =  pg.draw.circle(self.surf, colours.RED, (10, 10), 10)
        elif self.q == 0: # neutral charge
            self.rect =  pg.draw.circle(self.surf, colours.GREY, (10, 10), 10)

        self.sim_offset = (100, 100) # the displacement of sim surface from display window
        # interaction managers
        self.dragging = False
        self.rect_abs = pg.Rect(self.x + self.sim_offset[0], self.y + self.sim_offset[1], 
                            self.rect.w, self.rect.h) # offsets from display window

    def accel_calc(self, p_list):
        '''calculates the net force experienced by a particle p 
        caused by all other particles in p_list 
        
        updates the net acceleration = [a_x, a_y]'''
        
        self.a_x = 0 
        self.a_y = 0  # reset acceleration between frames

        for test in p_list:
            if test == self:
                continue # ignore itself
            # calculate the separation vector
            r_x = self.x - test.x
            r_y = self.y - test.y

            
            # separate out the magnitude and uvec calc
            force_coeff = self.coeff *  test.q * (1 / (math.sqrt(r_x **2 + r_y**2) **3))
            
            # calculate force comps
            self.a_x += force_coeff * r_x
            self.a_y += force_coeff * r_y

            #print(f'{i}, {r_x, r_y}, {force_coeff}, {a_x, a_y}')
        self.a_x = self.rescaler * self.a_x
        self.a_y = self.rescaler * self.a_y
    
    def handle_event(self, event):
        '''handles dragging of specific particle while in pause state'''
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect_abs.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                # save offsets from the actual hitbox and display window
                self.offset_x = self.rect_abs.x - mouse_x - self.sim_offset[0]
                self.offset_y = self.rect_abs.y - mouse_y - self.sim_offset[1]
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pg.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                
                # updates display positions
                self.x = mouse_x + self.offset_x 
                self.y = mouse_y + self.offset_y

                # updates actual hitbox position
                self.rect_abs = pg.Rect(self.x + self.sim_offset[0], self.y + self.sim_offset[1], 
                            self.rect.w, self.rect.h)

    def update(self):
        '''calculates new velocity from accelerations, 
        and then updates the position of the point charge
        dv contain [a_x, a_y]
        '''
        # update velocity from net acceleration
        self.v_x += self.a_x * self.dt
        self.v_y += self.a_y * self.dt

        # update position
        self.x += self.v_x * self.dt
        self.y += self.v_y * self.dt
        
        # print(self.v_x, self.v_y)

    def draw(self, surface):
        surface.blit(self.surf, (self.x, self.y))


# ---- basic setups
pg.init() # init pygame module

# main screen properties
s_width = 1500
s_height = 1000

displaysurface = pg.display.set_mode((s_width, s_height)) # init main display
displaysurface.fill(colours.BLACK) 

# ---- screen settings 
Clock = pg.time.Clock()

# ---- init simulation screen
time_step = 1
# last arg is modifier in the force coeff
simulation = Simulation((800, 800), time_step, fps = 60) 


# ---- init settings screen
controller = Controller((400, 800))
controller.load_buttons() # create buttons and text
controller.load_text_inp() # create text input fields
controller.load_checkbox() # create checkboxes
controller.draw(displaysurface) # only need to update this once for now
valid = True
# ---- particles
# test particle
#test1 = Particle(1, 300, 400, -0.5, -0.05, 0.01, time_step)
#test2 = Particle(1, 500, 400, 0, 0, 0.01, time_step) # two particles of like charge
#test3 = Particle(1, 400, 300, 0, 0, -0.01, time_step) # third of opposite
#test4 = Particle(1, 400, 500, 0, 0, 0.01, time_step)
#test5 = Particle(1, 320, 550, 0, 0, -0.01, time_step)
#simulation.particles.add(test1, test2, test3, test4, test5)

# ---- main loop
while True:

    # clean simulation surface
    simulation.clear()

    # clean controller surface
    controller.clear()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # selectors
        elif event.type == pg.MOUSEBUTTONDOWN:
            # extract event position
            mouse_pos = event.pos
            # speed controllers
            if controller.buttons['ff'].rect_abs.collidepoint(event.pos):
                simulation.fps += 10
            elif controller.buttons['sd'].rect_abs.collidepoint(event.pos):
                simulation.fps -= 10

            elif controller.buttons['random'].rect_abs.collidepoint(mouse_pos): 
                simulation.new_particle(1, random.randint(100, 700), 
                    random.randint(100, 700),
                     random.choice([-1,1]) * random.random() * 3, 
                     random.choice([-1,1]) * random.random() * 3, 
                     random.choice([-1,1]) * random.random() * 0.01) # randomise charge as well
                #print('a')
            
            elif controller.buttons['add'].rect_abs.collidepoint(mouse_pos):
                print('+')
                # read in properties from text input
                inp = {}
                for k, v in controller.text_input.items():
                    try:
                        inp[k] = float(v.text) # convert the text into numbers
                    except: 
                        valid = False
                        print('Invalid input')
                
                if valid:
                    simulation.new_particle(inp['m'], inp['x'], inp['y'],
                     inp['vx'], inp['vy'], inp['q'])
                
            elif controller.buttons['pause'].rect_abs.collidepoint(mouse_pos):
                simulation.running = False 
                print('p')
            elif controller.buttons['play'].rect_abs.collidepoint(mouse_pos):
                simulation.running = True
                print('>')
            
            elif controller.buttons['reset'].rect_abs.collidepoint(mouse_pos):
                simulation.reset()
                controller.reset()
                print('reset')

        # give event to the simulation particle handler
        simulation.particle_event_handle(event)

        # now give event to input boxes
        for box in controller.text_input.values():
            box.handle_event(event)

        # give event to checkboxes
        for radio in controller.checkboxes.values():
            radio.handle_event(event)

    #--------------------
    # update control surfaces (e.g. text input fields) 
    # text input
    for box in controller.text_input.values():
        box.resize()
        box.draw(controller.surf)

    for radio in controller.checkboxes.values():
        radio.draw(controller.surf)
    
    # blit control surface
    controller.draw(displaysurface)
    # -----------------------

    if simulation.running: # checks for game state
        # update particles -- force calculation must happen separate from render updater
        for p in simulation.particles:
            p.accel_calc(simulation.particles) # acceleration gets stored in itself 
        for p in simulation.particles:
            p.update() 
    # draw them
    for p in simulation.particles:    
        p.draw(simulation.surf)

    # redraw the simulation surface onto the display
    simulation.draw(displaysurface)
    
    pg.display.update()
    Clock.tick(simulation.fps)
