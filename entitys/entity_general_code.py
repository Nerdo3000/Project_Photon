import extra_math as mthd
import pygame
import pygame_setup as setup
import math
import random
import lists

class Entity_inputs:
    def __init__(self):
        self.joystick = mthd.Position(0,0)
        self.try_throw_fireball = False
        self.fireball_target = mthd.Position(0,0)
        self.try_sword = False
        self.throw_mod = 0
        self.try_dash = False
        self.ULTI = False

    def RESET(self):
        self.joystick = mthd.Position(0,0)
        self.try_throw_fireball = False
        self.try_sword = False
        self.throw_mod = 0
        self.try_dash = False
        self.ULTI = False

class visuals:
    def blit(image, posx=None, posy=None, scale=1, dir=0):
        if scale!=1: image = pygame.transform.rotozoom(image, dir, scale)
        setup.screen.blit(image, (posx-setup.camera_pos.x, posy-setup.camera_pos.y))
    
    def load_image(name, flipx=False, flipy=False, alpha=255):
        img = pygame.image.load(str(name) + ".png")
        img = pygame.transform.flip(img, flipx, flipy)
        img = img.convert_alpha(img)
        img.set_alpha(alpha)
        return img

class class_Collisions:
    def check_for_collisions(self, new_pos_X, new_pos_Y, hitbox_size):
        '''Checking for collisions.'''
        try: 
            if lists.current_map[1][int((new_pos_Y+hitbox_size)//32)][int((new_pos_X+hitbox_size)//32)] != "000":    return True
        except: return True
        try: 
            if lists.current_map[1][int((new_pos_Y-hitbox_size)//32)][int((new_pos_X+hitbox_size)//32)] != "000":    return True
        except: return True
        try: 
            if lists.current_map[1][int((new_pos_Y+hitbox_size)//32)][int((new_pos_X-hitbox_size)//32)] != "000":    return True
        except: return True
        try: 
            if lists.current_map[1][int((new_pos_Y-hitbox_size)//32)][int((new_pos_X-hitbox_size)//32)] != "000":    return True
        except: return True
        return False
    def negative_check_for_collisions(self, new_pos_X, new_pos_Y, hitbox_size):
        return not(self.check_for_collisions(new_pos_X, new_pos_Y, hitbox_size))
    colides =  check_for_collisions
    n_colides = negative_check_for_collisions


    def check_hitboxes(self, new_pos_X, new_pos_y, hitbox_size, self_name):
        entitys = list(lists.alive_entitys)
        try:    entitys.remove(self_name)
        except: pass
        entitys = [value for value in entitys if not "fireball" in value]
        for i in entitys:
            if math.dist((lists.name_dict[i].stats.pos.x, lists.name_dict[i].stats.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].stats.hitbox): return False
        return True
    def negative_check_hitboxes(self, new_pos_X, new_pos_y, hitbox_size, self_name):
        return not(self.check_hitboxes(new_pos_X, new_pos_y, hitbox_size, self_name))
    n_hitbox = negative_check_hitboxes
    hitbox = check_hitboxes


    def check_specific_entity_collision__type(self, new_pos_X, new_pos_y, hitbox_size, self_name, other_type):
        entitys = list(lists.alive_entitys)
        #entitys = [value for value in entitys if other_type in value]
        entitys = [value for value in entitys if not self_name in value]
        for i in entitys:
            # print((lists.name_dict[i]).stats.type)
            if (lists.name_dict[i]).stats.type != other_type:
                entitys[entitys.index(i)] = None
        entitys = [value for value in entitys if None != value]
        for i in entitys:
            if math.dist((lists.name_dict[i].stats.pos.x, lists.name_dict[i].stats.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].stats.hitbox): return (False, i)
        return (True, None)
    def negative_check_specific_entity_collision__type(self, new_pos_X, new_pos_y, hitbox_size, self_name, other_type):
        collision, name =  (self.check_specific_entity_collision__type(new_pos_X, new_pos_y, hitbox_size, self_name, other_type))
        return (not(collision), name)
    specific_hitbox__type = check_specific_entity_collision__type
    n_specific_hitbox__type = negative_check_specific_entity_collision__type

    def check_specific_entity_collision__name(self, new_pos_X, new_pos_y, hitbox_size, self_name, other_name):
        entitys = list(lists.alive_entitys)
        entitys = [value for value in entitys if not self_name in value]
        for i in entitys:
            if i != other_name:
                entitys.pop(entitys.index(i))
        for i in entitys:
            if math.dist((lists.name_dict[i].stats.pos.x, lists.name_dict[i].stats.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].stats.hitbox): return (False, i)
        return (True, None)
    def negative_check_specific_entity_collision__name(self, new_pos_X, new_pos_y, hitbox_size, self_name, other_name):
        collision, name =  (self.check_specific_entity_collision__name(new_pos_X, new_pos_y, hitbox_size, self_name, other_name))
        return (not(collision), name)
    specific_hitbox__name = check_specific_entity_collision__name
    n_specific_hitbox__name = negative_check_specific_entity_collision__name

Collisions = class_Collisions()
