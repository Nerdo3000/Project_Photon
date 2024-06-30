import pygame
import pygame_setup as setup
import numpy
import lists
import math

class TILES():
    def __init__(self):
        self.tile_data_map = []
        
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