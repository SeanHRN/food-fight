import itertools
import os.path
import random
import sys
import csv
from moves import Moves
import moves
import abilities
sys.path.append(os.getcwd())


### Use the CSV to make the character dictionary
move_control = Moves()
roster = {}

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
    print()
    print("--------------")
    print(user["name"] + " used " + case_change(move) + "!")
    print()

    if not move in moves.specific_moves.moves_dict:
        print("\"" + move + "\"" + " was not found!")
        return False

    elif moves.specific_moves.moves_dict[move]["category"] == "status":
        move_control.do_status_move(user, move)

    # Uses a loop so that multi-hit moves can work.
    elif moves.specific_moves.moves_dict[move]["category"] != "status":
        if target["state_protect"] is False:
            for _ in itertools.repeat(None, moves.specific_moves.moves_dict[move]["instances"]):
                move_control.calculate_interaction(move, user, target)
                if check_round_middle(user, target):    # If someone is out of HP, return true. If not, keep going.
                    return True
        else:
            print(target["name"] + " protected itself!")
    return False

def check_print_hp(fighterA, fighterB):
    l = [fighterA, fighterB]
    for fighter in l:
        print(fighter["name"] + " HP: " + str(fighter["curr_hp"]))

def check_print_status(fighterA, fighterB):
    l = [fighterA, fighterB]
    for fighter in l:
        if fighter["status"]:
            print("Status effect(s) on " + fighter["name"] + ": ", end="")
            for s in fighter["status"]:
                print(s)

def check_round_start(fighterA, fighterB):
    #print("check round start")
    l = [fighterA, fighterB]
    for fighter in l:
        fighter["state_protect"] = False


def check_ability(fighterA, fighterB):
    l = [fighterA, fighterB]
    for index,fighter in enumerate(l):
        abilities.check_soup_burst(fighter, l[1-index])


def check_round_middle(fighterA, fighterB):
    check_print_hp(fighterA, fighterB)
    check_ability(fighterA, fighterB)

    if fighterA["curr_hp"] <= 0 or fighterB["curr_hp"] <= 0:
        print("The fight is over.\n\n")

    return fighterA["curr_hp"] <= 0 or fighterB["curr_hp"] <= 0

def check_round_end(fighterA, fighterB):
    l = [fighterA, fighterB]
    for fighter in l:
        if fighter["status"] == "poison":
            if fighter["badly_poisoned"]:
                fighter["curr_hp"] -= int(fighter["max_hp"] * \
                    float(fighter["badly_poisoned_level"]) * moves.damage_multiplier_badly_poison)
                fighter["badly_poisoned_level"] += moves.damage_multiplier_badly_poison
            else:
                fighter["curr_hp"] -= int(fighter["max_hp"] * moves.damage_multiplier_poison)
            print(fighter["name"] + " is hurt by poison!")
            print("HP is now: " + str(fighter["curr_hp"]))
        elif fighter["status"] == "burn":
            fighter["curr_hp"] -= int(fighter["max_hp"] * moves.damage_multiplier_burn)



