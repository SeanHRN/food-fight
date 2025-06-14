def check_print_hp(fighterA, fighterB):
    # Copy of the function to avoid cyclical import
    print(fighterA["name"] + " HP: " + str(fighterA["curr_hp"]))
    print(fighterB["name"] + " HP: " + str(fighterB["curr_hp"]))

def check_soup_burst(a, b):
    if a["ability"] == "soup burst" and a["curr_hp"] <= (a["max_hp"]/2) and a["state_ability_activated"] is False:
        a["state_ability_activated"] = True
        print(a["name"] + " bursted soup!")
        print(b["name"] + " is burned!")
        print(a["name"] + "'s stats sharply decreased!")
        b["curr_hp"] -= 80
        b["status"].append("burned")
        check_print_hp(a, b)
