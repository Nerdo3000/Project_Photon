import json

player_stats    = None
player_amount   = None
REDGUY_stats    = None
REDGUY_amount   = None
VIOGUY_stats    = None
VIOGUY_amount   = None
new_random_map  = None

with open("log_set/settings.json", "r") as file:
    settings = json.load(file)

try:    player_stats    = settings["player"]["stats"]
except KeyError: player_stats    = "player_basic_lim";           print("No Setting for player_stats given! Setting set to Default!")
try:    player_amount   = settings["player"]["amount"]
except KeyError: player_amount   = 1;                            print("No Setting for player_amount given! Setting set to Default!")
try:    REDGUY_stats    = settings["REDGUY"]["stats"]
except KeyError: REDGUY_stats    = "REDGUY_basic_lim";           print("No Setting for REDGUY_stats given! Setting set to Default!")
try:    REDGUY_amount   = settings["REDGUY"]["amount"]
except KeyError: REDGUY_amount   = 1;                            print("No Setting for REDGUY_amount given! Setting set to Default!")
try:    VIOGUY_stats    = settings["VIOGUY"]["stats"]
except KeyError: VIOGUY_stats    = "VIOGUY_sword_lim";           print("No Setting for VIOGUY_stats given! Setting set to Default!")
try:    VIOGUY_amount   = settings["VIOGUY"]["amount"]
except KeyError: VIOGUY_amount   = 50;                           print("No Setting for VIOGUY_amount given! Setting set to Default!")
try:    new_random_map  = settings["new_random_map"]
except KeyError: new_random_map  = True;                         print("No Setting for new_random_map given! Setting set to Default!")