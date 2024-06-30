import log_set.logger as logger;    logger.log("Session started!")
import log_set.settings as settings
import math
import extra_math as mthd

if settings.new_random_map:import map_generator;logger.log("New Map Generated!")
import pygame;                                  logger.log("Pygame Import Successfull!")
import tile_scripts as TS;                      logger.log("Tile Import Successfull!")
import lists;                                   logger.log("Lists Import Successfull!")
import pygame_setup as setup;                   logger.log("Setup Successfull!")

TILES = TS.TILES()
lists.current_map = TILES.load_map();           logger.log("Starting map data: " + str(lists.current_map))
TILES.preload_tiles(lists.current_map);         logger.log("Tiles Preloaded!")


import entitys.entity_manager as entitys;       logger.log("Entity manager Import Successfull!")

entitys.make_pathgrid();                        logger.log("Pathgrid Generated!")
entitys.tick_all()

def draw_all():
    TILES.draw()
  
    if setup.mouse_keyboard.show_pathgrid:
        if (setup.ticks%10 == 9):  TILES.load_pathgird(lists.current_map, lists.path_dict["PLAYER"])
        try:
            if (setup.ticks>30):       TILES.draw_pathgrid()
        except AttributeError: pass

    entitys.draw_all()

def mode__normal():
    #pygame.draw.rect(setup.screen, (0,0,0), pygame.Rect(0, 0, setup.screen.get_width(), setup.screen.get_height()))
    logger.write("="*200)
    leng = (200-(len("Tick "+str(setup.ticks))))//2; logger.write("="*leng+"Tick "+str(setup.ticks)+"="*leng)
    logger.write("="*200)

    entitys.tick_all()

    try:
        tmp_cam_pos_x = ((lists.name_dict["PLAYER"]).vars.pos.x)-(setup.screen.get_width()/2)
        tmp_cam_pos_y = ((lists.name_dict["PLAYER"]).vars.pos.y)-(setup.screen.get_height()/2)
        if tmp_cam_pos_x+(setup.screen.get_width()/2) < (setup.screen.get_width())/2:
            tmp_cam_pos_x = 0
        if tmp_cam_pos_y+(setup.screen.get_height()/2) < (setup.screen.get_height())/2:
            tmp_cam_pos_y = 0
        if tmp_cam_pos_x > ((setup.map_width*32))-(setup.screen.get_width()/2)*2:
            tmp_cam_pos_x = ((setup.map_width*32))-(setup.screen.get_width()/2)*2
        if tmp_cam_pos_y > ((setup.map_height*32))-(setup.screen.get_height()/2)*2:
            tmp_cam_pos_y = ((setup.map_height*32))-(setup.screen.get_height()/2)*2
        if (lists.name_dict["PLAYER"]).vars.conditions.plop_animation<30:
            old_cam_pos = setup.camera_pos
            new_cam_pos_x = tmp_cam_pos_x
            new_cam_pos_y = tmp_cam_pos_y
            dir = (mthd.maths.atan3(new_cam_pos_x-old_cam_pos.x, old_cam_pos.y-new_cam_pos_y)-270) % 360
            dir = mthd.maths.transform_direction(dir)
            dist = math.dist(old_cam_pos.xy, (new_cam_pos_x, new_cam_pos_y))
            #print(dir)

            x = math.sin(math.radians(dir))
            y = math.cos(math.radians(dir))

            new_cam_pos_x = setup.camera_pos.x
            new_cam_pos_y = setup.camera_pos.y

            change_x = math.copysign((abs(x*dist)**0.7), x)
            change_y = math.copysign((abs(y*dist)**0.7), y)
            print(dist,change_x) #x*dist/4

            #"""
            new_cam_pos_x += change_x
            new_cam_pos_y += change_y
            #"""
            """
            dif_x = new_cam_pos_x - old_cam_pos.x
            new_cam_pos_x = setup.camera_pos.x
            change = math.copysign((abs(dif_x)**0.7), dif_x)*x
            if abs(change)<0.25: change=0
            new_cam_pos_x += change

            dif_y = new_cam_pos_y - old_cam_pos.y
            new_cam_pos_y = setup.camera_pos.y
            change = math.copysign((abs(dif_y)**0.7), dif_y)*y
            if abs(change)<0.25: change=0
            new_cam_pos_y += change
            """
        else: 
            new_cam_pos_x = tmp_cam_pos_x
            new_cam_pos_y = tmp_cam_pos_y
        setup.camera_pos.xy = (new_cam_pos_x, new_cam_pos_y) 
    except KeyError:pass

    draw_all()
    setup.mouse_keyboard.draw_mouse()

    if lists.slow_motion:
        old_screen = pygame.Surface.copy(setup.screen)
        pygame.transform.grayscale(setup.screen, setup.screen)
        setup.screen.blit(old_screen, (0,0), special_flags=pygame.BLEND_MAX)

    logger.log("Alive Entitys: " + str(lists.alive_entitys))
    logger.log("Delta Time: "+str(setup.delta))

def mode__pause():
    draw_all()
    pygame.transform.grayscale(setup.screen, setup.screen)
    setup.mouse_keyboard.draw_mouse()

logger.log("Entering Main Loop!")
while setup.running:
    events = pygame.event.get()
    if "Quit" in str(events):
        setup.running = False
    setup.mouse_keyboard.update_mouse_keyboard()

    if setup.mouse_keyboard.pause:
        if not setup.pause: setup.pause = True
        elif setup.pause: setup.pause = False

    if setup.pause:
        mode__pause()
    else:
        mode__normal()

    setup.window.blit(setup.screen, (0,0))
    pygame.display.flip()

    setup.delta = setup.clock.tick(60) / 1000 #setup.map_width ticks per second ###New: 25 ticks per second
    setup.ticks += 1


logger.write(("="*200), amt=6)
logger.log("Application Terminated!")
pygame.quit()
TILES.deload_map()
