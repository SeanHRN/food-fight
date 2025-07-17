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
 # 3: Modifier for damage reduction OR it's a counter ability
 # 4: Whatever Skill Link is - variable hit modifier?
 # 6: Activated upon summon
ability_category_set = [set() for _ in range(7)]
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

def check_print_hp(fighterA, fighterB):
    # Copy of the function to avoid cyclical import
    print(fighterA["name"] + " HP: " + str(fighterA["curr_hp"]))
    print(fighterB["name"] + " HP: " + str(fighterB["curr_hp"]))

def check_soup_burst(attacker, move, target, damage):
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
    return damage

def check_adaptability(user, move):
    '''
    It's 0.5 as an addition to the existing 1.5 STAB.
    '''
    if specific_moves.moves_dict[move]["type"] in user["types"]:
        print(user["name"] + "'s " + move.title() + " is boosted by Adaptability!")
        return 0.5, "none"
    return 0, "none"

def check_aerilate(user, move):
    if specific_moves.moves_dict[move]["type"] == "normal":
        print(user["name"] + "'s " + move.title() + " is boosted by Aerilate!")
        return 0.20, "flying"
    return 0, "none"

def check_pixilate(user, move):
    if specific_moves.moves_dict[move]["type"] == "normal":
        print(user["name"] + "'s " + move.title() + " is boosted by Pixilate!")
        return 0.20, "fairy"
    return 0, "none"

def check_normalize(user, move):
    if specific_moves.moves_dict[move]["type"] == "normal":
        print(user["name"] + "'s " + move.title() + " is boosted by Normalize!")
        return 0.20, "none"
    return 0, "none"

def check_refrigerate(user, move):
    if specific_moves.moves_dict[move]["type"] == "normal":
        print(user["name"] + "'s " + move.title() + " is boosted by Refrigerate!")
        return 0.20, "ice"
    return 0, "none"

def check_galvanize(user, move):
    if specific_moves.moves_dict[move]["type"] == "normal":
        print(user["name"] + "'s " + move.title() + " is boosted by Galvanize!")
        return 0.20, "electric"
    return 0, "none"

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

def alt_check_punk_rock(user, move, target, damage):
    '''
    For defense part of Punk Rock 
    '''
    if "attr_sound" in specific_moves.moves_dict[move] and specific_moves.moves_dict[move]["attr_sound"]:
        print("Damage lowered by " + target["name"] + "'s Punk Rock!")
        return damage * 0.5
    return damage

def check_sturdy(user, move, target, damage):
    if target["hp"] == target["curr_hp"] and damage >= target["hp"]:
        damage = target["hp"] - 1
        print(target["name"] + " held on with Sturdy!")
    return damage

def check_intimidate(user, target):
    print(user["name"] + "'s Intimidate!")
    specific_moves.change_stats(target,["phy_att"], [-1])