import csv
import os.path
import specific_moves

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

damage_multiplier_poison = 1/8
damage_multiplier_badly_poison = 1/16
damage_multiplier_burn = 1/16
class Moves:
    moves_dict = {}
    abilities_dict = {}
    types_dict = {}
    def __init__(self):
        if os.path.isfile("all_moves.csv"):
            with open("all_moves.csv", newline='', encoding="UTF-8") as move_file:
                reader_obj_moves = csv.reader(move_file)
                for row in reader_obj_moves:
                    move_temp = {
                        "type"                     : row[1],
                        "category"                 : row[2],
                        "pp"                       : int(row[3]),
                        "power"                    : int(row[4]),
                        "accuracy"                 : int(row[5]),
                        "priority"                 : int(row[6]),
                        "instances"                : int(row[7]),
                        "effect_function"          : row[8],
                        "attr_makes_contact"       : bool(row[9]),
                        "attr_affected_by_protect" : bool(row[10]),
                        "description"              : row[11]
                    }
                    self.moves_dict[row[0]] = move_temp
            #print(self.moves_dict)

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
                    self.types_dict[row[0]] = type_temp
                    #print(self.types_dict)

        if os.path.isfile("all_abilities.csv"):
            with open("all_abilities.csv", newline='', encoding="UTF-8") as type_file:
                reader_obj_abilities = csv.reader(type_file)
                for row in reader_obj_abilities:
                    ability_temp = {
                        "function": row[1],
                        "description" : row[2]
                    }
                    self.abilities_dict[row[0]] = ability_temp

    def change_stage_main_stat(self, target, stat, change):
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


    def type_interaction(self, move_type, target_type):
        # Returns pair: 0: Interaction Value, 1: Interaction Message
        try:
            value = self.types_dict[move_type][target_type]
        except KeyError:
            value = 1
        message = ""
        if value == 2:
            message = "It's super effective!"
        elif value == 0.5:
            message = "It's not very effective..."
        elif value == 0:
            message = "It had no effect."
        return value, message

    def calculate_attack_damage(self, move, user, target):
        move_power = self.moves_dict[move]["power"]

        # Irregular Effect
        move_function = self.moves_dict[move]["effect_function"]
        #print("move function:" + move_function)
        if move_function != "none":
            if move_function == "move_heat_crash()":
                move_power = specific_moves.move_heat_crash(user, target)
            elif move_function == "move_sucker_punch()":
                result = specific_moves.move_sucker_punch(target)
                if not result:
                    print("Sucker Punch failed!")
                    return 0
            elif move_function == "move_scrape()":
                specific_moves.move_scrape(user, target)
                return 0
            elif move_function == "move_analyzed_impale()":
                move_power = specific_moves.move_analyzed_impale(self.moves_dict["analyzed_impale()"]["power"], user, target)


        # Offense and Defense Stats
        if self.moves_dict[move]["category"] == "physical":
            attack_stat = user["phy_att"] * stage_multiplier_main_stats_dict[float(user["curr_stage_phy_att"])]
            def_stat = target["phy_def"] * stage_multiplier_main_stats_dict[float(target["curr_stage_phy_def"])]
        else:
            attack_stat = user["spec_att"] * stage_multiplier_main_stats_dict[float(user["curr_stage_spec_att"])]
            def_stat = target["spec_def"] * stage_multiplier_main_stats_dict[float(target["curr_stage_spec_def"])]


        damage = (((user["level"] * 2) / 5) + 2) * move_power
        
        damage = damage * (attack_stat/def_stat)
        damage = damage / 50


        # User Burned
        if user["status"] == "burn" and self.moves_dict[move]["category"] == "physical":
            damage = damage * 0.5
            print("Damage reduced because " + user["name"] + " is burned!")

        #STAB
        if self.moves_dict[move]["type"] in user["types"]:
            damage = damage * 1.5

        # Type Effectiveness
        type_multiplier = 1.0
        for t in target["types"]:
            #print("      type damage multiplier for " + t + ": " + self.types_dict[self.moves_dict[move]["type"]][t])
            type_multiplier = type_multiplier * float(self.types_dict[self.moves_dict[move]["type"]][t])
        #print("      total type multiplier: " + str(type_multiplier))
        damage = damage * type_multiplier

        match type_multiplier:
            case 2.0:
                print("It's super effective!")
            case 0.5:
                print("It's not very effective...")
            case 0:
                print("It had no effect!")

        return int(damage)
