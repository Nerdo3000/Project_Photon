import pygame
import pygame_setup as setup
import math
import random
import extra_math as mthd
import entitys.entity_general_code as ent
import lists

class HUMANOID:
    "The Humanoid Entity class."
    def __init__(self, name, nick_name, start_modXY=(0, 0), speed=128, target="PLAYER", weapons=()):
        """Initialisation of the Humanoid charakter. Setting up the Humanoids: speed, position, direction, Animitaion frame, Image and cooldown variables."""
        self.vars = ent.basic_entity_variables(start_modXY, move_speed = speed, hitbox = 8, name = name, nick=nick_name, target_Ent=target, weapon=weapons)
        self.type = "HUM"
    
    def tick(self):
        """Ticks the humanoid: Moving the humanoid, fireball throwing and updating variables like the animation frame and cooldown variables."""
        if not self.vars.conditions.dead:
            self.update_and_reset()

            if (self.vars.conditions.stunned <= 0) and(self.vars.conditions.throw_cooldown+2) <= 0 and (self.vars.conditions.sword_cooldown+4)<=0:
                if self.vars.name == 'PLAYER':      self.PLAYER_controller()
                if 'GUY' in self.vars.name:         self.AI_controller()

            if setup.mouse_keyboard.ULTIMATE_POWER and self.vars.conditions.ULTI_cooldown<0:
                self.vars.conditions.ULTI_cooldown = 500
                if self.vars.weapons.up=="CIRCLE": 
                    entity_summoner.summon_CIRCLE(n=36, startXY=self.vars.pos.xy, owner=self.vars.name)
                if self.vars.weapons.up=="HEAL": 
                    self.vars.conditions.ULTI_healing = 200

            if self.vars.conditions.ball_dead and self.vars.inputs.try_throw_fireball:
                if self.vars.weapons.fireball=="one":   self.vars.dir = entity_summoner.summon_fireball(self.vars.pos.xy, self.vars.inputs.fireball_target.xy, self.vars.inputs.throw_mod, owner=self.vars.name)
                if self.vars.weapons.fireball=="wave":  self.vars.dir = entity_summoner.summon_fireball_wave(pos_mod=5,dir_mod=10, speed_mod=32, time_mod=0.2, startXY=self.vars.pos.xy, endXY=self.vars.inputs.fireball_target.xy, throw_mod=self.vars.inputs.throw_mod, owner=self.vars.name)
                self.vars.conditions.throw_cooldown = 5
            elif (self.vars.conditions.sword_cooldown+4)<=0 and self.vars.inputs.try_sword:
                self.vars.conditions.sword_cooldown = 5

            self.movement()

            self.hit()
            
        else:
            self.vars.alpha_fade -= 20
            if self.vars.alpha_fade <=0: lists.KILL_entity(self.vars.name)

    def PLAYER_controller(self):
        "Getting the Controls of the Player Charakter/User."
        self.vars.inputs.throw_mod = random.randint(-10, 10) * lists.hardness
        self.vars.inputs.joystick.xy = setup.mouse_keyboard.joystick.xy
        if self.vars.weapons.fireball != False: self.vars.inputs.try_throw_fireball = setup.mouse_keyboard.right_click
        self.vars.inputs.fireball_target = setup.mouse_keyboard.mouse_custom_pos
        self.vars.inputs.try_sword = setup.mouse_keyboard.spacebar
        self.vars.inputs.try_dash = setup.mouse_keyboard.shift
        self.vars.inputs.ULTI = setup.mouse_keyboard.ULTIMATE_POWER
        if self.vars.inputs.try_dash:
            self.vars.conditions.dash_cooldown += 1
            if self.vars.conditions.dash_cooldown<0 and self.vars.inputs.joystick.xy != (0,0):
                self.vars.conditions.velocity_time = 23
                self.vars.conditions.dash_cooldown = 40
                self.vars.conditions.velocity_dir.xy = self.vars.inputs.joystick.xy
    
    def AI_controller(self):
        "Getting the Controls of the AI charakter, this includes walking, fireball throwing and fireball deflecting (sword)."
        if not "!G!" == self.vars.target_ent[0]:
            dists = {}
            for i in self.vars.target_ent:
                try:
                    dists[math.dist(self.vars.pos.xy, (lists.name_dict[i]).vars.pos.xy)+100000*(lists.name_dict[i]).vars.conditions.dead] = i
                except:
                    pass
            if len(dists)>0:
                self.target_name = dists[(sorted((list(dists))))[0]]
                self.vars.inputs.fireball_target = (lists.name_dict[self.target_name]).vars.pos
            else: return
        else:
            dists = {}
            for enemy in self.vars.target_ent[1:]:
                for name in lists.alive_entitys:
                    if (enemy in name) and not ("fireball" in name):
                        dists[math.dist(self.vars.pos.xy, (lists.name_dict[name]).vars.pos.xy)+100000*(lists.name_dict[name]).vars.conditions.dead] = name
            if len(dists)>0:
                self.target_name = dists[(sorted((list(dists))))[0]]
                self.vars.inputs.fireball_target = (lists.name_dict[self.target_name]).vars.pos
            else: return
            
        if self.vars.weapons.sword:
            dont_try_fireball = self.AI__sword_controller()
            if dont_try_fireball=="r":return
        else:
            dont_try_fireball = False
        
        direct, dir = self.AI__fireball_and_direct_path_controller((self.vars.weapons.fireball!=False), dont_try_fireball)

        if not direct: dir = self.AI__pathgrid_controller()

        self.vars.inputs.joystick.xy = mthd.maths.sin(dir), mthd.maths.cos(dir)   
          
    def AI__sword_controller(self):
        collision, name = ent.Collisions.n_specific_hitbox__type(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox+256, self.vars.name, 'fireball')
        collision2, name2 = ent.Collisions.n_specific_hitbox__type(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox*3.5, self.vars.name, 'HUM')
        if collision: #FIREBALL DEFENSE
            collision, name = ent.Collisions.n_specific_hitbox__type(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox+6, self.vars.name, 'fireball')
            if collision and random.randint(1,3)!=1:
                self.vars.dir = int((math.degrees((lists.name_dict[name]).vars.dir)-45)//90*90%360)
                if self.vars.dir == 270: self.vars.dir=-90
                self.vars.inputs.try_sword = True
                return "r"
            return True
        if collision2 and random.randint(1,10)==1 and (name2 in self.target_name):  #MEELE
            atan2dir= (mthd.maths.atan3(lists.name_dict[name2].vars.pos.x - self.vars.pos.x, lists.name_dict[name2].vars.pos.y - self.vars.pos.y)-270) % 360
            dir = (((atan2dir+45)//90*90)%360)
            if dir == 270: dir=-90
            self.vars.dir = int(dir)
            self.vars.inputs.try_sword = True
            return "r"
        return False
    def AI__pathgrid_controller(self):
        try:
            targetpos = (lists.path_dict[self.target_name], int(self.vars.pos.y//32), int(self.vars.pos.x//32))
        except KeyError:
            print(setup.ticks, self.target_name)
            return 0
        targetval = lists.current_map[targetpos]
        if targetval == '###' or targetval == 'QQQ':     return mthd.maths.atan4(self.vars.inputs.fireball_target.x - self.vars.pos.x, self.vars.inputs.fireball_target.y - self.vars.pos.y) 
        else:
            try:        dir = (int(targetval) +180) % 360
            except:     print(targetval); print((0/0))
            target = mthd.Position(targetpos[2] * 32 + 32 * int(mthd.maths.sin(dir)) + 16,   targetpos[1] * 32 + 32 * int(mthd.maths.cos(dir)) + 16)
            return (mthd.maths.atan3(target.x - self.vars.pos.x, self.vars.pos.y - target.y)-270)%360
    def AI__fireball_and_direct_path_controller(self, fireball, dont_try_fireball):
        currentPos = mthd.Position(self.vars.pos.x, self.vars.pos.y)
        dir = mthd.maths.atan4(self.vars.inputs.fireball_target.x - currentPos.x, self.vars.inputs.fireball_target.y - currentPos.y)
        while True:
            dist = math.dist(currentPos.xy, self.vars.inputs.fireball_target.xy)
            if dist < 8:
                dist = math.dist(self.vars.inputs.fireball_target.xy, self.vars.pos.xy)
                if dist <= 256 and (self.vars.name + '_fireball' not in str(lists.alive_entitys)) and not dont_try_fireball:         #40 * setup.delta * 300:
                    self.vars.inputs.try_throw_fireball = fireball
                    self.vars.inputs.throw_mod = random.randint(-lists.entity_presision, lists.entity_presision)
                return True, dir 
            currentPos.add(mthd.maths.sin(dir) * 6, mthd.maths.cos(dir) * 6)
            if ent.Collisions.colides(currentPos.x, currentPos.y, 8): return False, dir

    def hit(self):
        attacker = self.ball_hit()
        attacker2 = self.sword_hit()
        if self.vars.hp<=0:
            self.vars.conditions.dead = True
            if attacker ==  None:
                (lists.name_dict[attacker2]).vars.conditions.vamp_healing = 30
            if attacker2 == None:
                (lists.name_dict[attacker]).vars.conditions.vamp_healing = 30
        else:
            if self.vars.conditions.vamp_healing > 0:
                self.vars.hp += 0.1
                if self.vars.hp > self.vars.max_hp: self.vars.hp = self.vars.max_hp
                self.vars.conditions.vamp_healing -= 1
            if self.vars.conditions.ULTI_healing > 0:
                self.vars.hp += 0.5
                if self.vars.hp > self.vars.max_hp: self.vars.hp = self.vars.max_hp
                self.vars.conditions.ULTI_healing -= 1

    def ball_hit(self):
        "Code for detcting if a Humanoid is hit by a fireball and checking if they deflect it sucessfully."
        collision, name = ent.Collisions.n_specific_hitbox__type(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox, self.vars.name, 'fireball')
        if collision and self.vars.conditions.invulenarbility < 0: 
            otherdir = (math.degrees((lists.name_dict[name]).vars.dir)+135)//90*90       
            owndir = (self.vars.dir+360)%360
            self.vars.conditions.invulenarbility = 20
            owner = (lists.name_dict[name]).vars.owner
            if self.vars.conditions.ULTI_healing > 0 or (self.vars.conditions.sword_cooldown>0 and (otherdir != owndir) and not(self.vars.conditions.blocked>14) and (random.randint(1,5)!=1) and not (lists.name_dict[name]).unblock): 
                amaing = ((mthd.maths.atan3((self.vars.inputs.fireball_target.x - self.vars.pos.x), (self.vars.inputs.fireball_target.y - self.vars.pos.y)))+90) + random.randint(-25, 25)  #math.degrees((setup.name_dict[name]).dir)
                entity_summoner.summon_fireball__actual(len(lists.name_dict)+1, (0,0), amaing-90, 300, (lists.name_dict[name]).vars.pos.xy, self.vars.name, 1, optional_name="REVENGE_fireball"+str(len(lists.name_dict)+1))
                (lists.name_dict[name]).vars.conditions.animation_invisible = True 
                self.vars.conditions.blocked += 2
                if self.vars.conditions.blocked>=16: self.vars.conditions.blocked = 16
                lists.KILL_entity(name)
            else:
                self.vars.conditions.stunned = 20; self.vars.hp -= lists.name_dict[name].damage
                dir = abs(mthd.maths.atan3(lists.name_dict[name].vars.pos.x - self.vars.pos.x, lists.name_dict[name].vars.pos.y - self.vars.pos.y)-270) % 360
                self.vars.conditions.velocity_dir.xy = (mthd.maths.sin(dir), mthd.maths.cos(dir));     self.vars.conditions.velocity_time = 20
                self.vars.dir = mthd.find_dir.find_direction_knockback(dir)
            return owner

    def sword_hit(self):
        if self.vars.conditions.exp_stunning_backoff>2: self.vars.conditions.exp_stunning_backoff -= 1
        collision, name = ent.Collisions.n_specific_hitbox__type(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox*3.5, self.vars.name, 'HUM')
        if collision and (lists.name_dict[name]).vars.conditions.sword_cooldown>0:
            atan2dir= (mthd.maths.atan3(lists.name_dict[name].vars.pos.x - self.vars.pos.x, lists.name_dict[name].vars.pos.y - self.vars.pos.y)-270) % 360
            dir = (((atan2dir+45)//90*90)%360)  
            if dir == 270: dir=-90
            if (dir!=(lists.name_dict[name]).vars.dir) and self.vars.conditions.sword_cooldown<0 and self.vars.conditions.invulenarbility<0:
                self.vars.conditions.stunned = 15 - ((self.vars.conditions.ULTI_healing>0)*10) - self.vars.conditions.exp_stunning_backoff
                damage = (4 - self.vars.conditions.exp_stunning_backoff)
                if damage < 1 : damage = 1
                print(damage)
                self.vars.hp -= damage + ((lists.name_dict[name]).vars.conditions.dash_cooldown>30)*3
                self.vars.conditions.velocity_dir.xy = (-mthd.maths.sin(atan2dir), mthd.maths.cos(atan2dir));     
                self.vars.conditions.velocity_time = 15; self.vars.conditions.invulenarbility = 15
                self.vars.conditions.exp_stunning_backoff *= 2
                self.vars.dir = int((((lists.name_dict[name]).vars.dir)+180)%360)
                if self.vars.dir== 270: self.vars.dir=-90
            return name
                
    def draw(self):
        """Finding the correct animation frame and drawing it on screen."""
        self.humanoid_image()

        ent.visuals.blit(self.humanoid_img, (self.vars.pos.x - 48), (self.vars.pos.y - 48))

        if self.vars.conditions.ULTI_healing > 0:
            img = (ent.visuals.load_image("img/ULTI_/healing"+str(setup.ticks%90)))
            ent.visuals.blit(img, (self.vars.pos.x - 48), (self.vars.pos.y - 50))

        ent.visuals.blit(self.head, (self.vars.pos.x - 48), (self.vars.pos.y - 48))

        color_ = (25.5*abs(self.vars.hp-self.vars.max_hp), 25.5*self.vars.hp, 0)
        color = []
        for val in color_:
            if val < 0: color.append(0)
            elif val > 255: color.append(255)
            else: color.append(val)
        width = 5*self.vars.hp

        pygame.draw.rect(setup.screen,(20,24,46), pygame.Rect((self.vars.pos.x - 22), (self.vars.pos.y - 38), 50, 8))
        try:
            pygame.draw.rect(setup.screen, color, pygame.Rect((self.vars.pos.x - 22), (self.vars.pos.y - 38), width, 8))
        except ValueError:
            print(color)
        a = (ent.visuals.load_image("img/icons_/health_bar_empty"))
        ent.visuals.blit(a,(self.vars.pos.x - 24), (self.vars.pos.y - 40))
        if self.vars.name == "PLAYER":
            n = (500 - self.vars.conditions.ULTI_cooldown)//62.5
            if n>8: n = 8
            a = (ent.visuals.load_image("img/icons_/ULTI_icon" + str(int(n))))
            ent.visuals.blit(a,(self.vars.pos.x - 4), (self.vars.pos.y - 54))
            #ent.visuals.blit(a,(self.vars.pos.x + 32), (self.vars.pos.y - 40))


    def movement(self):
        """Moving the humanoid in the correct way: controlling voluntry diagonal movement, involuntry movement, respective of the delta value and checking for collisions with the level."""
        modif = (abs(self.vars.inputs.joystick.x) + abs(self.vars.inputs.joystick.y)) ** 0.5
        if modif == 0:      modif = 1
        self.move.x = self.vars.inputs.joystick.x * self.vars.move_speed * setup.delta / modif 
        self.move.y = self.vars.inputs.joystick.y * self.vars.move_speed * setup.delta / modif 
        
        if self.vars.conditions.velocity_time > 0:
            self.move.x += self.vars.conditions.velocity_dir.x * self.vars.conditions.velocity_time ** 2 / 2 * setup.delta
            if self.move.x == 0:    self.vars.conditions.velocity_dir.xy = (0, self.vars.conditions.velocity_dir.y)

            self.move.y += self.vars.conditions.velocity_dir.y * self.vars.conditions.velocity_time ** 2 / 2 * setup.delta
            if self.move.y == 0:    self.vars.conditions.velocity_dir.xy = (self.vars.conditions.velocity_dir.x, 0)
        
        if self.vars.inputs.joystick.x!=0 or self.vars.inputs.joystick.y!=0: 
            self.vars.dir = mthd.find_dir.find_direction__moved(self.vars.inputs.joystick.x, self.vars.inputs.joystick.y)
        
        hitboxX = ent.Collisions.hitbox(self.vars.pos.x + self.move.x, self.vars.pos.y, self.vars.hitbox, self.vars.name)
        hitboxY = ent.Collisions.hitbox(self.vars.pos.x, self.vars.pos.y + self.move.y, self.vars.hitbox, self.vars.name)
        self.vars.pos.x += self.move.x * int(ent.Collisions.n_colides(self.vars.pos.x + self.move.x, self.vars.pos.y, self.vars.hitbox)) * int(hitboxX)
        self.vars.pos.y += self.move.y * int(ent.Collisions.n_colides(self.vars.pos.x, self.vars.pos.y + self.move.y, self.vars.hitbox)) * int(hitboxY)

    def humanoid_image(self): #(<PATH> + 'HUMANOID' + animation + dir + '.' + frame + '.png')
        """Finding the correct humanoid animation frame: Either Idle, throw, sword or walking. It also sets the head image."""
        if self.vars.conditions.sword_cooldown > 0:
            self.humanoid_img = 'HUMANOID' + "sword" + str(abs(self.vars.dir)) + '.' + str(int(5 - self.vars.conditions.sword_cooldown))
        elif self.vars.conditions.throw_cooldown > 0:
            self.humanoid_img = 'HUMANOID' + "throw" + str(abs(self.vars.dir)) + '.' + str(int(5 - self.vars.conditions.throw_cooldown))
        elif (self.vars.inputs.joystick.x == 0 and self.vars.inputs.joystick.y == 0) or (self.move.x == 0 and self.move.y == 0):
            self.humanoid_img = 'HUMANOID' + "idle" + str(abs(self.vars.dir)) + '.' + str(0)
        elif self.vars.conditions.velocity_time > 0:
            self.humanoid_img = 'HUMANOID' + "dash" + str(abs(self.vars.dir)) + '.' + str(0)
        else:
            self.humanoid_img = 'HUMANOID' + "walk" + str(abs(self.vars.dir)) + '.' + str(self.humanoid_frame)
        self.humanoid_img = ent.visuals.load_image((self.vars.IMG_PATH_body + self.humanoid_img), self.vars.dir == -90, False, self.vars.alpha_fade)
        self.head = ent.visuals.load_image((self.vars.IMG_PATH_head + str(self.vars.nick_name) + 'head' + str(abs(self.vars.dir))), self.vars.dir == -90, False, self.vars.alpha_fade)

    def update_and_reset(self):
        "Updating and reseting essential variables."
        self.move = mthd.Position(0, 0)
        self.vars.conditions.throw_cooldown -= 0.2;   self.vars.conditions.sword_cooldown -= 0.4;   self.vars.conditions.stunned -= 1;     self.vars.conditions.velocity_time -= 1;     self.vars.conditions.invulenarbility -= 1
        self.humanoid_frame = int(setup.ticks / 10) % 6     ;   self.vars.conditions.blocked -= 0.025   ; self.vars.conditions.dash_cooldown -= 1
        if self.vars.conditions.blocked<=1: self.vars.conditions.blocked = 1
        self.vars.conditions.ball_dead = self.vars.name + '_fireball' not in str(lists.alive_entitys)
        self.vars.conditions.ULTI_cooldown -= 1
        self.vars.inputs.RESET()

class FIRE_BALL:
    "The Fireball class."
    def __init__(self, start_x, start_y, dir, name, speed_mod, killtimer, invulnerability, owner, damage_mult, unblock):
        """Intialising the fireball Entity. Setting up the fireballs speed, dir, position, image and cooldown variables."""
        self.vars = ent.basic_entity_variables((start_x, start_y), speed_mod, math.radians(dir), 3, name, owner=owner)
        self.type = "fireball"
        self.death_dir = 90 * random.randint(1, 4)
        self.vars.conditions.invulenarbility = invulnerability
        self.vars.conditions.counter_till_death = 5
        self.image = pygame.transform.rotate(pygame.image.load('img/fireball_/fireball.png'), -dir)
        self.kill_timer = killtimer
        self.size_mod = 0.3125*256/2
        self.damage = damage_mult
        self.unblock = unblock

    def tick(self):
        """Ticking the fireball: Moving it and checking for (deadly) colisions."""
        if self.vars.conditions.dead: 
            if self.vars.conditions.counter_till_death <= 0: lists.KILL_entity(self.vars.name)
            self.vars.hitbox = self.size_mod;   self.vars.conditions.counter_till_death -= 0.5;     return
        self.kill_timer -= setup.delta; self.vars.conditions.invulenarbility -= 1
        self.vars.pos.x += math.cos(self.vars.dir) * self.vars.move_speed * setup.delta
        self.vars.pos.y += math.sin(self.vars.dir) * self.vars.move_speed * setup.delta
        if (ent.Collisions.colides(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox)) or (self.kill_timer <= 0): self.vars.conditions.dead = True
        if self.vars.conditions.invulenarbility <= 0:
            if ent.Collisions.n_hitbox(self.vars.pos.x, self.vars.pos.y, self.vars.hitbox * 4, self.vars.name): self.vars.conditions.dead = True
    
    def draw(self):
        "Determining the correct image, position and animation of the fireball and drawing it on screen."
        if not self.vars.conditions.dead:                  setup.screen.blit(self.image, self.vars.pos.xy);     return
        elif not self.vars.conditions.animation_invisible: 
            image = ent.visuals.load_image('img/fireball_/explosion' + str(5 - int(self.vars.conditions.counter_till_death)))
            ent.visuals.blit(image, (self.vars.pos.x - self.size_mod), (self.vars.pos.y - self.size_mod), 0.3125, self.death_dir)

class entity_summoner:
    def summon_fireball__actual(n=0, posmod=(0,0), dir=0, speed=300, startXY=(0,0), owner="?", kill_timer=math.inf, optional_name="", damage_mult=1, unblock=False):
        "Actualy adding fireballs to the entitys list."
        if optional_name != "": name = optional_name
        else:   name = owner+"_fireball"+str(n)
        fireball = FIRE_BALL(startXY[0]+posmod[0], startXY[1]+posmod[1], dir, name=name, speed_mod = speed, killtimer=kill_timer, invulnerability=5, owner=owner, damage_mult=damage_mult, unblock=unblock)
        lists.ADD_entity(name, fireball)

    def summon_fireball(startXY, endXY, throw_mod=0, owner="???"):
        "Summon 1 Fireball, flying towards the target Coordinates and returning the throwers new direction."
        atan2_dir = (mthd.maths.atan3((endXY[1] - startXY[1]), (endXY[0] - startXY[0])));       dir = 90-atan2_dir
        entity_summoner.summon_fireball__actual(0, dir=dir+throw_mod, startXY=startXY, owner=owner, kill_timer=1)
        return mthd.find_dir.find_direction__throw(atan2_dir)

    def summon_fireball_wave(pos_mod=0, dir_mod=0, speed_mod=0, time_mod=0, startXY=0, endXY=0, throw_mod=0, owner="???"):
        "Summons 50 Fireballs, flying towards the target Coordinates in a wave formation and returning the throwers new direction."
        for i in range(50):
            posmod = (random.randint(-pos_mod, pos_mod), random.randint(-pos_mod, pos_mod))
            dmod = random.randint(-dir_mod, dir_mod)
            smod = 300 + random.randint(-speed_mod, speed_mod)
            tmod = 0.3+(time_mod * random.random())
            atan2_dir = (mthd.maths.atan3((endXY[1] - startXY[1]), (endXY[0] - startXY[0])));       dir = 90-atan2_dir
            entity_summoner.summon_fireball__actual(i, posmod, dir+dmod+throw_mod, smod, startXY, owner, kill_timer=tmod, damage_mult=3, unblock=True)
        return mthd.find_dir.find_direction__throw(atan2_dir)

    def summon_HUMANOID(name, nick, pos=None, spd=128, target_Ent=None, weapons=()):
        "Summons a Humanoid entity at a random Position, if pos is not given."
        if pos==None:
            coord = (random.randint(0, 1280), random.randint(0, 736))
            dist=True
            while (ent.Collisions.colides(coord[0], coord[1], 8)) or dist:
                    coord = (random.randint(0, 1280), random.randint(0, 736))
                    dist = ent.Collisions.n_hitbox(coord[0], coord[1], 50, name) # dist = ent.Collisions.n_hitbox(coord[0], coord[1], 500, name)
        else:   coord=pos
        while name in lists.alive_entitys:
            name = name + str(len(lists.alive_entitys))
        Hum = HUMANOID(name, nick, (coord[0], coord[1]), speed=spd, target=target_Ent, weapons=weapons)
        lists.ADD_entity(name, Hum)
    
    def summon_CIRCLE(n, startXY=0, owner="???"):
        "Summons n Fireballs, flying in all directions in a Circle Formation and setting the throwers direction." 
        for i in range(1,n+1):
            dmod = i*(360/n)
            smod = 300 + random.randint(-15, 15)
            tmod = 0.1 + (random.random()/10)
            name = owner+"_ULTI_fireball"+str(i)
            entity_summoner.summon_fireball__actual(i, dir=dmod, speed=smod, startXY=startXY, optional_name=name, owner=owner, kill_timer=tmod, damage_mult=9, unblock=True)
