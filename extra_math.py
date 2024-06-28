import math

class maths:
    def sin(angle):
        return(math.sin(math.radians(angle)))

    def cos(angle):
        return(math.cos(math.radians(angle)))

    def atan3(x, y):
        return (math.degrees(math.atan2(y, x)))

    def atan4(x, y):
        return (abs(math.degrees(math.atan2(y, x)) - 270) % 360 - 180) % 360
    
    def transform_direction(angle):
        if angle > 180: return (180-(angle-180))*-1
        else:   return angle

class Position:
    def __init__(self, startX=0, startY=0):
        self._x = startX
        self._y = startY
        self._xy = (self.x, self.y)

    @property 
    def xy(self): return self._xy
    @xy.setter
    def xy(self, value):
        self._xy = value
        self._x = value[0]
        self._y = value[1]
    
    @property 
    def x(self): return self._x
    @x.setter
    def x(self, value):
        self._x = value
        self.xy = (value, self._y)

    @property
    def y(self): return self._y
    @y.setter
    def y(self, value):
        self._y = value
        self.xy = (self._x, value)

    def add(self, val1, val2):
        self.x += val1 
        self.y += val2

class find_dir:
    def find_direction__moved(Xstick, Ystick):
        '''Finding the direction the entity is facing, for animation, while walking.'''
        if abs(Ystick)>abs(Xstick):
            if Ystick> 0:  return 180 
            return 0    
        else: return int(math.copysign(90, Xstick))
    dir_move = find_direction__moved

    def find_direction__throw(atan2_dir):
        '''Finding the direction the entity is facing for animation, while throwing a Fireball.'''
        dir = ((((atan2_dir+45)//90)*90)%360)
        if dir==270: dir=-90
        elif dir==180: dir=0
        elif dir==0: dir=180
        return int(dir)
    dir_throw = find_direction__throw

    def find_direction_knockback(dir):
        dir = ((((dir+45)//90)*90)%360)#(round(dir/90)*90)%360
        if dir == 90: dir = -90
        elif dir == 270: dir = 90
        return int(dir)