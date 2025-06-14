import random

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



### Attack/Contact Moves ###

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
        return [2,0,0]
    return [1,0,0]

def move_sucker_punch(user, target):
    if accuracy_check():
        if target["queued_move"] in ["physical", "special"]:
            return [2,0,0]
        else:
            return [0,0,0]

def move_scrape(user, target):
    if accuracy_check():
        poison_reason = check_can_be_poisoned(user, target)
        if poison_reason == 0:
            target["status"] = "poison"
            print(target["name"] + " is poisoned!")
        elif poison_reason == 3:
            print(target["name"] + " is already poisoned!")
        if poison_reason in [0,3]:
            user["curr_stage_spec_att"] += 2
            user["curr_stage_phy_def"] -= 1
            user["curr_stage_spec_def"] -= 1
            print(user["name"] + "'s special attack sharply raised!")
            print(user["name"] + "'s defense and special defense decreased!")
        elif poison_reason in [1,2]:
            #print("scrape() failed!")
            return[0,0,0]
        return[2,0,0]
    return [1,0,0]

def move_toxic(user, target):
    # Toxic specifically sets the badly poison level to 1.
    if accuracy_check():
        if check_can_be_poisoned(user, target) != 0:
            print("It had no effect!")
        else:
            target["status"] = "poison"
            target["badly_poison_level"] = 1
            print(target["name"] + " is badly poisoned!")
        return [3,0,0]
    return [1,0,0]

# Status Moves


#def autotomize():
#