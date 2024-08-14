import pygame
import pygame.freetype
import extra_math as mthd
import lists
import math

running = True
delta = 0
ticks = 0

pygame.init()
window = pygame.display.set_mode((1280, 736))
screen = pygame.Surface((1280, 736))
icon = pygame.image.load("img/icons_/Project_Photon_icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Project Photon Prototype", "Project Photon")

clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
delta_list = []
pause = False

cursor_img = pygame.image.load('img/icons_/cursor.png')
mouse_img = pygame.image.load("img/icons_/mouse.png")

pygame.freetype.init()
font = pygame.freetype.Font(None, 36)

camera_pos = mthd.Position(0,0)

map_width = 80
map_height = 46

class _mouse_keyboard:
    def __init__(self):
        self.mouse_custom_pos = mthd.Position()
        self.click = 0
        self.right_click = False
        self.spacebar = False 
        self.shift = False
        self.ULTIMATE_POWER = False 
        self.show_pathgrid = False
        self.joystick = mthd.Position()
        self.click_wait = 0
        self.pause_wait = 0

    def update_mouse_keyboard(self):
        self.mouse_custom_pos.xy = tuple(pygame.mouse.get_pos())
        self.click = pygame.mouse.get_pressed()
        self.joystick = mthd.Position()
        self.pause = False
        self.spacebar = False; self.shift = False; self.ULTIMATE_POWER=False
        self.show_minimap =  False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:   self.joystick.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.joystick.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.joystick.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:self.joystick.x += 1

        if keys[pygame.K_SPACE]:                    self.spacebar = True
        if keys[pygame.K_LSHIFT]:                   self.shift = True
        if keys[pygame.K_LESS]:                     self.shift = True
        if keys[pygame.K_x]:                        self.ULTIMATE_POWER = True
        if keys[pygame.K_NUMLOCK]:                  self.show_pathgrid = not(self.show_pathgrid)
        if keys[pygame.K_m]:                        self.show_minimap = True

        self.pause_wait -= 1
        if self.pause_wait<0:
            if keys[pygame.K_ESCAPE] or keys[pygame.K_p]: self.pause = True; self.pause_wait = 15

        self.right_click = self.click[0]
        if self.click_wait>0: self.right_click = False
        self.click_wait -= 1

    def draw_mouse(self, mode):
        if mode=="normal":
            rot = False
            for ent in lists.alive_entitys:
                xy = (lists.name_dict[ent]).stats.pos.xy
                dis = math.dist(xy, (self.mouse_custom_pos.x+camera_pos.x, self.mouse_custom_pos.y+camera_pos.y))
                if dis < 25: rot = True
            if rot:     cursor_img_draw = pygame.transform.rotate(cursor_img, 45)
            else:       cursor_img_draw = cursor_img
            screen.blit(cursor_img_draw, (self.mouse_custom_pos.x - 18-(rot*9), self.mouse_custom_pos.y - 18-(rot*9)))
        else:
            screen.blit(mouse_img, (self.mouse_custom_pos.x, self.mouse_custom_pos.y))

mouse_keyboard = _mouse_keyboard()

def camera_positioning_at_edges(tmp_cam_pos_x, tmp_cam_pos_y):
    if tmp_cam_pos_x < 0:
        tmp_cam_pos_x = 0
    if tmp_cam_pos_y < 0:
        tmp_cam_pos_y = 0
    if tmp_cam_pos_x > ((map_width*32))-(screen.get_width()):
        tmp_cam_pos_x = ((map_width*32))-(screen.get_width())
    if tmp_cam_pos_y > ((map_height*32))-(screen.get_height()):
        tmp_cam_pos_y = ((map_height*32))-(screen.get_height())
    return tmp_cam_pos_x, tmp_cam_pos_y

def move_camera():
    try:
        tmp_cam_pos_x = ((lists.name_dict["PLAYER"]).stats.pos.x)-(screen.get_width()/2)
        tmp_cam_pos_y = ((lists.name_dict["PLAYER"]).stats.pos.y)-(screen.get_height()/2)

        tmp_cam_pos_x, tmp_cam_pos_y = camera_positioning_at_edges(tmp_cam_pos_x, tmp_cam_pos_y)

        if (lists.name_dict["PLAYER"]).stats.conditions.plop_animation<60:
            old_cam_pos = camera_pos
            new_cam_pos_x = tmp_cam_pos_x
            new_cam_pos_y = tmp_cam_pos_y
            dist = math.dist(old_cam_pos.xy, (new_cam_pos_x, new_cam_pos_y))
            if dist>0.5: 
                dir = (mthd.maths.atan3(new_cam_pos_x-old_cam_pos.x, old_cam_pos.y-new_cam_pos_y)-270) % 360
                dir = mthd.maths.transform_direction(dir)

                x = math.sin(math.radians(dir))
                y = math.cos(math.radians(dir))

                new_cam_pos_x = camera_pos.x
                new_cam_pos_y = camera_pos.y

                change_x = math.copysign((abs(x*dist)**0.6), x)
                change_y = math.copysign((abs(y*dist)**0.6), y)

                new_cam_pos_x += change_x
                new_cam_pos_y += change_y

                new_cam_pos_x, new_cam_pos_y = camera_positioning_at_edges(new_cam_pos_x, new_cam_pos_y)
        else: 
            new_cam_pos_x = tmp_cam_pos_x
            new_cam_pos_y = tmp_cam_pos_y
        camera_pos.xy = (new_cam_pos_x, new_cam_pos_y) 
    except KeyError:pass