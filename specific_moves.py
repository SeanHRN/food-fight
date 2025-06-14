import random
import os.path
import random
import sys
import csv
import itertools

moves_dict = {}
if os.path.isfile("all_moves.csv"):
    with open("all_moves.csv", newline='', encoding="UTF-8") as move_file:
        reader_obj_moves = csv.reader(move_file)
        for row in reader_obj_moves:
            move_temp = {
                "type"                     : row[1],
                "category"                 : row[2],
                "pp"                       : int(row[3]),
                "power"                    : int(row[4]),
                "accuracy"                 : int(row[5]),
                "priority"                 : int(row[6]),
                "instances"                : int(row[7]),
                "effect_function"          : row[8],
                "attr_makes_contact"       : bool(row[9]),
                "attr_affected_by_protect" : bool(row[10]),
                "description"              : row[11]
            }
            moves_dict[row[0]] = move_temp

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

def accuracy_check():
    return True


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


def print_status_effect(target, status, already):
    if not already:
        print(target["name"] + " is " + status + "ed!")
    else:
        print(target["name"] + " is already " + status + "ed!")


def print_ability_protect(user):
    print(user["name"] + " is protected by " + user["ability"].title() + "!")

### Attack/Contact Moves ###

def move_acid_spray(user, target):
    if accuracy_check():
        if target["ability"] == "bulletproof":
            print_ability_protect(target)
            return [3,0,0]
        target["curr_stage_spec_def"] -= 2
        return [2,0,0]
    return [1,0,0]

def move_crunch(user, target):
    if accuracy_check():
        if random.random() < 0.2:
            target["curr_stage_phy_def"] -= 1
        return [2,0,0]
    return [1,0,0]

def move_analyzed_impale(user, target):
    if accuracy_check():
        user["curr_hp"] -= int(user["max_hp"] / 16)
        if target["status"] == "poisoned":
            print("analyzed_impale() is boosted with poison!")
            return [2,2,1]
        return [2,1,1]
    return [1,1,1]

def move_heat_crash(user, target):
    # Python match-case doesn't have fall-through,
    # so there are no explicit breaks.
    if accuracy_check():
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

def move_sludge_bomb(user, target):
    if accuracy_check():
        if random.random() < 0.3:
            if target["status"] == "none":
                target["status"] = "poison"
                print_status_effect(target,"poison", False)
        return [2,0,0]
    return [1,0,0]

def move_sucker_punch(user, target):
    if accuracy_check():
        if moves_dict[target["queued_move"]]["category"] != "status":
            return [2,0,0]
        else:
            return [0,0,0]

def move_scrape(user, target):
    if accuracy_check():
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
    if accuracy_check():
        if check_can_be_poisoned(user, target) != 0:
            print("It had no effect!")
        else:
            target["status"] = "poison"
            target["badly_poison_level"] = 1
            print_status_effect(target, "badly poison", False)
        return [3,0,0]
    return [1,0,0]


# Status Moves

def move_autotomize(user):
    print_stat_level_change(user, ["speed"], [2])
    user["curr_stage_speed"] += 2
    user["weight"] -= 100.0
    if user["weight"] < 0.1:
        user["weight"] = 0.1

def move_dragon_dance(user):
    print_stat_level_change(user, ["phy_att", "speed"], [1, 1])
    user["curr_stage_phy_att"] += 1
    user["curr_stage_speed"] += 1