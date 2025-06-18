import random
import os.path
import random
import sys
import csv
import itertools
import json


moves_dict = {}

if os.path.isfile("moves.json"):
    with open("moves.json", "r", encoding="UTF-8") as moves_file:
        move_data = json.load(moves_file)
        for move in move_data["moves"]:
            move_temp = {}
            for mkey, mvalue in move.items():
                move_temp[mkey] = mvalue
            moves_dict[move_temp["name"]] = move_temp
#if os.path.isfile("all_moves.csv"):
#    with open("all_moves.csv", newline='', encoding="UTF-8") as move_file:
#        reader_obj_moves = csv.reader(move_file)
#        for row in reader_obj_moves:
#            move_temp = {
#                "type"                     : row[1],
#                "category"                 : row[2],
#                "pp"                       : int(row[3]),
#                "power"                    : int(row[4]),
#                "accuracy"                 : int(row[5]),
#                "priority"                 : int(row[6]),
#                "instances"                : int(row[7]),
#                "effect_function"          : row[8],
#                "attr_makes_contact"       : bool(row[9]),
#                "attr_affected_by_protect" : bool(row[10]),
#                "description"              : row[11]
#            }
#            moves_dict[row[0]] = move_temp

### Helper Functions ###
def check_can_be_poisoned(user, target):
    # Returns int:  Reason
    #               0: Can be poisoned
    #               1: Can't be poisoned due to type / no corrosion
    #               2: Can't be poisoned because the target already has a non-poison status
    #               3: Can't be poisoned because the target is already poisoned.
    if "poison" in target["types"] or "steel" in target["types"] and user["ability"] != "corrosion":
        return 1
    match target["status"]:
        case "poison":
            return 3
        case "none":
            return 0
        case _:
            return 2

def check_can_be_frozen(user, target):
    #if battle.curr_weather == "harsh sunlight":
    #    return False
    if target["ability"] in ["magma armor", "comatose", "purifying salt"]:
        return False
    if target["status"] == "none" and "ice" not in target["types"]:
        return True
    else:
        return False


def check_accuracy(move_accuracy):
    if random.random() < move_accuracy / 100:
        return True
    else:
        print("It missed!")
        return False

def print_stat_level_change(target, stats, levels): # levels before the change, not after
    # Use this only for the print statements. Do not make changes to the stats here.

    for s,l in zip(stats, levels):
        if l >= 1:
            if target["curr_stage_" + s] == 6:
                print(target["name"] + "'s " + s  + " can't go any higher!")
            elif l == 1:
                print(target["name"] + "'s " + s  + " increased!")
            elif l == 2:
                print(target["name"] + "'s " + s  + " sharply increased!")
            elif l >= 3:
                print(target["name"] + "'s " + s  + " rose drastically!")
        elif l <= 0:
            if target ["curr_stage_" + s] == -6:
                print(target["name"] + "'s " + s  + " can't go any lower!")
            elif l == -1:
                print(target["name"] + "'s " + s  + " fell!")
            if l == -2:
                print(target["name"] + "'s " + s  + " harshly fell!")
            if l <= -3:
                print(target["name"] + "'s " + s  + " severely fell!")

def self_thaw(user):
    if user["status"] == "freeze":
        user["status"] = "none"
        print(user + " thawed out!")

def print_status_effect(target, status, already):
    if not already:
        print(target["name"] + " is " + status + "ed!")
    else:
        print(target["name"] + " is already " + status + "ed!")


def print_ability_protect(user):
    print(user["name"] + " is protected by " + user["ability"].title() + "!")

def change_volatile_status_effect(target, status):
    if target["status"] == "none":
        target["status"] = status
        print_status_effect(target,status, False)

### Attack/Contact Moves ###

def move_acid_spray(user, target):
    if check_accuracy(moves_dict["acid spray"]["accuracy"]):
        if target["ability"] == "bulletproof":
            print_ability_protect(target)
            return [3,0,0]
        target["curr_stage_spec_def"] -= 2
        return [2,0,0]
    return [1,0,0]

def move_analyzed_impale(user, target):
    if check_accuracy(moves_dict["analyzed_impale()"]["accuracy"]):
        user["curr_hp"] -= int(user["hp"] / 16)
        print(user["name"] + " was damaged throwing its body!")
        if target["status"] == "poisoned":
            print("analyzed_impale() is boosted with poison!")
            return [2,2,1]
        return [2,1,1]
    return [1,0,0]

def move_chilling_water(user, target):
    if check_accuracy(moves_dict["chilling_ ater"]["accuracy"]):
        target["curr_stage_phy_att"] -= 1
        print_stat_level_change(target, ["phy_att"], [-1])
        return [2,0,0]
    return [1,0,0]

def move_crunch(user, target):
    if check_accuracy(moves_dict["crunch"]["accuracy"]):
        if random.random() < 0.2:
            target["curr_stage_phy_def"] -= 1
        return [2,0,0]
    return [1,0,0]

