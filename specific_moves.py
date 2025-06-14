# Attack/Contact Moves

def move_heat_crash(user, target):
    # Python match-case doesn't have fall-through,
    # so there are no explicit breaks.
    power = 0
    print("Target weight: " + str(target["weight"]))
    print("User weight: " + str(user["weight"]))
    percentage = target["weight"] / user["weight"]
    print("Percentage: " + str(percentage))
    match percentage:
        case _ if percentage > 0.5:
            power = 40
        case _ if percentage >= .3335:
            power = 60
        case _ if percentage >= 25.01:
            power = 80
        case _ if percentage >= 20.01:
            power = 100
        case _:  #percentage <= 20.0
            power = 120
    return power

def move_sucker_punch(target):
    return target["queued_move"] in ["physical", "special"]

def move_scrape(user, target):
    print("scrape activated!")
    if user["ability"] != "corrosion":
        if "poison" not in target["types"] and "steel" not in target["types"]:
            print("It had no effect!")
    else:
        target["status"].append("poisoned")
        print(target["name"] + " is poisoned!")
        user["curr_stage_spec_att"] += 2
        user["curr_stage_phys_def"] -= 1
        user["curr_stage_spec_def"] -= 1
        print(user["name"] + "'s special attack sharply raised!")
        print(user["name"] + "'s defense and special defense decreased!")

# Status Moves


#def autotomize():
#