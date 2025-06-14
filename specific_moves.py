# Helper Functions
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

# Attack/Contact Moves


def move_analyzed_impale(power, user, target):
    user["curr_hp"] -= int(user["max_hp"] / 16)
    if target["status"] == "poisoned":
        print("analyzed_impale() is boosted with poison!")
        return 2 * power
    else:
        return power

def move_heat_crash(user, target):
    # Python match-case doesn't have fall-through,
    # so there are no explicit breaks.
    percentage = target["weight"] / user["weight"]
    match percentage:
        case _ if percentage > 0.5:
            return 40
        case _ if percentage >= .3335:
            return 60
        case _ if percentage >= 25.01:
            return 80
        case _ if percentage >= 20.01:
            return 100
        case _:  #percentage <= 20.0
            return 120

def move_sucker_punch(target):
    return target["queued_move"] in ["physical", "special"]

def move_scrape(user, target):
    poison_reason = check_can_be_poisoned(user, target)
    if poison_reason == 0:
        target["status"] = "poison"
        print(target["name"] + " is poisoned!")
    if poison_reason == 3:
        print(target["name"] + " is already poisoned!")
    if poison_reason in [0,3]:
        user["curr_stage_spec_att"] += 2
        user["curr_stage_phy_def"] -= 1
        user["curr_stage_spec_def"] -= 1
        print(user["name"] + "'s special attack sharply raised!")
        print(user["name"] + "'s defense and special defense decreased!")
    if poison_reason in [1,2]:
        print("scrape() failed!")

def move_toxic(user, target):
    # Toxic specifically sets the badly poison level to 1.
    if check_can_be_poisoned(user, target) != 0:
        print("It had no effect!")
    else:
        target["status"] = "poison"
        target["badly_poison_level"] = 1
        print(target["name"] + " is badly poisoned!")

# Status Moves


#def autotomize():
#