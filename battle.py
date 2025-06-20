import math
import itertools
import os.path
import random
import sys
import csv
import json
import moves
import specific_moves
import abilities
sys.path.append(os.getcwd())


def case_change(move):
    if move in moves.dinu_moves_set:
        return move
    else:
        return move.title()

def test_character(fighter):
    print(fighter["curr_hp"])
    print(fighter["move_0"])

def do_turn(user, move, target):
    # By using check_round_middle,
    # returns False: Target is not out of HP
    # returns True:  Target is out of HP. The fight is over.
    print("\n--------------")
    print(user["name"] + " used " + case_change(move) + "!\n")

    if not move in specific_moves.moves_dict:
        print("\"" + move + "\"" + " was not found!")
        return False

    if specific_moves.moves_dict[move]["category"] == "status":
        moves.do_status_move(user, move)

    # Uses a loop so that multi-hit moves can work.
    elif specific_moves.moves_dict[move]["category"] != "status":
        if moves.protect_check(user, move, target) is False:
            for _ in itertools.repeat(None, specific_moves.moves_dict[move]["instances"]):
                moves.calculate_interaction(move, user, target)
                if check_round_middle(user, target):    # If someone is out of HP, return true. If not, keep going.
                    return True
    return False

def check_print_hp(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for f in l:
        print(f["name"] + " HP: " + str(f["curr_hp"]))

def check_print_status(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for fighter in l:
        if fighter["status"]:
            print("Status effect(s) on " + fighter["name"] + ": ", end="")
            for s in fighter["status"]:
                print(s)

def check_round_start(fighter_a, fighter_b):
    #print("check round start")
    l = [fighter_a, fighter_b]
    for f in l:
        f["state_protect"] = False


def check_ability(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for index,f in enumerate(l):
        abilities.check_soup_burst(f, l[1-index])


def check_round_middle(fighter_a, fighter_b):
    check_print_hp(fighter_a, fighter_b)
    check_ability(fighter_a, fighter_b)
    for f in [fighter_a, fighter_b]:
        if f["curr_hp"] <= 0:
            print("\n" + f["name"] + " fainted!")
    return fighter_a["curr_hp"] <= 0 or fighter_b["curr_hp"] <= 0

def check_round_end(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for fi in l:
        if fi["status"] == "poison":
            if fi["badly_poisoned"]:
                fi["curr_hp"] -= int(fi["hp"] * \
                    float(fi["badly_poisoned_level"]) * moves.damage_multiplier_badly_poison)
                fi["badly_poisoned_level"] += moves.damage_multiplier_badly_poison
            else:
                fi["curr_hp"] -= int(fi["hp"] * moves.damage_multiplier_poison)
            print(fi["name"] + " is hurt by poison!")
            print("HP is now: " + str(fi["curr_hp"]))
        elif fi["status"] == "burn":
            fi["curr_hp"] -= int(fi["hp"] * moves.damage_multiplier_burn)
        fi["curr_hp"] = max(0, fi["curr_hp"])

def do_battle(fighter_a, fighter_b):
    #
    # Per round:
    #     1. Check starting conditions.
    #     2. Get move inputs. The user may use numbers 0-3 or the full name of the move.
    #     3. Check who goes first based on priority and speed.
    #     4. Do the first move.
    #     5. Check the result.
    #     6. Do the second move.
    #     7. Check the result.
    #
    # Check the conditions of the completion of the battle to break ties.
    while (fighter_a["curr_hp"] > 0 and fighter_b["curr_hp"] > 0):
        print()
        check_round_start(fighter_a, fighter_b)

        turn_priority = {"a" : 0, "b" : 0}
        for index, f in enumerate([fighter_a, fighter_b]):
            selected_move = ""
            sufficient_pp = False
            while selected_move not in f["moves"] and sufficient_pp is False:
                print("Choose " + f["name"] + "'s Move: \n", end="")
                longest_name_length = len(max(f["moves"], key=len))
                longest_type_length = 0
                for m in f["moves"]:
                    new_type_len = len(specific_moves.moves_dict[m]["type"])
                    longest_type_length = max(longest_type_length, new_type_len)

                for num, m in enumerate(f["moves"]):
                    pad0 = " " * (longest_name_length - len(m))
                    pad1 = " " + (" " * (longest_type_length - len(specific_moves.moves_dict[m]["type"])))
                    tv = (str(num), case_change(m), pad0, specific_moves.moves_dict[m]["type"].title(), pad1, str(f["pps"][num]))
                    f_string_moves = f"{tv[0]}: {tv[1]} {tv[2]}-- {tv[3]}{tv[4]} -- PP: {tv[5]}"
                    print(f_string_moves)

                selected_move = input("\n")
                if selected_move.isdigit() and int(selected_move) in range(4):
                    if f["pps"][int(selected_move)] == 0:
                        print("\nThere's no PP left for this move!\n")
                    else:
                        f["pps"][int(selected_move)] -= 1
                        selected_move = f["moves"][int(selected_move)]
 
            f["queued_move"] = selected_move
            print("[   " + case_change(selected_move) + "   ]\n")
            if selected_move != "protect": # Refresh Protect Counter
                f["count_protect"] = 0
            try:
                pri = int(specific_moves.moves_dict[f["queued_move"]]["priority"])
            except KeyError:
                pri = 0
            if index == 0:
                turn_priority["a"] = pri
            else:
                turn_priority["b"] = pri

        goes_first = 'a'


        # Priority Check
        if turn_priority["a"] < turn_priority["b"]:
            goes_first = 'b'
        if turn_priority["a"] == turn_priority["b"]:
            speed_mult_a = moves.stage_multiplier_main_stats_dict[fighter_a["curr_stage_speed"]]
            speed_mult_b = moves.stage_multiplier_main_stats_dict[fighter_b["curr_stage_speed"]]
            if fighter_a["speed"] * speed_mult_a < fighter_b["speed"] * speed_mult_b:
                goes_first = 'b'
            elif fighter_a["speed"] == fighter_b["speed"]:
                if random.random() < 0.5:
                    goes_first = 'b'

        # Speed Check
        # 'if not', meaning: If this doesn't end the fight, keep going.
        print("- - - - - - - - -")
        if goes_first == 'a':
            if not do_turn(fighter_a, fighter_a["queued_move"], fighter_b):
                do_turn(fighter_b, fighter_b["queued_move"], fighter_a)
        else:
            if not do_turn(fighter_b, fighter_b["queued_move"], fighter_a):
                do_turn(fighter_a, fighter_a["queued_move"], fighter_b)

        if (fighter_a["curr_hp"] > 0 and fighter_b["curr_hp"] > 0):
            check_round_end(fighter_a, fighter_b)


        for f in [fighter_a, fighter_b]:
            f["previous_move"] = f["queued_move"]
        print("- - - - - - - - -")

    if fighter_a["curr_hp"] > 0 >= fighter_b["curr_hp"]:
        print(fighter_a["name"] + " wins!")
    elif fighter_b["curr_hp"] > 0 >= fighter_a["curr_hp"]:
        print(fighter_b["name"] + " wins!")
    else: # Tie Breakers
        for f in [fighter_a, fighter_b]:
            if "sd_counter_win" in f and f["sd_counter_win"] is True:
                print(f["name"] + " wins!")
                f["defeated_opponent"] = True


def determine_stats(f):
    '''
    Uses the formulas to convert the base stats, level, EVs, and IVs into the actual stats.
    '''
    # HP
    if f["name"].lower() != "shedinja":
        f["hp"] = 2 * f["base_hp"] + f["iv_hp"]
        f["hp"] += f["ev_hp"] * 0.25
        f["hp"] *= f["level"]
        f["hp"] /= 100
        f["hp"] += f["level"] + 10
        f["hp"] = int(f["hp"])
    else:
        f["hp"] = 1
    f["curr_hp"] = int(f["hp"])

    # All Other Stats
    # Default to Serious nature if the nature is undefined.
    try:
        up_stat = moves.natures_dict[f["nature"]]["up"]
        down_stat = moves.natures_dict[f["nature"]]["down"]
    except KeyError:
        up_stat = moves.natures_dict["serious"]["up"]
        down_stat = moves.natures_dict["serious"]["down"]

    nature_multiplier = 0

    for stat in ["phy_att", "phy_def", "spec_att", "spec_def", "speed"]:
        if up_stat == stat and down_stat != stat: # Neutral natures have cancelling ups and downs.
            nature_multiplier = 1.10
        elif down_stat == stat:
            nature_multiplier = 0.9
        else:
            nature_multiplier = 1.0
        s = 2 * f["base_"+stat] + f["iv_"+stat] + f["ev_"+stat]
        s *= f["level"]
        s /= 100
        s += 5
        s *= nature_multiplier
        f[stat] = int(s)


def debug_print(fighter_a, fighter_b):
    print("\n-- Fighters' Stats: --\n")
    for f in [fighter_a, fighter_b]:
        print(f["name"])
        for s in ["hp","phy_att","phy_def","spec_att","spec_def","speed"]:
            print(s + ": " + str(f[s]))
        print()

### Start of the part that runs. ###

BATTLE_CAN_HAPPEN = False
roster = {}

if os.path.isfile("fighters.json"):
    with open("fighters.json", "r", encoding="UTF-8") as fighter_file:
        fighter_data = json.load(fighter_file)
        for fighter in fighter_data["fighters"]:

            fighter_temp = {}
            for key, value in fighter.items():
                fighter_temp[key] = value
            # For values not declared in the character JSON
            fighter_temp["curr_stage_phy_att"] = 0
            fighter_temp["curr_stage_phy_def"] = 0
            fighter_temp["curr_stage_spec_att"] = 0
            fighter_temp["curr_stage_spec_def"] = 0
            fighter_temp["curr_stage_speed"] = 0
            fighter_temp["curr_stage_accuracy"] = 0
            fighter_temp["curr_stage_evasion"] = 0
            fighter_temp["state_protect"] = False
            fighter_temp["state_ability_activated"] = False
            fighter_temp["status"] = "none"
            fighter_temp["badly_poisoned_level"] = 0
            fighter_temp["badly_poisoned"] = False
            fighter_temp["confused"] = False
            fighter_temp["infatuated"] = False
            fighter_temp["queued_move"] = "blank"
            fighter_temp["previous_move"] = "blank"
            fighter_temp["count_protect"] = 0
            fighter_temp["hp"] = 0
            fighter_temp["phy_att"] = 0
            fighter_temp["phy_def"] = 0
            fighter_temp["spec_att"] = 0
            fighter_temp["spec_def"] = 0
            fighter_temp["speed"] = 0
            determine_stats(fighter_temp)
            # Start the moves with the pp from the moves dict.
            # If the move is undefined, give it 10 pp.
            for pp, mv in zip(["pp_0", "pp_1", "pp_2", "pp_3"], ["move_0", "move_1", "move_2", "move_3"]):
                try:
                    fighter_temp[pp] = specific_moves.moves_dict[fighter_temp[mv]]["pp"]
                except KeyError:
                    fighter_temp[pp] = 10

            fighter_temp["moves"] = [fighter_temp["move_0"],fighter_temp["move_1"],fighter_temp["move_2"],fighter_temp["move_3"]]
            fighter_temp["pps"] = [fighter_temp["pp_0"],fighter_temp["pp_1"],fighter_temp["pp_2"],fighter_temp["pp_3"]]
            roster[fighter_temp["id"]] = fighter_temp
        if fighter_data:
            BATTLE_CAN_HAPPEN = True


if BATTLE_CAN_HAPPEN:
    select_a = 99999
    select_b = 99999

    # TODO: Add team structure. Currently, it's just 1v1.

    while select_a not in range(0, len(roster)):
        print("\n- - -Select Character 1 - - -")
        for i,c in enumerate(roster):
            print(str(i) + ": " + roster[c]["name"])
        select_a = int(input())

    while select_b not in range(0, len(roster)):
        print("\n- - - Select Character 2 - - -")
        for i,c in enumerate(roster):
            print(str(i) + ": " + roster[c]["name"])
        select_b = int(input())

    char_a = roster[select_a].copy()
    char_b = roster[select_b].copy()


    print("\n\n--------------\n")

    debug_print(char_a, char_b)

    print("\n\n--------------\n")

    check_print_hp(char_a, char_b)
    do_battle(char_a, char_b)

    print("\n\n--------------\n")
