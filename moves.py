import json
import csv
import os.path
import specific_moves
import abilities
import random

stage_multiplier_main_stats_dict = {
    -6: 2/8,
    -5: 2/7,
    -4: 2/6,
    -3: 2/5,
    -2: 1/2,
    -1: 2/3,
     0: 1,
     1: 3/2,
     2: 2,
     3: 5/2,
     4: 3,
     5: 7/2,
     6: 4
}

major_status_set = {"burn", "sleep", "paralyze", "poison", "freeze"}
minor_status_set = {"confuse", "infatuate"}
dinu_moves_set = {"scrape()", "analyzed_impale()"}

damage_multiplier_poison = 1/8
damage_multiplier_badly_poison = 1/16
damage_multiplier_burn = 1/16

types_dict = {}

if os.path.isfile("type_chart.csv"):
    with open("type_chart.csv", newline='', encoding="UTF-8") as type_file:
        reader_obj_types = csv.reader(type_file)
        for row in reader_obj_types:
            type_temp = {
                "normal"   : row[1],
                "fire"     : row[2],
                "water"    : row[3],
                "electric" : row[4],
                "grass"    : row[5],
                "ice"      : row[6],
                "fighting" : row[7],
                "poison"   : row[8],
                "ground"   : row[9],
                "flying"   : row[10],
                "psychic"  : row[11],
                "bug"      : row[12],
                "rock"     : row[13],
                "ghost"    : row[14],
                "dragon"   : row[15],
                "dark"     : row[16],
                "steel"    : row[17],
                "fairy"    : row[18],
            }
            types_dict[row[0]] = type_temp

natures_dict = {}
if os.path.isfile("natures.json"):
    with open("natures.json", "r", encoding="UTF-8") as nature_file:
        nature_data = json.load(nature_file)
        nature_temp = {}
        for nature in nature_data["natures"]:
            for nkey, nvalue in nature.items():
                nature_temp[nkey] = nvalue
            natures_dict[nature_temp["name"]] = nature


def change_stage_main_stat(target, stat, change):
    if target[stat] == 6 and change > 0:
        print(stat + " can't go any higher!")
    elif target[stat] == -6 and change < 0:
        print(stat + " can't go any lower!")
    else:
        target[stat] = target[stat] + change
        if target[stat] < 6:
            target[stat] = 6
        elif target[stat] < -6:
            target[stat] = -6

def protect_check(user, move, target):
    '''
    Situations where the move breaks the protect, or if the protect variant has
    additional effects, are handled in the individual move functions.
    '''
    if (specific_moves.moves_dict[user["queued_move"]]["attr_bypass_protect"] is True) or \
        (user["queued_move"] == "curse" and "ghost" in user["types"]):
        print("Protect bypassed!")
        return False
    if target["state_protect"] is True:
        print(target["name"] + " protected itself!")
        return True
    return False


def do_status_move(user, move):
    #print("jojo")
    #print(specific_moves.moves_dict[move]["effect_function"])
    #try:
    move_function = specific_moves.moves_dict[move]["effect_function"]
    if move_function != "none":
        move_function = getattr(specific_moves, move_function)
        move_function(user)
        #return
    #except KeyError:
    #    print("Move Function for " + move + " not found!")
    return

def ability_check_category_1(user, target, move, move_power):
    '''
    Experimental / Work In Progress
    Not general enough.
    Currently works just for Technician.
    '''

    try:
        ability_function = abilities.abilities_dict[user["ability"]]["effect_function"]
        if ability_function == "check_technician":
            curr_ability_function = getattr(abilities, ability_function)
            return curr_ability_function(user, target, move, move_power)
    except KeyError:
        return move_power

    return move_power

def check_ability_based_modifiers(move, user, target):
    '''
    Also experimental / work in progress
    Not general enough.
    Currently works just for Punk Rock.
    '''
    mod_user = 1
    mod_target = 1
    if user["ability"] == "punk rock" or target["ability"] == "punk rock":
        mod_user, mod_target = abilities.check_punk_rock(user, target, move)
    return mod_user, mod_target


