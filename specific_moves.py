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
            elif l == -2:
                print(target["name"] + "'s " + s  + " harshly fell!")
            elif l <= -3:
                print(target["name"] + "'s " + s  + " severely fell!")

def change_stats(target, stats, levels):
    '''
    Use this to validate the math for a stat change.
    '''
    capped_levels = []
    for s, l in zip(stats, levels):
        current_stage = target["curr_stage_" + s]
        proposed_change = current_stage + l
        final_change = proposed_change
        if proposed_change <= -6:
            final_change = -6
        elif proposed_change >= 6:
            final_change = 6
        capped_levels.append(final_change)
    
    print_stat_level_change(target, stats, capped_levels)


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
        change_stats(target, ["spec_def"], [-2])
        return [2,0,0]
    return [1,0,0]

def move_analyzed_impale(user, target):
    if check_accuracy(moves_dict["analyzed_impale()"]["accuracy"]):
        user["curr_hp"] -= int(user["hp"] / 16)
        user["curr_hp"] = max(0, user["curr_hp"])
        if user["curr_hp"] == 0:
            user["sd_counter_win"] = True
        print(user["name"] + " was damaged throwing its body!")
        if target["status"] == "poisoned":
            print("analyzed_impale() is boosted with poison!")
            return [2,2,1]
        return [2,1,1]
    return [1,0,0]

def move_chilling_water(user, target):
    if check_accuracy(moves_dict["chilling water"]["accuracy"]):
        change_stats(target, ["phy_att"], [-1])
        return [2,0,0]
    return [1,0,0]

def move_crunch(user, target):
    if check_accuracy(moves_dict["crunch"]["accuracy"]):
        if random.random() < 0.2:
            change_stats(target, ["phy_def"], [-1])
        return [2,0,0]
    return [1,0,0]

def move_drain_punch(user, target):
    '''
    TODO: Fill out this move to utilize the damage calculation
    to get the correct HP.
    '''
    if check_accuracy(moves_dict["drain punch"]["accuracy"]):
        healing_amount = calculate_interaction_damage_only("drain punch", user, target)
        user["curr_hp"] += 0
        return [2,0,0]
    return [1,0,0]

def move_drum_solo(user, target):
    '''
    TODO: The fighter switch system will need to be able to refresh this.
    '''
    if check_accuracy(moves_dict["drum solo"]["accuracy"]):
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
        change_stats(target, ["phy_att"], [-1])
        #if check_can_change_stat(target, "phy_att", -1):
        #    target["curr_stage_phy_att"] -= 1
        #    print_stat_level_change(target, ["phy_att"], [-1])
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
        try:
            if moves_dict[target["queued_move"]]["category"] != "status":
                return [2,0,0]
            return [0,0,0]
        except KeyError: # In case the opponent recalls.
            return [0, 0, 0]

def move_scrape(user, target):
    if check_accuracy(moves_dict["scrape()"]["accuracy"]):
        poison_reason = check_can_be_poisoned(user, target)
        if poison_reason == 0:
            target["status"] = "poison"
            print_status_effect(target,"poison", False)
        elif poison_reason == 3:
            print_status_effect(target,"poison", True)
        if poison_reason in [0,3]:
            change_stats(user, ["spec_att","phy_def","spec_def"], [2,-1,-1])
        elif poison_reason in [1,2]:
            return[0,0,0]
        return[3,0,0]
    return [1,0,0]

def move_toxic(user, target):
    '''
    Toxic specifically sets the badly poison level to 1.
    '''
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
        return [4,0,0]
    return [1,0,0]






# Status Moves

def move_autotomize(user):
    change_stats(user, ["speed"], [2])
    user["weight"] -= 100.0
    if user["weight"] < 0.1:
        user["weight"] = 0.1

def move_belly_drum(user):
    print_stat_level_change(user, ["phy_att"], [6])
    print(user["name"] + "'s HP went down!")
    user["curr_hp"] *= 0.5
    user["curr_hp"] = int(user["curr_hp"])
    user["curr_stage_phy_att"] = 6

def move_dragon_dance(user):
    change_stats(user, ["phy_att", "speed"], [1, 1])

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





# Swapping Out Fighter
##def move_recall(current_fighter):
##    print("hi")
    #for t in current_fighter["team"]:
    #    print(str(t["team_slot"]) + ": " + t["name"])
    #choice = input("Which teammate?\n")

#    print(current_fighter["name"] + " is going back!")
#    usable_range = list(range(len(current_fighter["team"])))
#    usable_range.remove(current_fighter["team_slot"])
#    next_f = 999
#    while int(next_f) not in usable_range:
#        for ic in usable_range:
#            print(str(ic) + ": " + current_fighter["team"][ic]["name"])
#        next_f = input("Which character?\n")



                #print("Recall for team A:")
                #usable_range = [0, 1]
                #usable_range.remove(fighter_a["team_slot"])
                #next_f = 999
                #while int(next_f) not in usable_range:
                #    for ic in usable_range:
                #        print(str(ic) + ": " + team_a[ic]["name"])
                #    next_f = input("Which character?\n")
