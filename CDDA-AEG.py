import json
import os
import sys
from tomark import Tomark
import re

os.chdir(sys.path[0])
material_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'materials.json')
armor_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json/items/armor')
limbs_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'body_parts.json')
f1 = open(material_data_path)
f3 = open(limbs_data_path)
material_json = json.load(f1)
limbs_json = json.load(f3)
armor_efficiency_list = []
armor_efficiency_list_torso = []
armor_efficiency_list_head = []
armor_efficiency_list_eyes = []
armor_efficiency_list_mouth = []
armor_efficiency_list_arms = []
armor_efficiency_list_hands = []
armor_efficiency_list_legs = []
armor_efficiency_list_feet = []
pattern = re.compile("_l$")

for root, dirs, files in os.walk(armor_data_path):
    for file in files:
        f2 = open(os.path.join(root, file), "r")
        armor_json = json.load(f2)

        for armor_object in armor_json:
            if "name" in armor_object and "armor" in armor_object and "copy-from" not in armor_object and "material" in armor_object:
                armor_name = armor_object["name"]
                armor = armor_object["armor"]
            else:
                continue
            average_coverage = []
            average_coverage_part = []
            average_encumbrance = []
            average_resist = []
            armor_object_dict = {}

            if isinstance(armor_object["name"], str):
                armor_object_dict["Name"] = str(armor_name)
            elif "str" in armor_object["name"]:
                armor_object_dict["Name"] = armor_name["str"]
            elif "str_sp" in armor_object["name"]:
                armor_object_dict["Name"] = armor_name["str_sp"]

            for body_part in armor:
                if "coverage" in body_part and "covers" in body_part:
                    for exact_part in body_part["covers"]:
                        if "specifically_covers" in body_part:
                            for specificall_part in body_part["specifically_covers"]:
                                if pattern.search(specificall_part):
                                    continue
                                for limb_object in limbs_json:
                                    if "max_coverage" in limb_object:
                                        if limb_object["id"] == specificall_part:
                                            coverage_multiplayer = (limb_object["max_coverage"] / 100)
                                            average_coverage_part.append(body_part["coverage"] * coverage_multiplayer)
                        else:
                            average_coverage_part.append(body_part["coverage"])
                        average_coverage.append(sum(average_coverage_part))
                        average_coverage_part = []
            if average_coverage != []:
                average_coverage = round(sum(average_coverage) / len(average_coverage))
                armor_object_dict["Coverage"] = str(average_coverage)
                average_coverage = []

            for body_part in armor:
                if "encumbrance" in body_part:
                    if isinstance(body_part["encumbrance"], int):
                        average_encumbrance.append(body_part["encumbrance"])
                    else:
                        average_encumbrance.append(body_part["encumbrance"][0])
                else:
                    average_encumbrance.append(0)
            if average_encumbrance != []:
                average_encumbrance = round(sum(average_encumbrance) / len(average_encumbrance))
                armor_object_dict["Encumbrance"] = str(average_encumbrance)
                if "flags" in armor_object:
                    for flag in armor_object["flags"]:
                        if flag == "VARSIZE":
                            armor_object_dict.update({"Encumbrance": str(round(average_encumbrance / 2))})

            if "material_thickness" in armor_object:
                material_thickness = armor_object["material_thickness"]
                for material in armor_object["material"]:
                    for material_object in material_json:
                        if "id" in material_object and material_object["id"] == material:
                            if "bash_resist" in material_object:
                                average_resist.append(material_object["bash_resist"])
                            if "cut_resist" in material_object:
                                average_resist.append(material_object["cut_resist"])
                if average_resist != []:
                    average_resist = (sum(average_resist) / len(average_resist)) * material_thickness
                    armor_object_dict["Resist"] = str(round(average_resist, 1))
            else:
                for body_part in armor:
                    if "material" in body_part:
                        for material in body_part["material"]:
                            average_layer_resist = []
                            for material_object in material_json:
                                if "id" in material_object and material_object["id"] == material["type"]:
                                    if "bash_resist" in material_object:
                                        average_layer_resist.append(material_object["bash_resist"])
                                    if "cut_resist" in material_object:
                                        average_layer_resist.append(material_object["cut_resist"])
                            if average_layer_resist != []:
                                material_thickness = material["thickness"]
                                average_layer_resist = (sum(average_layer_resist) / len(average_layer_resist)) * material_thickness
                                average_resist.append(round(average_layer_resist, 1))
                            if material["covered_by_mat"] != 100:
                                layer_coverage = material["covered_by_mat"]
                if average_resist != []:
                    armor_object_dict["Resist"] = str(round((sum(average_resist) * (layer_coverage / 100)), 1))
                    layer_coverage = 100

            if "Coverage" in armor_object_dict and "Encumbrance" in armor_object_dict and "Resist" in armor_object_dict:
                armor_efficiency = (int(armor_object_dict["Coverage"]) / 10) * float(armor_object_dict["Resist"])
                if "Encumbrance" in armor_object_dict and armor_object_dict["Encumbrance"] != "0":
                    armor_efficiency = (armor_efficiency / int(armor_object_dict["Encumbrance"]))
                armor_object_dict["Efficiency"] = str(round(armor_efficiency, 1))
                if "flags" in armor_object:
                    for flag in armor_object["flags"]:
                        if flag == "OUTER":
                            armor_object_dict["Layer"] = "Outer"
                        if flag == "SKINTIGHT":
                            armor_object_dict["Layer"] = "Skintight"
                        if flag == "BELTED":
                            armor_object_dict["Layer"] = "Strapped"
                        if flag == "WAIST":
                            armor_object_dict["Layer"] = "Waist"
                if "Layer" not in armor_object_dict:
                    armor_object_dict["Layer"] = "Normal"
                if armor_object_dict["Efficiency"] != "0.0":
                    for body_part in armor:
                        if "covers" in body_part:
                            for covers in body_part["covers"]:
                                if covers == "torso":
                                    armor_efficiency_list_torso.append(armor_object_dict)
                                if covers == "head":
                                    armor_efficiency_list_head.append(armor_object_dict)
                                if covers == "eyes":
                                    armor_efficiency_list_eyes.append(armor_object_dict)
                                if covers == "mouth":
                                    armor_efficiency_list_mouth.append(armor_object_dict)
                                if covers == "arm_r":
                                    armor_efficiency_list_arms.append(armor_object_dict)
                                if covers == "hand_r":
                                    armor_efficiency_list_hands.append(armor_object_dict)
                                if covers == "leg_r":
                                    armor_efficiency_list_legs.append(armor_object_dict)
                                if covers == "foot_r":
                                    armor_efficiency_list_feet.append(armor_object_dict)

        f2.close()
    f1.close()
markdown_list = []
markdown_list.append(armor_efficiency_list_torso)
markdown_list.append(armor_efficiency_list_head)
markdown_list.append(armor_efficiency_list_eyes)
markdown_list.append(armor_efficiency_list_mouth)
markdown_list.append(armor_efficiency_list_arms)
markdown_list.append(armor_efficiency_list_hands)
markdown_list.append(armor_efficiency_list_legs)
markdown_list.append(armor_efficiency_list_feet)

names = ["Torso", "Head", "Eyes", "Mouth", "Arms", "Hands", "Legs", "Feet"]
i = 0
original_stdout = sys.stdout  # Save a reference to the original standard output
with open('markdow_output.txt', 'w+') as f:
    for lists in markdown_list:
        sys.stdout = f  # Change the standard output to the file we created.
        markdow_output = Tomark.table(lists)
        print("## " + names[i])
        print("<details>")
        print("  <summary>Spoiler</summary>")
        print()
        print(markdow_output)
        print("</details>")
        print()
        i += 1
        sys.stdout = original_stdout  # Reset the standard output to its original value
