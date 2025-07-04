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


 # ability_category_set: List of Sets
 # 0: Unused
 # 1: Multiplier for move power
 # 2: Multiplier for STAB
 # 3: Multiplier for damage reduction OR it's a counter ability
 # 4: Other (To Be Determined)
 # 5: Other (To Be Determined)
ability_category_set = [set() for _ in range(6)]
abilities_dict = {}
if os.path.isfile("abilities.json"):
    with open("abilities.json", "r", encoding="UTF-8") as ability_file:
        ability_data = json.load(ability_file)
        for ability in ability_data["abilities"]:
            ability_temp = {}
            for key, value in ability.items():
                ability_temp[key] = value
                if key == "category":
                    try:
                        ability_category_set[value].add(ability_temp["name"])
                    except KeyError:
                        ability_category_set[value].add(ability_temp["unnamed ability"])
            abilities_dict[ability_temp["name"]] = ability_temp


print (ability_category_set)

def check_print_hp(fighterA, fighterB):
    # Copy of the function to avoid cyclical import
    print(fighterA["name"] + " HP: " + str(fighterA["curr_hp"]))
    print(fighterB["name"] + " HP: " + str(fighterB["curr_hp"]))

def check_soup_burst(attacker, move, target):
    if target["curr_hp"] <= (target["hp"]/2) and target["state_ability_activated"] is False:
        target["state_ability_activated"] = True
        print(target["name"] + " bursted scalding soup!")
        specific_moves.change_stats(target, ["phy_att","phy_def","spec_att","spec_def","speed"], \
                                    [-2,-2,-2,-2,-2])
        if specific_moves.moves_dict[move]["attr_makes_contact"] is True:
            print(attacker["name"] + " is splashed with soup!")
            moves.calculate_interaction("scald", target, attacker)
            check_print_hp(attacker, target)
        else:
            print(attacker["name"] + " avoided the soup!")
        if attacker["curr_hp"] <= 0 and target["curr_hp"] <= 0:
            target["sd_counter_win"] = True
    return 1

def check_adaptability(user, move):
    if specific_moves.moves_dict[move]["type"] in user["types"]:
        print(user["name"] + "'s " + move.title() + " is boosted by Adaptability!")
        return 2
    return 1.5

def check_technician(user, move):
    if specific_moves.moves_dict[move]["power"] <= 60:
        print(user["name"] + "'s " + move.title() + " is boosted by Technician!")
        return 1.5
    return 1

def check_moxie(user, move, target):
    if specific_moves.moves_dict[move]["category"] != "status": # If the move was an attack #TODO: Make sure a move that missed won't allow this to go through.
        specific_moves.change_stats(user, ["phy_att"], [1])

def check_punk_rock(user, move):
    '''
    For offense part of Punk Rock
    '''
    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
        print("Damage boosted by " + user["name"] + "'s Punk Rock!")
        return 1.3
    return 1

def alt_check_punk_rock(user, move, target):
    '''
    For defense part of Punk Rock 
    '''
    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
        print("Damage lowered by " + target["name"] + "'s Punk Rock!")
        return 0.5
    return 1