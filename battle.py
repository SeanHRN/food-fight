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
import re
import numbers

sys.path.append(os.getcwd())


def case_change(move):
    if move in moves.dinu_moves_set:
        return move
    else:
        return move.title()

def test_character(f):
    print(f["curr_hp"])

def check_multi_hit_variable_type_1(user):
    if user["ability"] == "skill link":
        print(user["name"] + "'s attack is boosted by Skill Link!")
        return 5
    random_number = random.random()
    if random_number <= .125:
        return 5
    if random_number <= .25:
        return 4
    if random_number <= .375:
        return 3
    return 2

def do_turn(user, move, target):
    # By using check_round_middle,
    # returns False: Target is not out of HP
    # returns True:  Target is out of HP. The fight is over.
    # Second return value:  10: Nothing
    #                      0-5: User used U-turn, and this is the move selection.
    # Third return value: 
    # TODO: Check when U-Turn defeats an opponent.
    print("\n--------------")
    # Experimental: Freeze/Paralysis Status
    if user["status"] == "freeze":
        freeze_number = random.random()
        if freeze_number <= .2:
            user["status"] = "none"
            print(user["name"] + " thawed out!")
        else:
            print(user["name"] + " is frozen solid!")
            return False, 10
    print(user["name"] + " used " + case_change(move) + "!\n")

    if not move in specific_moves.moves_dict:
        print("\"" + move + "\"" + " was not found!")
        return False

    if specific_moves.moves_dict[move]["category"] == "status":
        moves.do_status_move(user, move)

    # Uses a loop so that multi-hit moves can work.
    elif specific_moves.moves_dict[move]["category"] != "status":
        if moves.protect_check(user, move, target) is False:
            try:
                curr_instances = specific_moves.moves_dict[move]["instances"]
                if not isinstance(curr_instances, numbers.Number):
                    if curr_instances == "variable_type_1":
                        curr_instances = check_multi_hit_variable_type_1(user)
            except KeyError:
                curr_instances = 1

            for _ in itertools.repeat(None, curr_instances):
                move_output = moves.calculate_interaction(move, user, target)
                if move in moves.u_turn_set and move_output in range(len(user["team"])):
                    return False, move_output
                if check_round_middle(user, target):    # If someone is out of HP, return true. If not, keep going.
                    return True, move_output
    return False, 10

