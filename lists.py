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
slow_motion = False
respawn_counter = {}
pathfinding_requests = []
to_spawn_ent = []
centered_square_num = [1, 5, 13, 25, 41, 61, 85, 113, 145, 181, 221, 265, 
                       313, 365, 421, 481, 545, 613, 685, 761, 841, 925, 
                       1013, 1105, 1201, 1301, 1405, 1513, 1625, 1741, 1861, 
                       1985, 2113, 2245, 2381, 2521, 2665, 2813, 2965, 3121, 
                       3281, 3445, 3613, 3785, 3961, 4141, 4325, 4513, 4705, 
                       4901, 5101, 5305, 5513, 5725, 5941, 6161, 6385, 6613, 
                       6845, 7081, 7321, 7565, 7813, 8065, 8321, 8581, 8845, 
                       9113, 9385, 9661, 9941, 10225, 10513, 10805, 11101, 
                       11401, 11705, 12013, 12325, 12641, 12961, 13285, 
                       13613, 13945, 14281, 14621, 14965, 15313, 15665, 
                       16021, 16381, 16745, 17113, 17485, 17861, 18241, 
                       18625, 19013, 19405, 19801] #OESIS:  A001844 
highest = math.inf

class stats:
    def __init__(self):
        """Basic Values          :   (NAME,      Nickname,   Enemies,                        Speed, respawns,    Weapons: fireball,  sword,  ULTI)"""
        self.stats_dict = {
            "player_basic_lim"   :   ("PLAYER",  "P",        [],                             128,   1,                   ("one",     True,   False)),
            "player_basic_unlim" :   ("PLAYER",  "P",        [],                             128,   math.inf,            ("one",     True,   False)),
            "player_OP_lim"      :   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "CIRCLE")),
            "player_OP_unlim"    :   ("PLAYER",  "P",        [],                             128,   math.inf,            ("wave",    True,   "CIRCLE")),
            "player_HEAL_lim"    :   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "HEAL")),
            "player_HEAL_unlim"  :   ("PLAYER",  "P",        [],                             128,   math.inf,            ("wave",    True,   "HEAL")),
            "player_TELE_lim"    :   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "TELE")),
            "player_TELE_unlim"  :   ("PLAYER",  "P",        [],                             128,   math.inf,            ("wave",    True,   "TELE")),
            "player_INVI_lim"    :   ("PLAYER",  "P",        [],                             128,   1,                   ("wave",    True,   "INVIS")),
            "player_INVI_unlim"  :   ("PLAYER",  "P",        [],                             128,   math.inf,            ("wave",    True,   "INVIS")),
            "REDGUY_OP_lim"      :   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   1,                   ("wave",    True,   False)),
            "REDGUY_basic_lim"   :   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   1,                   ("one",     True,   False)),
            "REDGUY_basic_unlim" :   ("REDGUY",  "RED",      ["!G!", "VIOGUY"],              128,   math.inf,            ("one",     True,   False)),
            "REDGUY_TEST"        :   ("REDGUY",  "RED",      [],                             0,     1,                   ("one",     True,   False)),
            "VIOGUY_OP_lim"      :   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   ("wave",    True,   False)),
            "VIOGUY_basic_lim"   :   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   ("one",     True,   False)),
            "VIOGUY_basic_unlim" :   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   math.inf,            ("one",     True,   False)),
            "VIOGUY_sword_lim"   :   ("VIOGUY",  "VIO",      ["!G!", "REDGUY", "PLAYER"],    128,   1,                   (False,     True,   False))}
    def create_variation(self, base, new_value, index):
        new_variation = list(base)
        new_variation[index] = new_value
        return tuple(new_variation)
    var = create_variation