def move_drum_solo(user, target):
    '''
    TODO: The fighter switch system will need to be able to refresh this.
    '''
    #if check_accuracy(moves_dict["drum solo"]["accuracy"]):
    if check_accuracy(0):
        if "drum_soloed" in user and user["drum_soloed"] is True:
                return [0,0,0]
        user["drum_soloed"] = True
        return [2,0,0]
    return [1,0,0]

def move_heat_crash(user, target):
    # Python match-case doesn't have fall-through,
    # so there are no explicit breaks.
    if check_accuracy(moves_dict["heat crash"]["accuracy"]):
        percentage = target["weight"] / user["weight"]
        match percentage:
            case _ if percentage > 0.5:
                return [2,40,0]
            case _ if percentage >= .3335:
                return [2,60,0]
            case _ if percentage >= 25.01:
                return [2,80,0]
            case _ if percentage >= 20.01:
                return [2,100,0]
            case _:  #percentage <= 20.0
                return [2,120,0]
    return [1,0,0]

def move_ice_punch(user, target):
    if check_accuracy(moves_dict["ice punch"]["accuracy"]):
        if random.random() < 0.1:
            change_volatile_status_effect(target, "freeze")
        return [2,0,0]
    return [1,0,0]

def move_lunge(user, target):
    if check_accuracy(moves_dict["lunge"]["accuracy"]):
        target["curr_stage_phy_att"] -= 1
        return [2,0,0]
    return [1,0,0]

def move_scald(user, target):
    self_thaw(user)
    if check_accuracy(moves_dict["scald"]["accuracy"]):
        if random.random() < 0.3:
            target["status"] = "burn"
            print(target["name"] + " is burned!")
        return [2,0,0]
    else:
        return [1,0,0]

def move_sludge_bomb(user, target):
    if check_accuracy(moves_dict["sludge bomb"]["accuracy"]):
        if random.random() < 0.3:
            change_volatile_status_effect(target, "poison")
        return [2,0,0]
    return [1,0,0]

def move_sucker_punch(user, target):
    if check_accuracy(moves_dict["sucker punch"]["accuracy"]):
        if moves_dict[target["queued_move"]]["category"] != "status":
            return [2,0,0]
        else:
            return [0,0,0]

def move_scrape(user, target):
    if check_accuracy(moves_dict["scrape()"]["accuracy"]):
        poison_reason = check_can_be_poisoned(user, target)
        if poison_reason == 0:
            target["status"] = "poison"
            print_status_effect(target,"poison", False)
        elif poison_reason == 3:
            print_status_effect(target,"poison", True)
        if poison_reason in [0,3]:
            print_stat_level_change(user, ["spec_att", "phy_def", "spec_def"], [2, -1, -1])
            user["curr_stage_spec_att"] += 2
            user["curr_stage_phy_def"] -= 1
            user["curr_stage_spec_def"] -= 1
        elif poison_reason in [1,2]:
            return[0,0,0]
        return[3,0,0]
    return [1,0,0]

def move_toxic(user, target):
    # Toxic specifically sets the badly poison level to 1.
    if check_accuracy(moves_dict["toxic"]["accuracy"]):
        if check_can_be_poisoned(user, target) != 0:
            print("It had no effect!")
        else:
            target["status"] = "poison"
            target["badly_poison_level"] = 1
            print_status_effect(target, "badly poison", False)
        return [3,0,0]
    return [1,0,0]

def move_u_turn(user, target):
    '''
    Properly fill this in when the team system is working.
    '''
    if check_accuracy(moves_dict["u-turn"]["accuracy"]):
        return [2,0,0]
    return [1,0,0]

# Status Moves

def move_autotomize(user):
    print_stat_level_change(user, ["speed"], [2])
    user["curr_stage_speed"] += 2
    user["weight"] -= 100.0
    if user["weight"] < 0.1:
        user["weight"] = 0.1

def move_belly_drum(user):
    print_stat_level_change(user, ["phy_att"], [6])
    print(user["name"] + "'s HP went down!")
    user["curr_hp"] *= 0.5
    user["curr_stage_phy_att"] = 6

def move_dragon_dance(user):
    print_stat_level_change(user, ["phy_att", "speed"], [1, 1])
    user["curr_stage_phy_att"] += 1
    user["curr_stage_speed"] += 1

def move_protect(user):
    '''
    The count is refreshed during the battle loop as needed.
    '''
    allow_protect = False
    user["count_protect"] += 1

    if user["count_protect"] == 1:
        allow_protect = True
    else:
        chance = 1/(3**user["count_protect"])
        #print("chance: " + str(chance))
        if random.random() < chance:
            allow_protect = True
        else:
            print("Protect failed!")
            allow_protect = False
    if allow_protect:
        user["state_protect"] = True
    else:
        user["state_protect"] = False
