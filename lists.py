import math
path_grid = []
name_dict = {}
path_dict = {}
alive_entitys = []
def ADD_entity(name, object):
    alive_entitys.append(name)
    name_dict[name] = object
def KILL_entity(name):
    alive_entitys.remove(name)
current_map = []
hardness = 0
entity_presision = 5 - 5 * hardness
respawn_counter = {}

to_spawn_ent = []

class stats:
    def __init__(self):
        """Basic Values         =   (NAME,      Nickname,   Enemies,                        Speed, respawns,    Weapons: fireball,  sword,  ULTI)"""
        self.player_basic_lim   =   ("PLAYER",  "P",        [],                             128,   1,                   ("one",     True,   False))
        self.player_basic_unlim =   ("PLAYER",  "P",        [],                             128,   math.inf,            ("one",     True,   False))
        self.player_OP_lim      =   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "CIRCLE"))
        self.player_OP_unlim    =   ("PLAYER",  "P",        [],                             128,   math.inf,            ("wave",    True,   "CIRCLE"))
        self.player_HEAL_lim    =   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "HEAL"))
        self.REDGUY_OP_lim      =   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   1,                   ("wave",    True,   False))
        self.REDGUY_basic_lim   =   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   1,                   ("one",     True,   False))
        self.REDGUY_basic_unlim =   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   math.inf,            ("one",     True,   False))
        self.REDGUY_TEST        =   ("REDGUY",  "RED",      [],                             0,     1,                   ("one",     True,   False))
        self.VIOGUY_OP_lim      =   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   ("wave",    True,   False))
        self.VIOGUY_basic_lim   =   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   ("one",     True,   False))
        self.VIOGUY_basic_unlim =   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   math.inf,            ("one",     True,   False))
        self.VIOGUY_sword_lim   =   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   (False,     True,   False))
    def create_variation(self, base, new_value, index):
        new_variation = list(base)
        new_variation[index] = new_value
        return tuple(new_variation)
    var = create_variation