def do_battle(fighterA, fighterB):
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
    while (fighterA["curr_hp"] > 0 and fighterB["curr_hp"] > 0):

        print()
        check_round_start(fighterA, fighterB)

        moveA = ""
        moveB = ""
        while moveA not in fighterA["moves"]:
            print("Choose Fighter 1 Move: ", end=" ")
            for num, move in enumerate(fighterA["moves"]):
                print(str(num) + ": " + case_change(move) + "  ", end="")
            moveA = input("\n")
            if moveA.isdigit() and int(moveA) in range(4):
                moveA = fighterA["moves"][int(moveA)]
        fighterA["queued_move"] = moveA
        print("[   " + case_change(moveA) + "   ]")
        print()
        while moveB not in fighterB["moves"]:
            print("Choose Fighter 2 Move: ", end=" ")
            for num, move in enumerate(fighterB["moves"]):
                print(str(num) + ": " + case_change(move) + "  ", end="")
            moveB = input("\n")
            if moveB.isdigit() and int(moveB) in range(4):
                moveB = fighterB["moves"][int(moveB)]
        fighterB["queued_move"] = moveB
        print("[   " + case_change(moveB) + "   ]")

        try:
            priority_a = int(moves.specific_moves.moves_dict[moveA]["priority"])
        except KeyError:
            print("Priority for " + case_change(moveA) + " not found. Using default.")
            priority_a = 0
        try:
            priority_b = int(moves.specific_moves.moves_dict[moveB]["priority"])
        except KeyError:
            print("Priority for " + case_change(moveB) + " not found. Using default.")
            priority_b = 0
        goes_first = 'a'

        #print("priority_a: " + str(priority_a))
        #print("priority_b: " + str(priority_b))
        #print("speed_a: " + str(fighterA["speed"]))
        #print("speed_b: " + str(fighterB["speed"]))
        # Priority Check
        if priority_a < priority_b:
            goes_first = 'b'
        if priority_a == priority_b:
            if fighterA["speed"] < fighterB["speed"]:
                goes_first = 'b'
            elif fighterA["speed"] == fighterB["speed"]:
                if random.random() < 0.5:
                    goes_first = 'b'

        # Speed Check
        if goes_first == 'a':
            if not do_turn(fighterA, moveA, fighterB):
                do_turn(fighterB, moveB, fighterA)
        else:
            if not do_turn(fighterB, moveB, fighterA):
                do_turn(fighterA, moveA, fighterB)

        if (fighterA["curr_hp"] > 0 and fighterB["curr_hp"] > 0):
            check_round_end(fighterA, fighterB)


BATTLE_CAN_HAPPEN = False
if os.path.isfile("fighters.csv"):
    with open("fighters.csv", newline='') as fighter_file:
        reader_obj = csv.reader(fighter_file)

        for row in reader_obj:
            fighter_temp = {   # the id, row[0], is just the key.
                "name" : row[1],
                "trainer" : row[2],
                "types" : row[3].split('/'),
                "hp" : int(row[4]),
                "phy_att" : int(row[5]),
                "phy_def" : int(row[6]),
                "spec_att" : int(row[7]),
                "spec_def" : int(row[8]),
                "speed" : int(row[9]),
                "ability" : row[10].lower(),
                "curr_stage_phy_att" : 0,
                "curr_stage_phy_def" : 0,
                "curr_stage_spec_att" : 0,
                "curr_stage_spec_def" : 0,
                "curr_stage_speed" : 0,
                "state_protect" : False,
                "state_ability_activated" : False,
                "weight" : float(row[15]),
                "status" : "none",
                "badly_poisoned_level" : 0,
                "badly_poisoned" : False,
                "confused" : False,
                "infatuated" : False,
                "queued_move" : "blank",
                "level" : 100,
                "iv_hp" : 31,
                "iv_phy_att" : 31,
                "iv_phy_def" : 31,
                "iv_spec_att" : 31,
                "iv_spec_def" : 31,
                "iv_speed" : 31,
                "ev_hp" : 0,
                "ev_phy_att" : 0,
                "ev_phy_def" : 0,
                "ev_spec_att" : 0,
                "ev_spec_def" : 0,
                "ev_speed" : 0,
            }
            if fighter_temp["name"].lower() != "shedinja":
                fighter_temp["max_hp"] = 2 * fighter_temp["hp"] + fighter_temp["iv_hp"] + (fighter_temp["ev_hp"]/4)
                fighter_temp["max_hp"] = fighter_temp["max_hp"] * fighter_temp["level"]
                fighter_temp["max_hp"] = fighter_temp["max_hp"] / 100
                fighter_temp["max_hp"] = fighter_temp["max_hp"] + fighter_temp["level"] + 10
                fighter_temp["curr_hp"] = int(fighter_temp["max_hp"])

            fighter_temp["moves"] = [row[11], row[12], row[13], row[14]]

            roster[row[0]] = fighter_temp
        if reader_obj:
                BATTLE_CAN_HAPPEN = True


if BATTLE_CAN_HAPPEN:
    char_a = roster["1"]
    char_b = roster["2"]

    print("\n\n--------------\n")

    check_print_hp(char_a, char_b)
    do_battle(char_a, char_b)
    #print(char_a["name"] + " HP: " + str(char_a["curr_hp"]))
    #print(char_b["name"] + " HP: " + str(char_b["curr_hp"]))

    #print(char_a)
    #print(char_b)

    print("\n\n--------------\n")
