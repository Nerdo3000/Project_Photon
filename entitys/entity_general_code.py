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

class weapons:
    def __init__(self, weapons):
        if len(weapons)<3:
            self.fireball = False
            self.sword = False
            self.up = False
        else:
            self.fireball = weapons[0]
            self.sword = weapons[1]
            self.up = weapons[2]

class Conditions:
    def __init__(self):
        self.stunned = 0
        self.dead = False
        self.throw_cooldown = 0
        self.ball_dead = True
        self.velocity_dir = mthd.Position(0,0)
        self.velocity_time = 0
        self.sword_cooldown = 0
        self.dash_cooldown = 0
        self.animation_invisible = False
        self.invulenarbility = 0
        self.blocked = 0
        self.counter_till_death = 0
        self.ULTI_cooldown = 0
        self.vamp_healing = 0
        self.ULTI_healing = 0
        self.exp_stunning_backoff = 1

class basic_entity_variables():
    def __init__(self, startpos=(0,0), move_speed=0, dir=0, hitbox=0, name="???", nick="", owner=None, target_Ent=None, weapon=()):
        self.pos = mthd.Position(startpos[0], startpos[1])
        self.move_speed = move_speed
        self.target_ent = target_Ent
        self.dir = dir
        self.hitbox = hitbox
        self.name = name
        self.nick_name = nick
        self.owner = owner
        self.conditions = Conditions()
        self.inputs = Entity_inputs()
        self.max_hp = self.hp = 10
        self.IMG_PATH_head = "img/humanoid_/head/"
        self.IMG_PATH_body = "img/humanoid_/body/"
        self.alpha_fade = 255
        self.weapons = weapons(weapon)

class visuals:
    def blit(image, posx=None, posy=None, scale=1, dir=0):
        if scale!=1: image = pygame.transform.rotozoom(image, dir, scale)
        setup.screen.blit(image, (posx, posy))
    
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
            if math.dist((lists.name_dict[i].vars.pos.x, lists.name_dict[i].vars.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].vars.hitbox): return False
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
            if (lists.name_dict[i]).type != other_type:
                entitys[entitys.index(i)] = None
        entitys = [value for value in entitys if None != value]
        for i in entitys:
            if math.dist((lists.name_dict[i].vars.pos.x, lists.name_dict[i].vars.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].vars.hitbox): return (False, i)
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
            if math.dist((lists.name_dict[i].vars.pos.x, lists.name_dict[i].vars.pos.y), (new_pos_X, new_pos_y)) < (hitbox_size)+(lists.name_dict[i].vars.hitbox): return (False, i)
        return (True, None)
    def negative_check_specific_entity_collision__name(self, new_pos_X, new_pos_y, hitbox_size, self_name, other_name):
        collision, name =  (self.check_specific_entity_collision__name(new_pos_X, new_pos_y, hitbox_size, self_name, other_name))
        return (not(collision), name)
    specific_hitbox__name = check_specific_entity_collision__name
    n_specific_hitbox__name = negative_check_specific_entity_collision__name

Collisions = class_Collisions()
