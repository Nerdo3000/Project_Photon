import logger
logger.log("Session started!")

import map_generator; logger.log("Map Generated!")
import pygame; logger.log("Pygame Import Successfull!")
import tile_scripts as TS; logger.log("Tile Import Successfull!")
import lists; logger.log("Lists Import Successfull!")
import pygame_setup as setup; logger.log("Setup Successfull!")

TILES = TS.TILES()
lists.current_map = TILES.load_map()
logger.log("Starting map data: " + str(lists.current_map))
TILES.preload_tiles(lists.current_map)
logger.log("Tiles Preloaded!")

import entitys.entity_manager as entitys; logger.log("Entity manager Import Successfull!")

entitys.make_pathgrid(); logger.log("Pathgrid Generated!")
entitys.tick_all()

logger.log("Entering Main Loop!")

while setup.running:
    #pygame.draw.rect(setup.screen, (0,0,0), pygame.Rect(0, 0, setup.screen.get_width(), setup.screen.get_height()))
    
    logger.write("="*200)
    leng = (200-(len("Tick "+str(setup.ticks))))//2; logger.write("="*leng+"Tick "+str(setup.ticks)+"="*leng)
    logger.write("="*200)

    events = pygame.event.get()
    if "Quit" in str(events):
        setup.running = False

    entitys.tick_all()
    TILES.draw()
    
    setup.mouse_keyboard.update_mouse_keyboard()
  
    if setup.mouse_keyboard.show_pathgrid:
        if (setup.ticks%10 == 9):  TILES.load_pathgird(lists.current_map, lists.path_dict["PLAYER"])
        try:
            if (setup.ticks>30):       TILES.draw_pathgrid()
        except AttributeError: pass

    entitys.draw_all()
    
    setup.mouse_keyboard.draw_mouse()

    pygame.display.flip()
    setup.delta = setup.clock.tick(60) / 1000 #40 ticks per second ###New: 25 ticks per second
    setup.ticks += 1
    logger.log("Alive Entitys: " + str(lists.alive_entitys))
    logger.log("Delta Time: "+str(setup.delta))


logger.write(("="*200)); logger.write(("="*200)); logger.write(("="*200)); logger.write(("="*200)); logger.write(("="*200)); logger.write(("="*200))
logger.log("Application Terminated!")
pygame.quit()
TILES.deload_map()
