import pygame
import pygame_setup as setup
import math
import random
import extra_math as mthd
import entitys.entity_general_code as ent
import lists
from types import SimpleNamespace
import json

class HUMANOID:
    "The Humanoid Entity class."
    def __init__(self, stats_block, name, start_modXY=(0, 0)):
        """Initialisation of the Humanoid charakter. Setting up the Humanoids: speed, position, direction, Animitaion frame, Image and cooldown variables."""
        self.stats = json.loads(json.dumps((lists.stats["HUMANOID"][stats_block])), object_hook=lambda item: SimpleNamespace(**item)) #Dark Magic
        self.stats.name = name
        self.stats.conditions.plop_animation = math.inf
        self.stats.conditions.velocity_dir = mthd.Position(0,0)
        self.stats.inputs = ent.Entity_inputs()
        self.stats.pos = mthd.Position(start_modXY[0], start_modXY[1])

    def tick(self):
        """Ticks the humanoid: Moving the humanoid, fireball throwing and updating variables like the animation frame and cooldown variables."""
        if lists.slow_motion:
            if self.stats.name!="PLAYER": return
            else:
                if setup.mouse_keyboard.right_click: 
                    setup.mouse_keyboard.click_wait = 30
                    self.stats.pos.xy = (setup.mouse_keyboard.mouse_custom_pos.x+setup.camera_pos.x, setup.mouse_keyboard.mouse_custom_pos.y+setup.camera_pos.y)
                    self.stats.conditions.plop_animation = 0
                    lists.slow_motion = False
                    if self.stats.hp <= 8: self.stats.hp += 2
                return
            
        if not self.stats.conditions.dead:
            self.update_and_reset()

            if (self.stats.conditions.stunned <= 0) and(self.stats.conditions.throw_cooldown+2) <= 0 and (self.stats.conditions.sword_cooldown+4)<=0:
                if self.stats.name == 'PLAYER':      self.PLAYER_controller()
                if 'GUY' in self.stats.name:         self.AI_controller()

            self.trigger_ULTI()

            if self.stats.conditions.ULTI_invis<0:
                self.stats.alpha_fade = 255

            if self.stats.conditions.ball_dead and self.stats.inputs.try_throw_fireball:
                if self.stats.weapons.fireball=="one":   self.stats.dir = entity_summoner.summon_fireball(self.stats.pos, self.stats.inputs.fireball_target, self.stats.inputs.throw_mod, owner=self.stats.name)
                if self.stats.weapons.fireball=="wave":  self.stats.dir = entity_summoner.summon_fireball_wave(self.stats.pos, self.stats.inputs.fireball_target, self.stats.inputs.throw_mod, owner=self.stats.name)
                self.stats.conditions.throw_cooldown = 5
            elif (self.stats.conditions.sword_cooldown+4)<=0 and self.stats.inputs.try_sword:
                self.stats.conditions.sword_cooldown = 5

            self.movement()

            self.hit()
            
        else:
            self.stats.alpha_fade -= 20
            if self.stats.alpha_fade <=0: lists.KILL_entity(self.stats.name)

    def PLAYER_controller(self):
        "Getting the Controls of the Player Charakter/User."
        self.stats.inputs.throw_mod = random.randint(-10, 10) * lists.hardness
        self.stats.inputs.joystick.xy = setup.mouse_keyboard.joystick.xy
        if self.stats.weapons.fireball != False: self.stats.inputs.try_throw_fireball = setup.mouse_keyboard.right_click
        self.stats.inputs.fireball_target = mthd.Position(setup.mouse_keyboard.mouse_custom_pos.x, setup.mouse_keyboard.mouse_custom_pos.y)
        self.stats.inputs.fireball_target.add(setup.camera_pos.x, setup.camera_pos.y)
        self.stats.inputs.try_sword = setup.mouse_keyboard.spacebar
        self.stats.inputs.try_dash = setup.mouse_keyboard.shift
        self.stats.inputs.ULTI = setup.mouse_keyboard.ULTIMATE_POWER
        if self.stats.inputs.try_dash:
            self.stats.conditions.dash_cooldown += 1
            if self.stats.conditions.dash_cooldown<0 and self.stats.inputs.joystick.xy != (0,0):
                self.stats.conditions.velocity_time = 20
                self.stats.conditions.dash_cooldown = 40
                self.stats.conditions.velocity_dir.xy = self.stats.inputs.joystick.xy
    
    def AI_controller(self):
        "Getting the Controls of the AI charakter, this includes walking, fireball throwing and fireball deflecting (sword)."
        possible_targets = []
        dists = {}
        if not "!G!" == self.stats.target_ent[0]:
            possible_targets = self.stats.target_ent
        else:
            for enemy in self.stats.target_ent[1:]:
                for name in lists.alive_entitys:
                    if (enemy in name) and not ("fireball" in name):
                        possible_targets.append(name)
        for target in possible_targets:
            try:
                if not (lists.name_dict[target]).stats.conditions.dead and ((lists.name_dict[target]).stats.conditions.ULTI_invis<0):
                        dist = math.dist(self.stats.pos.xy, (lists.name_dict[target]).stats.pos.xy)
                        if dist < self.stats.view_distance:
                            dists[dist] = target
            except KeyError:  pass
        if len(dists)>0:
            self.target_name = dists[(sorted((list(dists))))[0]]
            self.stats.inputs.fireball_target = (lists.name_dict[self.target_name]).stats.pos
            if not self.target_name in lists.pathfinding_requests:
                lists.pathfinding_requests.append(self.target_name)
        else: 
            try:
                if (round(self.last_pos.x, 1),round(self.last_pos.y, 1)) == (round(self.stats.pos.x, 1), round(self.stats.pos.y, 1)):
                    self.patrol_point_number = random.randint(0, lists.number_of_patrol_points)
            except AttributeError: pass
            self.last_pos = mthd.Position(self.stats.pos.x, self.stats.pos.y)

            try: self.patrol_point_number
            except AttributeError: self.patrol_point_number = random.randint(0, lists.number_of_patrol_points)

            try: targetpos = (lists.path_dict[self.target_name], int(self.stats.pos.y//32), int(self.stats.pos.x//32))
            except KeyError: pass
            # print(str(self.stats.name) + " | Target: " + str(self.target_name) + " of " + str(lists.number_of_patrol_points))
            if lists.current_map[targetpos] == "!!!": self.patrol_point_number = random.randint(0, lists.number_of_patrol_points)
            self.target_name = "Patrol Point "+str(self.patrol_point_number)

        if self.stats.weapons.sword:
            dont_try_fireball = self.AI__sword_controller()
            if dont_try_fireball=="r":return
        else:
            dont_try_fireball = False
        
        if "Patrol Point " in self.target_name:
            direct = False
        else:
            direct, dir = self.AI__fireball_and_direct_path_controller((self.stats.weapons.fireball!=False), dont_try_fireball)

        if not direct: dir = self.AI__pathgrid_controller()

        self.stats.inputs.joystick.xy = mthd.maths.sin(dir), mthd.maths.cos(dir)   
          
    def AI__sword_controller(self):
        collision, name = ent.Collisions.n_specific_hitbox__type(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox+256, self.stats.name, 'fireball')
        collision2, name2 = ent.Collisions.n_specific_hitbox__type(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox*3.5, self.stats.name, 'HUM')
        if collision: #FIREBALL DEFENSE
            collision, name = ent.Collisions.n_specific_hitbox__type(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox+6, self.stats.name, 'fireball')
            if collision and random.randint(1,3)!=1:
                self.stats.dir = int((math.degrees((lists.name_dict[name]).stats.dir)-45)//90*90%360)
                self.stats.dir = mthd.maths.transform_direction(self.stats.dir)
                self.stats.inputs.try_sword = True
                return "r"
            return True
        if collision2 and random.randint(1,10)==1 and (name2 in self.target_name):  #MEELE
            atan2dir= (mthd.maths.atan3(lists.name_dict[name2].stats.pos.x - self.stats.pos.x, lists.name_dict[name2].stats.pos.y - self.stats.pos.y)-270) % 360
            dir = (((atan2dir+45)//90*90)%360)
            dir = mthd.maths.transform_direction(dir)
            self.stats.dir = int(dir)
            self.stats.inputs.try_sword = True
            return "r"
        return False
    def AI__pathgrid_controller(self):
        try:
            targetpos = (lists.path_dict[self.target_name], int(self.stats.pos.y//32), int(self.stats.pos.x//32))
        except KeyError:
            print(setup.ticks, self.target_name)
            return 0
        targetval = lists.current_map[targetpos]
        if targetval == '###' or targetval == 'QQQ':     return mthd.maths.atan4(self.stats.inputs.fireball_target.x - self.stats.pos.x, self.stats.inputs.fireball_target.y - self.stats.pos.y) 
        elif targetval == "!!!": return 0
        else:
            try:        dir = (int(targetval) +180) % 360
            except:     print(targetval); print((0/0))
            target = mthd.Position(targetpos[2] * 32 + 32 * int(mthd.maths.sin(dir)) + 16,   targetpos[1] * 32 + 32 * int(mthd.maths.cos(dir)) + 16)
            return (mthd.maths.atan3(target.x - self.stats.pos.x, self.stats.pos.y - target.y)-270)%360
    def AI__fireball_and_direct_path_controller(self, fireball, dont_try_fireball):
        currentPos = mthd.Position(self.stats.pos.x, self.stats.pos.y)
        dir = mthd.maths.atan4(self.stats.inputs.fireball_target.x - currentPos.x, self.stats.inputs.fireball_target.y - currentPos.y)
        while True:
            dist = math.dist(currentPos.xy, self.stats.inputs.fireball_target.xy)
            if dist < 8:
                dist = math.dist(self.stats.inputs.fireball_target.xy, self.stats.pos.xy)
                if dist <= 256 and (self.stats.name + '_fireball' not in str(lists.alive_entitys)) and not dont_try_fireball:         #setup.map_width * setup.delta * 300:
                    self.stats.inputs.try_throw_fireball = fireball
                    self.stats.inputs.throw_mod = random.randint(-lists.entity_presision, lists.entity_presision)
                return True, dir 
            currentPos.add(mthd.maths.sin(dir) * 6, mthd.maths.cos(dir) * 6)
            if ent.Collisions.colides(currentPos.x, currentPos.y, 8): return False, dir

    def hit(self):
        attacker = self.ball_hit()
        attacker2 = self.sword_hit()
        if self.stats.hp<=0:
            self.stats.conditions.dead = True
            if attacker ==  None:
                (lists.name_dict[attacker2]).stats.conditions.vamp_healing = 30
            if attacker2 == None:
                (lists.name_dict[attacker]).stats.conditions.vamp_healing = 30
        else:
            if self.stats.conditions.vamp_healing > 0:
                self.stats.hp += 0.1
                if self.stats.hp > self.stats.max_hp: self.stats.hp = self.stats.max_hp
                self.stats.conditions.vamp_healing -= 1
            if self.stats.conditions.ULTI_healing > 0:
                self.stats.hp += 0.5
                if self.stats.hp > self.stats.max_hp: self.stats.hp = self.stats.max_hp
                self.stats.conditions.ULTI_healing -= 1
        if setup.ticks%300==0:
            self.stats.hp += 1
            if self.stats.hp > self.stats.max_hp: self.stats.hp = self.stats.max_hp

    def ball_hit(self):
        "Code for detcting if a Humanoid is hit by a fireball and checking if they deflect it sucessfully."
        collision, name = ent.Collisions.n_specific_hitbox__type(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox, self.stats.name, 'fireball')
        if collision and self.stats.conditions.invulenarbility < 0: 
            otherdir = (math.degrees((lists.name_dict[name]).stats.dir)+135)//90*90       
            owndir = (self.stats.dir+360)%360
            self.stats.conditions.invulenarbility = 20
            owner = (lists.name_dict[name]).stats.owner
            if self.stats.conditions.ULTI_healing > 0 or (self.stats.conditions.sword_cooldown>0 and (otherdir != owndir) and not(self.stats.conditions.blocked>14) and (random.randint(1,5)!=1) and not (lists.name_dict[name]).stats.unblock):
                amaing = ((mthd.maths.atan3((self.stats.inputs.fireball_target.x - self.stats.pos.x), (self.stats.inputs.fireball_target.y - self.stats.pos.y)))+90) + random.randint(-25, 25)  #math.degrees((setup.name_dict[name]).dir)
                entity_summoner.summon_fireball__actual(len(lists.name_dict)+1, (0,0), amaing-90, 300, (lists.name_dict[name]).stats.pos.xy, self.stats.name, 1, optional_name="REVENGE_fireball"+str(len(lists.name_dict)+1))
                (lists.name_dict[name]).stats.conditions.animation_invisible = True 
                self.stats.conditions.blocked += 2
                if self.stats.conditions.blocked>=16: self.stats.conditions.blocked = 16
                lists.KILL_entity(name)
            else:
                self.stats.conditions.stunned = 20; self.stats.hp -= lists.name_dict[name].stats.damage
                dir = abs(mthd.maths.atan3(lists.name_dict[name].stats.pos.x - self.stats.pos.x, lists.name_dict[name].stats.pos.y - self.stats.pos.y)-270) % 360
                self.stats.conditions.velocity_dir.xy = (mthd.maths.sin(dir), mthd.maths.cos(dir));     self.stats.conditions.velocity_time = 20
                self.stats.dir = mthd.find_dir.find_direction_knockback(dir)
            return owner

    def sword_hit(self):
        collision, name = ent.Collisions.n_specific_hitbox__type(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox*3.5, self.stats.name, 'HUM')
        if collision and (lists.name_dict[name]).stats.conditions.sword_cooldown>0:
            atan2dir= (mthd.maths.atan3(lists.name_dict[name].stats.pos.x - self.stats.pos.x, lists.name_dict[name].stats.pos.y - self.stats.pos.y)-270) % 360
            dir = (((atan2dir+45)//90*90)%360)  
            dir = mthd.maths.transform_direction(dir)
            if (dir!=(lists.name_dict[name]).stats.dir) and self.stats.conditions.sword_cooldown<0 and self.stats.conditions.invulenarbility<0:
                self.stats.conditions.stunned = 15 - ((self.stats.conditions.ULTI_healing>0)*10) - self.stats.conditions.exp_stunning_backoff
                damage = (4 - self.stats.conditions.exp_stunning_backoff)
                if damage < 1 : damage = 1
                self.stats.hp -= damage + ((lists.name_dict[name]).stats.conditions.dash_cooldown>30)*3
                self.stats.conditions.velocity_dir.xy = (-mthd.maths.sin(atan2dir), mthd.maths.cos(atan2dir));     
                self.stats.conditions.velocity_time = 15; self.stats.conditions.invulenarbility = 15
                self.stats.conditions.exp_stunning_backoff *= 2
                self.stats.dir = int((((lists.name_dict[name]).stats.dir)+180)%360)
                self.stats.dir = mthd.maths.transform_direction(self.stats.dir)
            return name
        if self.stats.conditions.exp_stunning_backoff>2: self.stats.conditions.exp_stunning_backoff -= 1
                
    def draw(self):
        """Finding the correct animation frame and drawing it on screen."""
        self.humanoid_image()
        
        if lists.slow_motion and self.stats.name == "PLAYER":
            img = (ent.visuals.load_image("img/ULTI_/teleporter"+str(setup.ticks%60)))
            ent.visuals.blit(img, (self.stats.pos.x - 48-2), (self.stats.pos.y - 50))
        if self.stats.conditions.plop_animation<30:
            a = (ent.visuals.load_image("img//ULTI_/plop" + str(int(self.stats.conditions.plop_animation))))
            ent.visuals.blit(a,(self.stats.pos.x - 48), (self.stats.pos.y - 48))
        self.stats.conditions.plop_animation += 2

        ent.visuals.blit(self.humanoid_img, (self.stats.pos.x - 48), (self.stats.pos.y - 48))

        if self.stats.conditions.ULTI_healing > 0:
            img = (ent.visuals.load_image("img/ULTI_/healing"+str(setup.ticks%90)))
            ent.visuals.blit(img, (self.stats.pos.x - 48), (self.stats.pos.y - 50))

        ent.visuals.blit(self.head, (self.stats.pos.x - 48), (self.stats.pos.y - 48))

        color_ = (25.5*abs(self.stats.hp-self.stats.max_hp), 25.5*self.stats.hp, 0)
        color = []
        for val in color_:
            if val < 0: color.append(0)
            elif val > 255: color.append(255)
            else: color.append(val)
        width = 5*self.stats.hp

        pygame.draw.rect(setup.screen,(20,24,46), pygame.Rect((self.stats.pos.x - 22-setup.camera_pos.x), (self.stats.pos.y - 38-setup.camera_pos.y), 50, 8))
        try:
            pygame.draw.rect(setup.screen, color, pygame.Rect((self.stats.pos.x - 22-setup.camera_pos.x), (self.stats.pos.y - 38-setup.camera_pos.y), width, 8))
        except ValueError:
            print(color)
        a = (ent.visuals.load_image("img/icons_/health_bar_empty"))
        ent.visuals.blit(a,(self.stats.pos.x - 24), (self.stats.pos.y - 40))
        if self.stats.name == "PLAYER":
            n = (self.stats.conditions.max_ULTI_cooldown - self.stats.conditions.ULTI_cooldown)//(self.stats.conditions.max_ULTI_cooldown/8)
            if n>8: n = 8
            a = (ent.visuals.load_image("img/icons_/ULTI_icon" + str(int(n))))
            ent.visuals.blit(a,(self.stats.pos.x - 4), (self.stats.pos.y - 54))

    def movement(self):
        """Moving the humanoid in the correct way: controlling voluntry diagonal movement, involuntry movement, respective of the delta value and checking for collisions with the level."""
        modif = (abs(self.stats.inputs.joystick.x) + abs(self.stats.inputs.joystick.y)) ** 0.5
        if modif == 0:      modif = 1
        self.move.x = self.stats.inputs.joystick.x * self.stats.move_speed * setup.delta / modif 
        self.move.y = self.stats.inputs.joystick.y * self.stats.move_speed * setup.delta / modif 
        
        if self.stats.conditions.velocity_time > 0:
            self.move.x += self.stats.conditions.velocity_dir.x * self.stats.conditions.velocity_time ** 2 / 2 * setup.delta
            if self.move.x == 0:    self.stats.conditions.velocity_dir.xy = (0, self.stats.conditions.velocity_dir.y)

            self.move.y += self.stats.conditions.velocity_dir.y * self.stats.conditions.velocity_time ** 2 / 2 * setup.delta
            if self.move.y == 0:    self.stats.conditions.velocity_dir.xy = (self.stats.conditions.velocity_dir.x, 0)
        
        if self.stats.inputs.joystick.x!=0 or self.stats.inputs.joystick.y!=0: 
            self.stats.dir = mthd.find_dir.find_direction__moved(self.stats.inputs.joystick.x, self.stats.inputs.joystick.y)
        
        hitboxX = ent.Collisions.hitbox(self.stats.pos.x + self.move.x, self.stats.pos.y, self.stats.hitbox, self.stats.name)
        hitboxY = ent.Collisions.hitbox(self.stats.pos.x, self.stats.pos.y + self.move.y, self.stats.hitbox, self.stats.name)
        self.stats.pos.x += self.move.x * int(ent.Collisions.n_colides(self.stats.pos.x + self.move.x, self.stats.pos.y, self.stats.hitbox)) * int(hitboxX)
        self.stats.pos.y += self.move.y * int(ent.Collisions.n_colides(self.stats.pos.x, self.stats.pos.y + self.move.y, self.stats.hitbox)) * int(hitboxY)

    def humanoid_image(self): #(<PATH> + 'HUMANOID' + animation + dir + '.' + frame + '.png')
        """Finding the correct humanoid animation frame: Either Idle, throw, sword or walking. It also sets the head image."""
        if self.stats.conditions.sword_cooldown > 0:
            self.humanoid_img = 'HUMANOID' + "sword" + str(abs(self.stats.dir)) + '.' + str(int(5 - self.stats.conditions.sword_cooldown))
        elif self.stats.conditions.throw_cooldown > 0:
            self.humanoid_img = 'HUMANOID' + "throw" + str(abs(self.stats.dir)) + '.' + str(int(5 - self.stats.conditions.throw_cooldown))
        elif (self.stats.inputs.joystick.x == 0 and self.stats.inputs.joystick.y == 0) or (self.move.x == 0 and self.move.y == 0):
            self.humanoid_img = 'HUMANOID' + "idle" + str(abs(self.stats.dir)) + '.' + str(0)
        elif self.stats.conditions.velocity_time > 0:
            self.humanoid_img = 'HUMANOID' + "dash" + str(abs(self.stats.dir)) + '.' + str(0)
        else:
            self.humanoid_img = 'HUMANOID' + "walk" + str(abs(self.stats.dir)) + '.' + str(self.humanoid_frame)
        self.humanoid_img = ent.visuals.load_image((self.stats.IMG_PATH_body + self.humanoid_img), self.stats.dir == -90, False, self.stats.alpha_fade)
        self.head = ent.visuals.load_image((self.stats.IMG_PATH_head + str(self.stats.nick_name) + 'head' + str(abs(self.stats.dir))), self.stats.dir == -90, False, self.stats.alpha_fade)

    def update_and_reset(self):
        "Updating and reseting essential variables."
        self.stats.conditions.ULTI_invis -= 1
        self.move = mthd.Position(0, 0)
        self.stats.conditions.throw_cooldown -= 0.2;   self.stats.conditions.sword_cooldown -= 0.4;   self.stats.conditions.stunned -= 1;     self.stats.conditions.velocity_time -= 1;     self.stats.conditions.invulenarbility -= 1
        self.humanoid_frame = int(setup.ticks / 10) % 6     ;   self.stats.conditions.blocked -= 0.025   ; self.stats.conditions.dash_cooldown -= 1
        if self.stats.conditions.blocked<=1: self.stats.conditions.blocked = 1
        self.stats.conditions.ball_dead = self.stats.name + '_fireball' not in str(lists.alive_entitys)
        self.stats.conditions.ULTI_cooldown -= 1
        self.stats.inputs.RESET()

    def trigger_ULTI(self):
        if setup.mouse_keyboard.ULTIMATE_POWER and self.stats.conditions.ULTI_cooldown<0:
            if self.stats.weapons.up=="CIRCLE": 
                self.stats.conditions.ULTI_cooldown = 500
                self.stats.conditions.max_ULTI_cooldown = 500
                entity_summoner.summon_CIRCLE(n=36, startXY=self.stats.pos, owner=self.stats.name)
            elif self.stats.weapons.up=="HEAL": 
                self.stats.conditions.ULTI_cooldown = 500
                self.stats.conditions.max_ULTI_cooldown = 500
                self.stats.conditions.ULTI_healing = 200
            elif self.stats.weapons.up=="TELE": 
                self.stats.conditions.ULTI_cooldown = 200
                self.stats.conditions.max_ULTI_cooldown = 200
                lists.slow_motion = True
            elif self.stats.weapons.up=="INVIS": 
                self.stats.conditions.ULTI_cooldown = 500
                self.stats.conditions.max_ULTI_cooldown = 500
                self.stats.conditions.ULTI_invis = 400
                self.stats.alpha_fade = 100


class FIRE_BALL:
    "The Fireball class."
    def __init__(self, stats_block, startXY, dir, name, speed_mod, owner):
        """Intialising the fireball Entity. Setting up the fireballs speed, dir, position, image and cooldown variables."""
        self.stats = json.loads(json.dumps((lists.stats["fireball"][stats_block])), object_hook=lambda item: SimpleNamespace(**item)) #Dark Magic
        self.stats.pos = startXY
        self.stats.move_speed += speed_mod
        self.stats.dir = math.radians(dir)
        self.stats.name = name
        self.stats.owner = owner
        self.death_dir = 90 * random.randint(1, 4)
        self.image = pygame.transform.rotate(pygame.image.load('img/fireball_/fireball.png'), -dir)

    def tick(self):
        """Ticking the fireball: Moving it and checking for (deadly) colisions."""
        if lists.slow_motion: return
        if self.stats.conditions.dead: 
            if self.stats.conditions.counter_till_death <= 0: lists.KILL_entity(self.stats.name)
            self.stats.hitbox = self.stats.size_mod;   self.stats.conditions.counter_till_death -= 0.5;     return
        self.stats.kill_timer -= setup.delta; self.stats.conditions.invulenarbility -= 1
        self.stats.pos.x += math.cos(self.stats.dir) * self.stats.move_speed * setup.delta
        self.stats.pos.y += math.sin(self.stats.dir) * self.stats.move_speed * setup.delta
        if (self.stats.kill_timer <= 0): self.stats.conditions.dead = True; return
        if ent.Collisions.colides(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox): self.stats.conditions.dead = True; return
        if self.stats.conditions.invulenarbility <= 0:
            if ent.Collisions.n_hitbox(self.stats.pos.x, self.stats.pos.y, self.stats.hitbox * 4, self.stats.name): self.stats.conditions.dead = True; return
    
    def draw(self):
        "Determining the correct image, position and animation of the fireball and drawing it on screen."
        if not self.stats.conditions.dead:                  setup.screen.blit(self.image,(self.stats.pos.x-setup.camera_pos.x, self.stats.pos.y-setup.camera_pos.y));     return
        elif not self.stats.conditions.animation_invisible: 
            image = ent.visuals.load_image('img/fireball_/explosion' + str(5 - int(self.stats.conditions.counter_till_death)))
            ent.visuals.blit(image, (self.stats.pos.x - self.stats.size_mod), (self.stats.pos.y - self.stats.size_mod), 1.000001, self.death_dir)


class entity_summoner:
    def summon_fireball__actual(stats_block, name="", dir=0, speed_mod=0, startXY=mthd.Position(0,0), owner="?"):
        "Actualy adding fireballs to the entitys list."
        fireball = FIRE_BALL(stats_block, startXY, dir, name, speed_mod, owner=owner)
        lists.ADD_entity(name, fireball)

    def summon_fireball(startXY, endXY, throw_mod=0, owner="???"):
        "Summon 1 Fireball, flying towards the target Coordinates and returning the throwers new direction."
        atan2_dir = (mthd.maths.atan3((endXY.y - startXY.y), (endXY.x - startXY.x)));       dir = 90-atan2_dir
        name = owner+"_fireball0"
        startXY = mthd.Position(startXY.x, startXY.y)
        entity_summoner.summon_fireball__actual("one", name, dir+throw_mod, startXY=startXY, owner=owner)
        return mthd.find_dir.find_direction__throw(atan2_dir)

    def summon_fireball_wave(startXY=mthd.Position(0,0), endXY=mthd.Position(0,0), throw_mod=0, owner="???"):
        "Summons 50 Fireballs, flying towards the target Coordinates in a wave formation and returning the throwers new direction."
        atan2_dir = (mthd.maths.atan3((endXY.y - startXY.y), (endXY.x - startXY.x)));       dir = 90-atan2_dir
        for i in range(25):
            base_pos = mthd.Position(startXY.x, startXY.y)
            dmod = dir + random.randint(-15, 15) + throw_mod
            smod = random.randint(-32, 32)
            name = owner+"_fireball"+str(i)
            entity_summoner.summon_fireball__actual("wave", name, dmod, smod, startXY=base_pos, owner=owner)
        return mthd.find_dir.find_direction__throw(atan2_dir)
    
    def summon_CIRCLE(n, startXY=mthd.Position(0,0), owner="???"):
        "Summons n Fireballs, flying in all directions in a Circle Formation." 
        for i in range(1,n+1):
            base_pos = mthd.Position(startXY.x, startXY.y)
            dmod = i*(360/n)
            smod = random.randint(-15, 15)
            name = owner+"_ULTI_fireball"+str(i)
            entity_summoner.summon_fireball__actual("CIRCLE", name, dmod, smod, startXY=base_pos, owner=owner)

    def summon_HUMANOID(stats_block, name, pos=None):
        "Summons a Humanoid entity at a random Position, if pos is not given."
        if pos==None:
            coord = (random.randint(0, setup.map_width*32), random.randint(0, setup.map_height*32))
            dist=True
            while (ent.Collisions.colides(coord[0], coord[1], 8)) or dist:
                    coord = (random.randint(0, setup.map_width*32), random.randint(0, setup.map_height*32))
                    dist = ent.Collisions.n_hitbox(coord[0], coord[1], 50, name) # dist = ent.Collisions.n_hitbox(coord[0], coord[1], 500, name)
        else:   coord=pos
        while name in lists.alive_entitys:
            name = name + str(len(lists.alive_entitys))
        Hum = HUMANOID(stats_block, name, (coord[0], coord[1]))
        lists.ADD_entity(name, Hum)