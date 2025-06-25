import random
import os.path
import random
import sys
import csv
import itertools
import specific_moves
import moves
import json

if os.path.isfile("fighters.json"):
    with open("fighters.json", "r", encoding="UTF-8") as fighter_file:
        fighter_data = json.load(fighter_file)
        for fighter in fighter_data["fighters"]:

            fighter_temp = {}
            for key, value in fighter.items():
                fighter_temp[key] = value

abilities_dict = {}
if os.path.isfile("abilities.json"):
    with open("abilities.json", "r", encoding="UTF-8") as ability_file:
        ability_data = json.load(ability_file)
        for ability in ability_data["abilities"]:
            ability_temp = {}
            for key, value in ability.items():
                ability_temp[key] = value
            abilities_dict[ability_temp["name"]] = ability_temp


def check_print_hp(fighterA, fighterB):
    # Copy of the function to avoid cyclical import
    print(fighterA["name"] + " HP: " + str(fighterA["curr_hp"]))
    print(fighterB["name"] + " HP: " + str(fighterB["curr_hp"]))

def check_soup_burst(user, target):
    if user["ability"].lower() == "soup burst" and user["curr_hp"] <= (user["hp"]/2) and user["state_ability_activated"] is False:
        user["state_ability_activated"] = True
        print(user["name"] + " bursted soup!")
        specific_moves.change_stats(user, ["phy_att","phy_def","spec_att","spec_def","speed"], [-3,-3,-3,-3,-3])

        if specific_moves.moves_dict[target["queued_move"]]["attr_makes_contact"] is True:
            moves.calculate_interaction("scald", user, target)
            check_print_hp(user, target)
        else:
            print(target["name"] + " avoided the soup!")
        if user["curr_hp"] <= 0 and target["curr_hp"] <= 0:
            user["sd_counter_win"] = True


def check_technician(user, move):
    if specific_moves.moves_dict[move]["power"] <= 60:
        print(user["name"] + "'s " + move.title() + " is boosted by Technician!")
        return 1.5
    return 1

def check_punk_rock(user, move):
    '''
    For offense part of Punk Rock
    '''
    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
        print("Damage boosted by " + user["name"] + "'s Punk Rock!")
        return 1.3
    return 1

def alt_check_punk_rock(target, move):
    '''
    For defense part of Punk Rock 
    '''
    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
        print("Damage lowered by " + target["name"] + "'s Punk Rock!")
        return 0.5
    return 1


#def check_punk_rock(user, target, move):
#    val_user = 1
#    val_target = 1
#    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
#        if user["ability"].lower() == "punk rock":
#            val_user = 1.30
#            print("Damage boosted by Punk Rock!")
#        if target["ability"].lower() == "punk rock":
#            val_target = 0.5
#            print("Damage lowered by Punk Rock!")
#    return val_user, val_target
