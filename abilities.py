import random
import os.path
import random
import sys
import csv
import itertools
import specific_moves
import moves


abilities_dict = {}
if os.path.isfile("all_abilities.csv"):
    with open("all_abilities.csv", newline='', encoding="UTF-8") as type_file:
        reader_obj_abilities = csv.reader(type_file)
        for row in reader_obj_abilities:
            ability_temp = {
                "effect_function": row[1],
                "description"    : row[2]
            }
            abilities_dict[row[0]] = ability_temp

def check_print_hp(fighterA, fighterB):
    # Copy of the function to avoid cyclical import
    print(fighterA["name"] + " HP: " + str(fighterA["curr_hp"]))
    print(fighterB["name"] + " HP: " + str(fighterB["curr_hp"]))

def check_soup_burst(user, target):
    if user["ability"].lower() == "soup burst" and user["curr_hp"] <= (user["hp"]/2) and user["state_ability_activated"] is False:
        user["state_ability_activated"] = True
        print(user["name"] + " bursted soup!")
        user["curr_stage_phy_att"] -= 2
        user["curr_stage_phy_def"] -= 2
        user["curr_stage_spec_att"] -= 2
        user["curr_stage_spec_def"] -= 2
        user["curr_stage_speed"] -= 2
        print(user["name"] + "'s stats sharply decreased!")
        moves.calculate_interaction("scald", user, target)
        check_print_hp(user, target)

def check_technician(user, target, move, move_power):
    if user["ability"].lower() == "technician":
        if move_power <= 60:
            print(user["name"] + "'s " + move.title() + " is boosted by Technician!")
            return move_power * 1.50
    return move_power

def check_punk_rock(user, target, move):
    val_user = 1
    val_target = 1
    if user["ability"].lower() == "punk rock":
        val_user = 1.30
        print("Damage boosted by Punk Rock!")
    if target["ability"].lower() == "punk rock":
        val_target = 0.5
        print("Damage lowered by Punk Rock!")
    return val_user, val_target
