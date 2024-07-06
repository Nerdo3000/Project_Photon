import pygame
import log_set.settings as settings
import pygame_setup as setup 
import entitys.entity as entity
import math
import entitys.entity_general_code as ent
import extra_math as mthd
import lists
import numpy

respawn_timer = setup.map_width*3

stats = lists.stats()

def add_entitys():
    for i in range(settings.player_amount):
        add_entity(stats.stats_dict[settings.player_stats])
    for i in range(settings.REDGUY_amount):
        add_entity(stats.var(stats.stats_dict[settings.REDGUY_stats], "REDGUY"+str(i), 0))
    for i in range(settings.VIOGUY_amount):
        add_entity(stats.var(stats.stats_dict[settings.VIOGUY_stats], "VIOGUY"+str(i), 0))

def add_entity(values):
    lists.to_spawn_ent.append(values)
    lists.respawn_counter[values[0]] = values[4]

def try_summon_all():
    global respawn_timer
    if respawn_timer <= 0: 
        for i in lists.to_spawn_ent:
            if lists.respawn_counter[i[0]]>0:
                succes = try_summon(predifined_values=i)
                if succes:   respawn_timer = setup.map_width;    lists.respawn_counter[i[0]] -= 1;   break

def tick_all():
    if not lists.slow_motion:
        try_summon_all()
        for n in (range(lists.highest,0,-10)):
            if (setup.ticks%n == n-1): 
                m = lists.centered_square_num[n]
                pathgriders = []
                for i in lists.pathfinding_requests:
                    if (lists.name_dict[i]).type == "HUM":
                        pathgriders.append(i)
                        if not i in lists.path_dict:
                            layers = int(lists.current_map.shape[0])
                            lists.path_dict[i]= layers
                            lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((layers+1, setup.map_height, setup.map_width))
                lists.pathfinding_requests = []
                update_pathgrids(pathgriders, max_idx=m)
                break
    for name in lists.alive_entitys:
        (lists.name_dict[name]).tick()
    global respawn_timer
    respawn_timer-=1

def draw_all():
    draw_sequence = order_draw_sequence()
    for name in draw_sequence:
        if (setup.camera_pos.x+setup.screen.get_width()+100)>(lists.name_dict[name]).vars.pos.x and (setup.camera_pos.x-100)<(lists.name_dict[name]).vars.pos.x:
            if (setup.camera_pos.y+setup.screen.get_height()+100)>(lists.name_dict[name]).vars.pos.y and (setup.camera_pos.y-100)<(lists.name_dict[name]).vars.pos.y:
                (lists.name_dict[name]).draw()

def make_pathgrid():
    lists.path_grid = numpy.full((1, setup.map_height, setup.map_width), "000")
    for y in range((lists.current_map.shape[1])):
        for x in range((lists.current_map.shape[2])):
            if lists.current_map[1,y,x] != "000":
                lists.path_grid[0,y,x] = "###"
            else:
                lists.path_grid[0,y,x] = "QQQ"
    lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((int(lists.current_map.shape[0])+1, setup.map_height, setup.map_width))

def update_pathgrids(grid_names, max_idx=math.inf):
    for i in grid_names:
        new = update_pathgrid(i, max_idx=max_idx)
        mask = (new == "QQQ")
        new_array = numpy.copy(new)
        old = lists.current_map[lists.path_dict[i]]
        new_array[mask] = old[mask]
        lists.current_map[lists.path_dict[i]] = new_array

def update_pathgrid(target_name, max_idx=math.inf):
    did_idx = 0
    path_grid = numpy.array(lists.path_grid).reshape((setup.map_height, setup.map_width))   #lists.current_map[lists.path_dict[target_name]] 
    startX = int((lists.name_dict[target_name]).vars.pos.x//32)
    startY = int((lists.name_dict[target_name]).vars.pos.y//32)
    path_grid[startY, startX] = "000"
    to_do = [(startY, startX)]
    while not(len(to_do)<=0 or did_idx>max_idx):
        #print(len(to_do))
        current_pos = to_do.pop(0) 
        for i in range(4):
            dir = (i*90)%360
            if dir==270: dir=-90
            next_pos = (int(current_pos[0]+ math.cos(math.radians(dir))), int(current_pos[1]+ math.sin(math.radians(dir))))
            try:
                if path_grid[next_pos]=="QQQ":
                    path_grid[next_pos] = dir
                    to_do.append(next_pos)
            except IndexError:
                pass
        did_idx += 1
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
            lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((layers+1, setup.map_height, setup.map_width))
            update_pathgrid(name)
        return True
    return False

add_entitys()
