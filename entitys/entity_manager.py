import pygame
import pygame_setup as setup 
import entitys.entity as entity
import math
import entitys.entity_general_code as ent
import extra_math as mthd
import lists
import numpy

respawn_timer = 40*3

stats = lists.stats()

def add_entitys():
    add_entity(stats.player_HEAL_unlim)
    for i in range(0):
        add_entity(stats.var(stats.REDGUY_OP_lim, "REDGUY"+str(i), 0))
    for i in range(50):
        add_entity(stats.var(stats.VIOGUY_sword_lim, "VIOGUY"+str(i), 0))#VIOGUY_basic_lim

def add_entity(values):
    lists.to_spawn_ent.append(values)
    lists.respawn_counter[values[0]] = values[4]

def try_summon_all():
    global respawn_timer
    if respawn_timer <= 0: 
        for i in lists.to_spawn_ent:
            if lists.respawn_counter[i[0]]>0:
                succes = try_summon(predifined_values=i)
                if succes:   respawn_timer = 40;    lists.respawn_counter[i[0]] -= 1;   break

def tick_all():
    try_summon_all()
    if (setup.ticks%10 == 9): 
        pathgriders = []
        for i in lists.alive_entitys:
            if (lists.name_dict[i]).type == "HUM":
                pathgriders.append(i)
                if not i in lists.path_dict:
                    layers = int(lists.current_map.shape[0])
                    lists.path_dict[i]= layers
                    lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((layers+1, 23, 40))
        update_pathgrids(pathgriders)
    for name in lists.alive_entitys:
        (lists.name_dict[name]).tick()
    global respawn_timer
    respawn_timer-=1

def draw_all():
    draw_sequence = order_draw_sequence()
    for name in draw_sequence:
        (lists.name_dict[name]).draw()

def make_pathgrid():
    lists.path_grid = numpy.full((1, 23, 40), "000")
    for y in range((lists.current_map.shape[1])):
        for x in range((lists.current_map.shape[2])):
            if lists.current_map[1,y,x] != "000":
                lists.path_grid[0,y,x] = "###"
            else:
                lists.path_grid[0,y,x] = "QQQ"

def update_pathgrids(grid_names):
    for i in grid_names:
        lists.current_map[lists.path_dict[i]] = update_pathgrid(i)

def update_pathgrid(target_name):
    path_grid = numpy.array(lists.path_grid)
    startX = int((lists.name_dict[target_name]).vars.pos.x//32)
    startY = int((lists.name_dict[target_name]).vars.pos.y//32)
    startZ = 0
    path_grid[startZ, startY, startX] = "000"
    to_do = [(startZ, startY, startX)]
    while len(to_do)>0:
        current_pos = to_do.pop(0) 
        for i in range(4):
            dir = (i*90)%360
            if dir==270: dir=-90
            next_pos = (startZ, int(current_pos[1]+ math.cos(math.radians(dir))), int(current_pos[2]+ math.sin(math.radians(dir))))
            try:
                if path_grid[next_pos]=="QQQ":
                    path_grid[next_pos] = dir
                    to_do.append(next_pos)
            except:
                pass
    return path_grid

def order_draw_sequence():
    ordering_dictionary = {}
    for i in (lists.alive_entitys):
        ordering_dictionary[i] = ((lists.name_dict[i]).vars.pos.y + 100000000*int((lists.name_dict[i]).vars.conditions.dead))
    ordering_dictionary = dict(sorted(ordering_dictionary.items(), key=lambda x:x[1]))
    return list(ordering_dictionary.keys())

def try_summon(name="???", nick="???", other=[], spd = 128, respawns=math.inf, weapons=(False, False, False), predifined_values = ()):
    if predifined_values != (): name, nick, other, spd, respawns, weapons = predifined_values
    if not name in lists.alive_entitys:
        entity.entity_summoner.summon_HUMANOID(name,nick,target_Ent=other, spd=spd, weapons=weapons)
        if not name in lists.path_dict:
            lists.path_dict[name] = layers = int(lists.current_map.shape[0])
            lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((layers+1, 23, 40))
            update_pathgrid(name)
        return True
    return False

add_entitys()
