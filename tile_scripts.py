import pygame
import pygame_setup as setup
import numpy
import lists
import math

class TILES():
    def __init__(self):
        self.tile_data_map = []
        self.minimap_scale = 1/4
        
    def preload_tiles(self, current_map):
        self.current_map=current_map
        self.tile_data_map = numpy.full((2, setup.map_height, setup.map_width), None)
        for z in range(current_map.shape[0]):
            for y in range(current_map.shape[1]):
                for x in range(current_map.shape[2]):
                    if str(current_map[z, y, x])=="000": img = None
                    else:   img = pygame.image.load("img/tiles_/tile"+str(current_map[z, y, x])+".png")
                    self.tile_data_map[z, y, x] = img
    
    def draw(self):
        for z in range(0,2):
            for y in range(math.floor((setup.camera_pos.y/32))-1, math.ceil(((setup.camera_pos.y+setup.screen.get_height())/32))):
                for x in range(math.floor((setup.camera_pos.x/32))-1, math.ceil(((setup.camera_pos.x+setup.screen.get_width())/32))):
                    img = self.tile_data_map[z,y,x]
                    if img != None: setup.screen.blit(img, ((x*32)-setup.camera_pos.x,(y*32)-setup.camera_pos.y))
        """
        for z in range(0,2):
            for y in range(self.tile_data_map.shape[1]):
                for x in range(self.tile_data_map.shape[2]):
                    img = self.tile_data_map[z,y,x]
                    if img != None: setup.screen.blit(img, ((x*32)-setup.camera_pos.x,(y*32)-setup.camera_pos.y))
        """
    
    def preload_minimap(self): 
        self.minimap_data = numpy.full((2, setup.map_height, setup.map_width), None)
        for z in range(0,2):
            for y in range(self.current_map.shape[1]):
                for x in range(self.current_map.shape[2]):
                    if str(self.current_map[z, y, x])=="000": img = None
                    else:   
                        img = pygame.image.load("img/tiles_/tile"+str(self.current_map[z, y, x])+".png")
                        img = pygame.transform.scale_by(img, self.minimap_scale)
                    self.minimap_data[z, y, x] = img

    def draw_minimap(self):
        surf = pygame.Surface((setup.screen.get_width(), setup.screen.get_height()), pygame.SRCALPHA, 32)
        surf.convert_alpha()
        size = 8
        x_offset = setup.screen.get_width()*0.25-1
        y_offset = setup.screen.get_height()*0.25-1
        for z in range(0,2):
            for y in range(self.minimap_data.shape[1]):
                for x in range(self.minimap_data.shape[2]):
                    img = self.minimap_data[z,y,x]
                    if img != None: surf.blit(img, (x_offset+x*(size),  y_offset+y*(size)))
        for name in lists.alive_entitys:
            x = (lists.name_dict[name]).vars.pos.x/32*(size)
            y = (lists.name_dict[name]).vars.pos.y/32*(size)
            if "fireball" in name:
                pygame.draw.circle(surf, (194,120,33), (x_offset+x, y_offset+y), size)
            elif "REDGUY" in name:
                pygame.draw.circle(surf, (173,60,60), (x_offset+x, y_offset+y), size/2)
            elif "PLAYER" in name:
                pygame.draw.circle(surf, (58,63,94), (x_offset+x, y_offset+y), size/2)
            elif "VIOGUY" in name:
                pygame.draw.circle(surf, (120,59,118), (x_offset+x, y_offset+y), size/2)
        scroll = pygame.image.load("img/icons_/GUI_scroll_small.png")
        scroll = pygame.transform.scale(scroll, (self.minimap_data.shape[2]*size*1.25, self.minimap_data.shape[1]*size*1.5))
        setup.screen.blit(scroll, ((x_offset-self.minimap_data.shape[2]*size)+575, (y_offset-self.minimap_data.shape[1]*size)+260))
        surf.set_alpha(255)
        setup.screen.blit(surf, (0,0))


    def load_map(self):
        map = numpy.loadtxt("cmap_data.txt", comments='#>', dtype=str)
        map = map[0:(setup.map_height*2)]
        
        map = map.reshape(2, setup.map_height, setup.map_width)
        return map
    
    def deload_map(self):
        map = lists.current_map
        with open("cmap_data.txt", "w") as data_file:
            for slice in map:
                numpy.savetxt(data_file, slice, fmt='%s')
                numpy.savetxt(data_file, ["#>break<#"], fmt='%s')

    def load_pathgird(self,current_map, layer):
        self.current_map=current_map
        self.path_tile_data = numpy.full((1, setup.map_height, setup.map_width), None)
        z = layer
        for y in range(current_map.shape[1]):
            for x in range(current_map.shape[2]):
                try:
                    tile = int((current_map[z, y, x]))
                except:
                    tile = (current_map[z, y, x])
                img = pygame.image.load("img/tiles_/path_tile"+str(tile)+".png")
                self.path_tile_data[0, y, x] = img

    def draw_pathgrid(self):
        for y in range(self.path_tile_data.shape[1]):
            for x in range(self.path_tile_data.shape[2]):
                img = self.path_tile_data[0,y,x]
                if img != None: setup.screen.blit(img, ((x*32)-setup.camera_pos.x, (y*32)-setup.camera_pos.y))