def check_print_hp(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for f in l:
        print("   " + f["name"] + " HP: " + str(f["curr_hp"]))

def check_print_status(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for f in l:
        if f["status"]:
            print("Status effect(s) on " + f["name"] + ": ", end="")
            for s in f["status"]:
                print(s)

def check_round_start(fighter_a, fighter_b):
    l = [fighter_a, fighter_b]
    for f in l:
        f["state_protect"] = False

def check_round_middle(fighter_a, fighter_b):
    check_print_hp(fighter_a, fighter_b)
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
            fi["curr_hp"] = max(0, fi["curr_hp"])
            print(fi["name"] + " is hurt by poison!")
            print("HP is now: " + str(fi["curr_hp"]))
        elif fi["status"] == "burn":
            fi["curr_hp"] -= int(fi["hp"] * moves.damage_multiplier_burn)
        fi["curr_hp"] = max(0, fi["curr_hp"])




def do_battle(fighter_a, fighter_b, suspend_code):
    #print("suspend code: " + str(suspend_code))
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
    # Suspend/Battle Code: 0: The battle is normal.
    #                      1: Fighter A did a recall.
    #                      2: Fighter B did a recall.
    #
    # Return Values: [0: Exit code string
    #                 1: Team that will swap
    #                 2: Index of the swap-in fighter
    #                 3: If the user does a U-Turn: True   - End of the round.
    #                                               False: - Suspend, so keep the round going.]
    #
    # Check the conditions of the completion of the battle to break ties.
    while (fighter_a["curr_hp"] > 0 and fighter_b["curr_hp"] > 0):

        print()
        check_round_start(fighter_a, fighter_b)

        turn_priority = {"a" : 0, "b" : 0}
        recall_next_f = [-1, -1] # Keeps track of fighter selection if a user decides to recall.

        if suspend_code == 0:
            for index, fi in enumerate([fighter_a, fighter_b]):
                selected_move = ""
                sufficient_pp = False
                while (selected_move not in fi["moves"] and sufficient_pp is False):
                    # Print the moves.
                    print("\nTurn: " + fi["name"] + "\n", end="")
                    longest_name_length = len(max(fi["moves"], key=len))
                    longest_type_length = 0
                    for m in fi["moves"]:
                        new_type_len = len(specific_moves.moves_dict[m]["type"])
                        longest_type_length = max(longest_type_length, new_type_len)
                    for num, m in enumerate(fi["moves"]):
                        pad0 = " " * (longest_name_length - len(m))
                        pad1 = " " + (" " * (longest_type_length - len(specific_moves.moves_dict[m]["type"])))
                        tv = (str(num), case_change(m), pad0, specific_moves.moves_dict[m]["type"].title(), pad1, str(fi["pps"][num]))
                        f_string_moves = f"{tv[0]}: {tv[1]} {tv[2]}-- {tv[3]}{tv[4]} -- PP: {tv[5]}"
                        print(f_string_moves)

                    selected_move = input("\n")

                    # Recall
                    if selected_move == "recall":
                        recall_return = moves.recall(fi, True)
                        if recall_return == fi["team_slot"]:
                            continue
                        if recall_return not in [-1, fi["team_slot"]]:
                            recall_next_f[index] = recall_return
                            break

                    # TODO: Make sure PP check is correct.
                    elif selected_move.isdigit() and int(selected_move) in range(0, 4):
                        #valid_switch = True
                        if fi["pps"][int(selected_move)] == 0:
                            print("\nThere's no PP left for this move!\n")
                        else:
                            fi["pps"][int(selected_move)] -= 1
                            selected_move = fi["moves"][int(selected_move)]
                    is_info_call = bool(re.search(r'[0-3][i,info,d,desc,description]', selected_move))
                    if is_info_call:
                        print("\n" + specific_moves.moves_dict[fi["moves"][int(selected_move[0])]]["description"] + "\n")
                fi["queued_move"] = selected_move
                print("[   " + case_change(selected_move) + "   ]\n")
                if selected_move != "protect": # Refresh Protect Counter
                    fi["count_protect"] = 0
                try:
                    pri = int(specific_moves.moves_dict[fi["queued_move"]]["priority"])
                except KeyError:
                    pri = 0
                if index == 0:
                    turn_priority["a"] = pri
                else:
                    turn_priority["b"] = pri

            goes_first = 'a'

            # Priority Check and Speed Check
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


            # Recall / Suspend System v2
            if fighter_a["queued_move"] == "recall" and fighter_b["queued_move"] != "recall":
                print("returning with recall for 1")
                return "recall", 1, [int(recall_next_f[0]), 10], True # not actually using these True statements for this context; it's more for u-turn currently.
            if fighter_b["queued_move"] == "recall" and fighter_a["queued_move"] != "recall":
                print("returning with recall for 2")
                return "recall", 2, [10, int(recall_next_f[1])], True
            if fighter_a["queued_move"] == "recall" and fighter_b["queued_move"] == "recall":
                print("Both recalled!")
                return "recall", 3, [int(recall_next_f[0]), int(recall_next_f[1])], True

            print("- - - - - - - - -")

            # U-turn Compatible System v2
            u_turn_a = False
            u_turn_b = False
            special_code = [10, 10] # 10 is 'blank', since 0 is used for team index.
            if goes_first == 'a':
                #print("A first")
                battle_over, special_code[0] = do_turn(fighter_a, fighter_a["queued_move"], fighter_b)
                #print("special code -> A moved first: " + str(special_code))
                if special_code[0] in range(len(fighter_a["team"])):
                    u_turn_a = True
                if not battle_over:
                    battle_over, special_code[1] = do_turn(fighter_b, fighter_b["queued_move"], fighter_a)
                #    print("special code -> B moved second: " + str(special_code[1]))
                    if special_code[1] in range(len(fighter_b["team"])):
                        u_turn_b = True
            else:
                #print("B first")
                battle_over, special_code[1] = do_turn(fighter_b, fighter_b["queued_move"], fighter_a)
                #print("special code -> B moved first: " + str(special_code[1]))
                if special_code[1] in range(len(fighter_b["team"])):
                    u_turn_b = True
                if not battle_over:
                    battle_over, special_code[0] = do_turn(fighter_a, fighter_a["queued_move"], fighter_b)
                #    print("special code -> A moved second: " + str(special_code[0]))
                    if special_code[0] in range(len(fighter_a["team"])):
                        u_turn_a = True

            if u_turn_a and u_turn_b:
                #print("u-turn: both")
                return "u-turn", 3, special_code, False
            if u_turn_a:
                #print("u-turn A")
                return "u-turn", 1, special_code, False
            if u_turn_b:
                #print("u-turn B")
                return "u-turn", 2, special_code, False

            # TODO: Make sure that rough skin/soup burst hits the u-turning opponent. Currently, soup burst does not.

        # Recall/Suspend System Continuation
        if suspend_code in [1, 2]:
            if suspend_code == 1:
                do_turn(fighter_b, fighter_b["queued_move"], fighter_a)
            elif suspend_code == 2:
                do_turn(fighter_a, fighter_a["queued_move"], fighter_b)

            #suspend_code = 0
            print("Doing normal return completion.")
            return "completion after suspend", 0, [0]

        if (fighter_a["curr_hp"] > 0 and fighter_b["curr_hp"] > 0):
            check_round_end(fighter_a, fighter_b)

        for fm in [fighter_a, fighter_b]:
            fm["previous_move"] = fm["queued_move"]
        print("- - - - - - - - -")


    if fighter_a["curr_hp"] > 0 >= fighter_b["curr_hp"]:
        moves.ability_check_category_5(fighter_a, fighter_a["queued_move"], fighter_b)
        fighter_b["koed"] = True
        return "fighter_b_defeated", 0, [0]
    if fighter_b["curr_hp"] > 0 >= fighter_a["curr_hp"]:
        moves.ability_check_category_5(fighter_b, fighter_b["queued_move"], fighter_a)
        fighter_a["koed"] = True
        return "fighter_a_defeated", 0, [0]
    if fighter_a["curr_hp"] == fighter_b["curr_hp"] == 0: # Tie Breakers
        for index,f in enumerate([fighter_a, fighter_b]):
            if "sd_counter_win" in f and f["sd_counter_win"] is True:
                f["defeated_opponent"] = True
                f[1-index]["koed"] = True
        return "fighter_both_defeated", 0, [0]
    return "normal_completion", 0, [0]


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

def reset_stat_changes(fr):
    for s in [
        "curr_stage_phy_att",
        "curr_stage_phy_def",
        "curr_stage_spec_att",
        "curr_stage_spec_def",
        "curr_stage_speed",
        "curr_stage_accuracy",
        "curr_stage_evasion"
    ]:
        fr[s] = 0

def debug_print(fighter_a, fighter_b):
    print("\n-- Fighters' Stats: --\n")
    for f in [fighter_a, fighter_b]:
        print(f["name"])
        for s in ["hp","phy_att","phy_def","spec_att","spec_def","speed"]:
            print(s + ": " + str(f[s]))
        print()


def select_next_fighter(team, team_key, longest_name_length):
    print(f"Select the next fighter for {team_key}:")
    while not valid_pick:
        for i, f in enumerate(team):
            fighter_name = f["name"]
            pad_length = 3 + longest_name_length - len(fighter_name)
            suffix = "" if not f["koed"] else "  " * pad_length + " [Fainted]"
            print(f"{i}: {fighter_name}{suffix}")
        choice = input("\n")
        try:
            if not team[int(choice)]["koed"]:
                next_fighter[team_key] = int(choice)
                break
            print(f"{choice}: {team[int(choice)]['name']} has fainted!")
        except (IndexError, ValueError):
            print("Fighter selection is not valid.")

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
            fighter_temp["koed"] = False
            determine_stats(fighter_temp)
            # Start the moves with the pp from the moves dict.
            # If the move is undefined, give it 10 pp.
            for pp, mv in zip(["pp_0", "pp_1", "pp_2", "pp_3"], \
                              ["move_0", "move_1", "move_2", "move_3"]):
                try:
                    fighter_temp[pp] = specific_moves.moves_dict[fighter_temp[mv]]["pp"]
                except KeyError:
                    fighter_temp[pp] = 10

            fighter_temp["moves"] = \
                [fighter_temp["move_0"],fighter_temp["move_1"],\
                 fighter_temp["move_2"],fighter_temp["move_3"]]
            fighter_temp["pps"] = \
                [fighter_temp["pp_0"],fighter_temp["pp_1"],\
                 fighter_temp["pp_2"],fighter_temp["pp_3"]]

            roster[fighter_temp["id"]] = fighter_temp
        if fighter_data:
            BATTLE_CAN_HAPPEN = True

if BATTLE_CAN_HAPPEN:

    team_a = [roster[1].copy(), roster[2].copy(), roster[3].copy()]

    for slot,f in enumerate(team_a):
        f["team_slot"] = slot
        f["team"] = team_a

    team_b = [roster[4].copy(), roster[5].copy(), roster[6].copy()]

    for slot,f in enumerate(team_b):
        f["team_slot"] = slot
        f["team"] = team_b

    select_a = 99999
    select_b = 99999

    defeated_a = False
    defeated_b = False
    valid_pick = False

    longest_name_length_a = 0
    longest_name_length_b = 0
    for f in team_a:
        if len(f["name"]) > longest_name_length_a:
            longest_name_a = f["name"]
    for f in team_b:
        if len(f["name"]) > longest_name_length_b:
            longest_name_b = f["name"]

    return_code = "none"
    next_fighter = {"team_a" : 0, "team_b" : 0}


    while defeated_a is False and defeated_b is False:
        if return_code in ["fighter_a_defeated", "both_defeated"]:
            select_next_fighter(team_a, "team_a", longest_name_length_a)
        if return_code in ["fighter_b_defeated", "both_defeated"]:
            select_next_fighter(team_b, "team_b", longest_name_length_b)

        if return_code in ["keep_a", "keep_both"]: # This is going to be redundant. Make it compact later.
            for index, f in enumerate(team_b):
                if f["koed"] is False:
                    next_fighter["team_b"] = index
        if return_code in ["keep_b", "keep_both"]:
            for index, f in enumerate(team_a):
                if f["koed"] is False:
                    next_fighter["team_a"] = index

        print("Fight: <<< " + \
              team_a[next_fighter["team_a"]]["name"] + " vs " + team_b[next_fighter["team_b"]]["name"] + " >>>")
        check_print_hp(team_a[next_fighter["team_a"]], team_b[next_fighter["team_b"]])
        battle_output = do_battle(team_a[next_fighter["team_a"]], team_b[next_fighter["team_b"]], 0)
        #print("checking battle_output[0]: " + battle_output[0])
        #print("battle output: ")
        #for p in battle_output:
        #    print(p, end= "   ")


        if battle_output[0] == "recall" or battle_output[0] == "u-turn":
            if battle_output[1] == 1:
                reset_stat_changes(team_a[next_fighter["team_a"]])
                next_fighter["team_a"] = battle_output[2][0]
                print("Team A sent out " + team_a[int(battle_output[2][0])]["name"] + "!")
                if battle_output[0] != "u-turn":
                    do_battle(team_a[next_fighter["team_a"]], team_b[next_fighter["team_b"]], battle_output[1])
            elif battle_output[1] == 2:
                reset_stat_changes(team_b[next_fighter["team_b"]])
                next_fighter["team_b"] = battle_output[2][1]
                print("Team B sent out " + team_b[int(battle_output[2][1])]["name"] + "!")
                if battle_output[0] != "u-turn":
                    do_battle(team_a[next_fighter["team_a"]], team_b[next_fighter["team_b"]], battle_output[1])
            elif battle_output[1] == 3:
                print("Both u-turned!!!")
                reset_stat_changes(team_a[next_fighter["team_a"]])
                reset_stat_changes(team_a[next_fighter["team_b"]])
                next_fighter["team_a"] = battle_output[2][0]
                next_fighter["team_b"] = battle_output[2][1]
                print("Team A sent out " + team_a[int(battle_output[2][0])]["name"] + "!")
                print("Team B sent out " + team_b[int(battle_output[2][1])]["name"] + "!")
                do_battle(team_a[next_fighter["team_a"]], team_b[next_fighter["team_b"]], 0)


        if all(f["koed"] for f in team_a):
            print("Player 2 wins!")
            break
        if all(f["koed"] for f in team_b):
            print("Player 1 wins!")
            break


        return_code = battle_output[0]

    print("\n--------------\n")