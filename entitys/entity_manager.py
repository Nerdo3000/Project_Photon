import pygame
import log_set.settings as settings
import pygame_setup as setup 
import entitys.entity as entity
import math
import entitys.entity_general_code as ent
import extra_math as mthd
import lists
import numpy
import random

respawn_timer = setup.map_width*3

lists.highest = math.ceil(math.ceil((((setup.map_height*setup.map_width)-1)/2)**0.5+1)/10)*10

def add_entitys():
    for i in range(settings.player_amount):
        add_entity(stats_block=settings.player_stats)
    for i in range(settings.REDGUY_amount):
        add_entity("REDGUY"+str(i), stats_block=settings.REDGUY_stats)
    for i in range(settings.VIOGUY_amount):
        add_entity("VIOGUY"+str(i), stats_block=settings.VIOGUY_stats)

def add_entity(name=None, stats_block=None):
    if stats_block != None:
        if name == None:    name = lists.stats["HUMANOID"][stats_block]["name"]
        lists.to_spawn_ent.append(name)
        lists.to_spawn_ent_stats[name] = stats_block
        lists.respawn_counter[name] = lists.stats["HUMANOID"][stats_block]["respawns"]

def try_summon_all():
    global respawn_timer
    if respawn_timer <= 0: 
        for name in lists.to_spawn_ent:
            if lists.respawn_counter[name]!=0:
                succes = try_summon(lists.to_spawn_ent_stats[name], name)
                if succes:   respawn_timer = 40;    lists.respawn_counter[name] -= 1;   break

def tick_all():
    if not lists.slow_motion:
        try_summon_all()
        for n in (range(lists.highest,0,-10)):
            if (setup.ticks%n == n-1): 
                m = lists.centered_square_num[n]
                pathgriders = []
                for i in lists.pathfinding_requests:
                    if (lists.name_dict[i]).stats.type == "HUM":
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
        if (setup.camera_pos.x+setup.screen.get_width()+100)>(lists.name_dict[name]).stats.pos.x and (setup.camera_pos.x-100)<(lists.name_dict[name]).stats.pos.x:
            if (setup.camera_pos.y+setup.screen.get_height()+100)>(lists.name_dict[name]).stats.pos.y and (setup.camera_pos.y-100)<(lists.name_dict[name]).stats.pos.y:
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
        x = int((lists.name_dict[i]).stats.pos.x//32)
        y = int((lists.name_dict[i]).stats.pos.y//32)
        new = update_pathgrid(x, y, max_idx=max_idx)
        mask = (new == "QQQ")
        new_array = numpy.copy(new)
        old = lists.current_map[lists.path_dict[i]]
        new_array[mask] = old[mask]
        lists.current_map[lists.path_dict[i]] = new_array

def update_pathgrid(target_x, target_y, max_idx=math.inf, start_val="000"):
    did_idx = 0
    path_grid = numpy.array(lists.path_grid).reshape((setup.map_height, setup.map_width))   #lists.current_map[lists.path_dict[target_name]] 
    startX = int(target_x)
    startY = int(target_y)
    path_grid[startY, startX] = start_val
    to_do = [(startY, startX)]
    while len(to_do)>0 and did_idx<max_idx:   
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
        ordering_dictionary[i] = ((lists.name_dict[i]).stats.pos.y + 100000000*int((lists.name_dict[i]).stats.conditions.dead))
    ordering_dictionary = dict(sorted(ordering_dictionary.items(), key=lambda x:x[1]))
    return list(ordering_dictionary.keys())

def try_summon(stats_block, name="???"):
    if not name in lists.alive_entitys:
        entity.entity_summoner.summon_HUMANOID(stats_block, name)
        if not name in lists.path_dict:
            lists.path_dict[name] = layers = int(lists.current_map.shape[0])
            lists.current_map = (numpy.append(lists.current_map, lists.path_grid)).reshape((layers+1, setup.map_height, setup.map_width))
            update_pathgrid(int((lists.name_dict[name]).stats.pos.x//32), int((lists.name_dict[name]).stats.pos.y//32))
        return True
    return False

def generate_patrol_checkpoints_positions():
    points = []
    for i in range(10000):
        x1 = random.randint(32, (setup.map_width-1)*32)
        y1 = random.randint(32, (setup.map_height-1)*32)
        gdg = True
        for xy in points:
            dist = math.dist((x1, y1), xy)
            if dist<738/2 or lists.current_map[1, y1//32, x1//32]!="000":
                gdg = False
                break
            else: continue
        if gdg: points.append((x1, y1))
    return points

def generate_patrol_checkpoints_pathgrids():
    points = generate_patrol_checkpoints_positions()

    n = 0
    for point in points:
        point = mthd.Position(point[0]//32, point[1]//32)
        generate_pathgrid_for_patrol_point(point, n)

        n += 1
    lists.number_of_patrol_points = n-1

def generate_pathgrid_for_patrol_point(point, n):
    layers = int(lists.current_map.shape[0])
    lists.path_dict[("Patrol Point "+str(n))] = layers
    new = update_pathgrid(point.x, point.y, start_val="!!!")
    if (new=="QQQ").sum() > 0.6*setup.map_height*setup.map_width:
        new_point = mthd.Position((point.x+random.randint(-1,1))%setup.map_width, (point.y+random.randint(-1,1))%setup.map_width)
        generate_pathgrid_for_patrol_point(new_point, n)
    else:
        lists.current_map = (numpy.append(lists.current_map, new)).reshape((layers+1, setup.map_height, setup.map_width))


add_entitys()
