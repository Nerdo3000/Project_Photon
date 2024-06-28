import pygame
import extra_math as mthd
import lists

running = True
delta = 0
ticks = 0

pygame.init()
screen = pygame.display.set_mode((1280, 736))
icon = pygame.image.load("img/icons_/Project_Photon_icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Project Photon Prototype", "Project Photon")

clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

cursor_img = pygame.image.load('img/icons_/cursor.png')

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
        self._wait = 0

    def update_mouse_keyboard(self):
        self.mouse_custom_pos.xy = tuple(pygame.mouse.get_pos())
        self.click = pygame.mouse.get_pressed()
        self.joystick = mthd.Position()
        self.spacebar = False; self.shift = False; self.ULTIMATE_POWER=False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:   self.joystick.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.joystick.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.joystick.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:self.joystick.x += 1

        if keys[pygame.K_SPACE]:                    self.spacebar = True
        if keys[pygame.K_LSHIFT]:                   self.shift = True
        if keys[pygame.K_LESS]:                     self.shift = True
        if keys[pygame.K_x]:                        self.ULTIMATE_POWER = True
        if keys[pygame.K_p]:                        self.show_pathgrid = not(self.show_pathgrid)
        self.right_click = self.click[0]

        if self.right_click and lists.slow_motion: 
            lists.slow_motion = False
            self._wait = 30
            (lists.name_dict["PLAYER"]).vars.pos.xy = self.mouse_custom_pos.xy
        if self._wait>0: self.right_click = False
        self._wait -= 1

    def draw_mouse(self):
        screen.blit(cursor_img, (self.mouse_custom_pos.x - 18, self.mouse_custom_pos.y - 18))
mouse_keyboard = _mouse_keyboard()