def unusual_damage_stat_to_use_check(user, move, phy_a, spec_a, phy_d, spec_d):
    '''
    For unusual moves that break the usual physical/special stat interations.
    Return the [attack, defense] to use.

    Shell Side Arm: The only modifiers used are stat stages.
                    In a tie, it's a random pick.
    '''
    if move.lower() in ["psyshock", "psystrike", "secret sword"]:
        return spec_a, phy_d
    if move.lower() == "shell side arm":
        forecast_phy_att = stage_multiplier_main_stats_dict[user["curr_stage_phy_att"]] * user["phy_att"]
        forecast_spec_att = stage_multiplier_main_stats_dict[user["curr_stage_spec_att"]] * user["spec_att"]

        if (forecast_phy_att/phy_d) > (forecast_spec_att/spec_d):
            return phy_a, phy_d
        elif (forecast_phy_att/phy_d) < (forecast_spec_att/spec_d):
            return spec_a, spec_d
        else:
            if random.random() < 0.5:
                return phy_a, phy_d
            else:
                return spec_a, spec_d
    # Default
    if specific_moves.moves_dict[move]["category"] == "physical":
        return phy_a, phy_d
    else:
        return spec_a, spec_d

def calculate_interaction(move, user, target):
    damage = 0
    move_power = specific_moves.moves_dict[move]["power"]
    # Irregular Effect
    move_function = specific_moves.moves_dict[move]["effect_function"]

    if move_function != "none":
        curr_irregular_move_function = getattr(specific_moves, move_function)
        result = curr_irregular_move_function(user, target)
        # Tuple Code System
        # [0]: 0: Failure, 1: Missed, 2: Success (Regular Interaction)
        #      3: Success OR Failed via Ability Resolve (Halt calculate_interaction() Immediately)
        # [1]: Irregular damage to apply
        # [2]: 0: The return value is a damage addition. 1: The return value is a damage multiplier.
        if result[0] == 0:
            print("It failed!")
            return
        elif result[0] == 1:
            return
        elif result[0] == 2:
            if result[2] == 0:
                move_power += result[1]
            elif result[2] == 1:
                move_power *= result[1]
        else: # result[0] == 3
            return
    else: # Basic attack; just do the accuracy check.
        if specific_moves.check_accuracy(specific_moves.moves_dict[move]["accuracy"]) is False:
            return


    # Ability Check: Offense abilities that start with the calculated move_power, such as Technician
    move_power = ability_check_category_1(user, target, move, move_power)

    # Offense and Defense Stats
    phy_attack_stat = user["phy_att"] * stage_multiplier_main_stats_dict[float(user["curr_stage_phy_att"])]
    phy_def_stat = target["phy_def"] * stage_multiplier_main_stats_dict[float(target["curr_stage_phy_def"])]
    spec_attack_stat = user["spec_att"] * stage_multiplier_main_stats_dict[float(user["curr_stage_spec_att"])]
    spec_def_stat = target["spec_def"] * stage_multiplier_main_stats_dict[float(target["curr_stage_spec_def"])]

    if specific_moves.moves_dict[move]["category"] == "physical":
        attack_stat_to_use = phy_attack_stat
        def_stat_to_use = phy_def_stat
    else:
        attack_stat_to_use = spec_attack_stat
        def_stat_to_use = spec_def_stat

    attack_stat_to_use, def_stat_to_use = \
        unusual_damage_stat_to_use_check(user, move, phy_attack_stat, spec_attack_stat, phy_def_stat, spec_def_stat)

    damage = (((user["level"] * 2) / 5) + 2) * move_power
    
    damage *= (attack_stat_to_use/def_stat_to_use)
    damage /= 50


    # User Burned
    if user["status"] == "burn" and specific_moves.moves_dict[move]["category"] == "physical":
        damage = damage * 0.5
        print("Damage reduced because " + user["name"] + " is burned!")

    # STAB
    if specific_moves.moves_dict[move]["type"] in user["types"]:
        damage = damage * 1.5

    # Type Effectiveness
    type_multiplier = 1.0
    for t in target["types"]:
        type_multiplier *= float(types_dict[specific_moves.moves_dict[move]["type"]][t])
    damage *= type_multiplier

    # Ability-Based Modifiers
    for d in check_ability_based_modifiers(move, user, target):
        damage *= d


    target["curr_hp"] -= int(damage)
    target["curr_hp"] = max(0, target["curr_hp"])

    match type_multiplier:
        case 2.0 | 4.0:
            print("It's super effective!")
        case 0.5:
            print("It's not very effective...")
        case 0:
            print("It had no effect!")
