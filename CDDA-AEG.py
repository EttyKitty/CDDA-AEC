import json
import os
import sys
from tomark import Tomark
import re

os.chdir(sys.path[0])
material_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'materials.json')
armor_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json/items/armor')
limbs_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'body_parts.json')
# material_data_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'materials.json'))
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
            average_coverage = []
            average_encumbrance = []
            average_resist = []
            armor_object_dict = {}
            if "copy-from" in armor_object:
                continue
            if "name" in armor_object:
                armor_name = armor_object["name"]
                if isinstance(armor_name, str):
                    # print()
                    # print("name: " + armor_name)
                    armor_object_dict["Name"] = str(armor_name)
                elif "str" in armor_name:
                    # print()
                    # print("name: " + armor_name["str"])
                    armor_object_dict["Name"] = armor_name["str"]
                elif "str_sp" in armor_name:
                    # print()
                    # print("name: " + armor_name["str_sp"])
                    armor_object_dict["Name"] = armor_name["str_sp"]
            if "armor" in armor_object:
                armor_info = armor_object["armor"]

                for body_part in armor_info:
                    if "coverage" in body_part:
                        if "specifically_covers" in body_part:
                            for specificall_part in body_part["specifically_covers"]:
                                if pattern.search(specificall_part):
                                    continue
                                for limb_object in limbs_json:
                                    if "max_coverage" in limb_object:
                                        if limb_object["id"] == specificall_part:
                                            coverage_multiplayer = (limb_object["max_coverage"] / 100)
                                            # print(body_part["coverage"])
                                            # print(coverage_multiplayer)
                                            average_coverage.append(body_part["coverage"] * coverage_multiplayer)
                                            average_coverage = round(sum(average_coverage) / len(average_coverage))
                                            # print("average coverage: " + str(average_coverage))
                                            armor_object_dict["Coverage"] = str(average_coverage)
                                            average_coverage = []
                        else:
                            average_coverage.append(body_part["coverage"])
                            average_coverage = round(sum(average_coverage) / len(average_coverage))
                            # print("average coverage: " + str(average_coverage))
                            armor_object_dict["average_coverage"] = str(average_coverage)
                            average_coverage = []
                    # else:
                    #     average_coverage.append(0)
                    #     armor_object_dict["Coverage"] = str(average_coverage)
                    #     average_coverage = []

                for body_part in armor_info:
                    if "encumbrance" in body_part:
                        if isinstance(body_part["encumbrance"], int):
                            average_encumbrance.append(body_part["encumbrance"])
                        else:
                            average_encumbrance.append(body_part["encumbrance"][0])
                    else:
                        average_encumbrance.append(0)
                if average_encumbrance != []:
                    average_encumbrance = round(sum(average_encumbrance) / len(average_encumbrance))
                    # print("average encumbrance: " + str(average_encumbrance))
                    armor_object_dict["Encumbrance"] = str(average_encumbrance)
                    if "flags" in armor_object:
                        for flag in armor_object["flags"]:
                            if flag == "VARSIZE":
                                armor_object_dict.update({"Encumbrance": str(round(average_encumbrance / 2))})

            if "material_thickness" in armor_object:
                material_thickness = armor_object["material_thickness"]
                # print("material thickness: " + str(material_thickness))
                if "material" in armor_object:
                    i = 0
                    for material in armor_object["material"]:
                        for material_object in material_json:
                            if "id" in material_object:
                                if material_object["id"] == material:
                                    i += 1
                                    # print("material " + str(i) + ":" + str(material))
                                    if "bash_resist" in material_object:
                                        # print("bash resist: " + str(material_object["bash_resist"]))
                                        average_resist.append(material_object["bash_resist"])
                                    if "cut_resist" in material_object:
                                        # print("cut resist: " + str(material_object["cut_resist"]))
                                        average_resist.append(material_object["cut_resist"])
                    if average_resist != []:
                        average_resist = (sum(average_resist) / len(average_resist)) * material_thickness
                        # print("average resist: " + str(average_resist))
                        armor_object_dict["Resist"] = str(round(average_resist, 1))
            if "Coverage" in armor_object_dict and "Encumbrance" in armor_object_dict and "Resist" in armor_object_dict:
                armor_efficiency = (int(armor_object_dict["Coverage"]) / 10) * float(armor_object_dict["Resist"])
                if "Encumbrance" in armor_object_dict and armor_object_dict["Encumbrance"] != "0":
                    armor_efficiency = (armor_efficiency / int(armor_object_dict["Encumbrance"]))
                # print("armor efficiency: " + str(round(armor_efficiency, 1)))
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
                    for body_part in armor_info:
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
# print(armor_efficiency_list)
markdown_list = []
markdown_list.append(armor_efficiency_list_torso)
markdown_list.append(armor_efficiency_list_head)
markdown_list.append(armor_efficiency_list_eyes)
markdown_list.append(armor_efficiency_list_mouth)
markdown_list.append(armor_efficiency_list_arms)
markdown_list.append(armor_efficiency_list_hands)
markdown_list.append(armor_efficiency_list_legs)
markdown_list.append(armor_efficiency_list_feet)

original_stdout = sys.stdout  # Save a reference to the original standard output
with open('markdow_output.txt', 'w+') as f:
    for lists in markdown_list:
        sys.stdout = f  # Change the standard output to the file we created.
        markdow_output = Tomark.table(lists)
        print("##")
        print("<details>")
        print("  <summary>Spoiler</summary>")
        print()
        print(markdow_output)
        print("</details>")
        print()
        sys.stdout = original_stdout  # Reset the standard output to its original value
