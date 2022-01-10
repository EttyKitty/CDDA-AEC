import json
import os
import sys
from tomark import Tomark


material_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'materials.json')
# material_data_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json', 'materials.json'))
f1 = open(material_data_path)
material_json = json.load(f1)
armor_efficiency_list = []
armor_data_path = os.path.join(os.path.dirname(__file__), '..', 'cdda/data/json/items/armor')
for root, dirs, files in os.walk(armor_data_path):
    for file in files:
        f2 = open(os.path.join(root, file), "r")
        armor_json = json.load(f2)
        for armor_object in armor_json:
            average_coverage = []
            average_encumbrance = []
            average_resist = []
            armor_object_dict = {}
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
                        average_coverage.append(body_part["coverage"])
                if average_coverage != []:
                    average_coverage = round(sum(average_coverage) / len(average_coverage))
                    # print("average coverage: " + str(average_coverage))
                    armor_object_dict["Average Coverage"] = str(round(average_coverage))

                for body_part in armor_info:
                    if "encumbrance" in body_part:
                        if isinstance(body_part["encumbrance"], int):
                            average_encumbrance.append(body_part["encumbrance"])
                        else:
                            average_encumbrance.append(body_part["encumbrance"][0])
                if average_encumbrance != []:
                    average_encumbrance = round(sum(average_encumbrance) / len(average_encumbrance))
                    # print("average encumbrance: " + str(average_encumbrance))
                    armor_object_dict["Average Encumbrance"] = str(round(average_encumbrance))

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
                        armor_object_dict["Average Resist"] = str(round(average_resist, 1))
            if average_coverage != [] and average_encumbrance != [] and average_resist != []:
                armor_efficiency = average_coverage * average_resist
                if average_encumbrance != 0:
                    armor_efficiency = (armor_efficiency / average_encumbrance)
                # print("armor efficiency: " + str(round(armor_efficiency, 1)))
                armor_object_dict["Armor Efficiency"] = str(round(armor_efficiency, 1))
                armor_efficiency_list.append(armor_object_dict)

        f2.close()
    f1.close()
# print(armor_efficiency_list)
markdown = Tomark.table(armor_efficiency_list)
original_stdout = sys.stdout # Save a reference to the original standard output
with open('markdow-output.txt', 'w') as f:
    sys.stdout = f # Change the standard output to the file we created.
    print(markdown)
    sys.stdout = original_stdout # Reset the standard output to its original value