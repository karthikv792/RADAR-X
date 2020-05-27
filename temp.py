from foil_parser import get_actions, clean_user_foil, extract_vocab, extract_actions

user_foil = "why address media transport chief deploy bulldozers firechief adminfire byeng instead of deploy small engines fire chief scottsdale fire lake and block road transportchief lake marketplace"
# user_foil = clean_user_foil(user_foil, vocab)
# user_foil = " ".join(user_foil)
why, why_not = get_actions(user_foil, current_plan=set())
print("Why ", why)
print("Why Not ", why_not)
# import re
# regex = []
# patterns = dict()
#
# patterns[re.compile("address.*transport.*")] = "ADDRESS_MEDIA_TRANSPORTCHIEF"
# patterns[re.compile("address.*medi.*")] = "ADDRESS_MEDIA_MEDICHIEF"
# patterns[re.compile("address.*fire.*")] = "ADDRESS_MEDIA_FIRECHIEF"
# patterns[re.compile("address.*police.*")] = "ADDRESS_MEDIA_POLICECHIEF"
#
# patterns[re.compile("attend.*")] = "ATTEND_CASUALTIES_MEDICHIEF_BYENG"
# patterns[re.compile("att.*")] = "ATTEND_CASUALTIES_MEDICHIEF_BYENG"
# patterns[re.compile("at.*casual.*")] = "ATTEND_CASUALTIES_MEDICHIEF_BYENG"
#
# patterns[re.compile("search.*")] = "SEARCH_CASUALTIES_FIRECHIEF_BYENG"
#
# patterns[re.compile("barricade.*byeng")] = "BARRICADE_FIRECHIEF_BYENG"
# patterns[re.compile("barricade.*rural")] = "BARRICADE_FIRECHIEF_RURAL"
# patterns[re.compile("barricade.*market.*")] = "BARRICADE_FIRECHIEF_MARKETPLACE"
# patterns[re.compile("barricade.*mill")] = "BARRICADE_FIRECHIEF_MILL"
# patterns[re.compile("barricade.*lake")] = "BARRICADE_FIRECHIEF_LAKE"
#
# patterns[re.compile("extinguish.*")] = "EXTINGUISH_BIG_FIRE_FIRECHIEF_BYENG"
#
# places = ["byeng", "rural", "marketplace", "mill", "lake"]
# for place1 in places:
#     for place2 in places:
#         action = "EVACUATE_POLICECHIEF_" + place1.upper() + "_" + place2.upper()
#         regexp = "evacuate\s*(police\s*(chief)?)?\s*" + place1 + r"\s*" + place2
#         patterns[re.compile(regexp)] = action
#
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*byeng")] = "PREPARE_EVACUATION_POLICECHIEF_BYENG"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*rural")] = "PREPARE_EVACUATION_POLICECHIEF_RURAL"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*market")] = "PREPARE_EVACUATION_POLICECHIEF_MARKETPLACE"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*mill")] = "PREPARE_EVACUATION_POLICECHIEF_MILL"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*lake")] = "PREPARE_EVACUATION_POLICECHIEF_LAKE"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*joseph")] = "PREPARE_EVACUATION_POLICECHIEF_JOSEPH"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*lukes")] = "PREPARE_EVACUATION_POLICECHIEF_LUKES"
#
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*phoenix\s*(fire)?")] = "PREPARE_EVACUATION_POLICECHIEF_PHXFIRE"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*scotts(dale)?\s*(fire)?")] = "PREPARE_EVACUATION_POLICECHIEF_SCOTTSFIRE"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*mesa\s*(fire)?")] = "PREPARE_EVACUATION_POLICECHIEF_MESAFIRE"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*admin\s*(fire)?")] = "PREPARE_EVACUATION_POLICECHIEF_ADMINFIRE"
#
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*sub\s*(station)?")] = "PREPARE_EVACUATION_POLICECHIEF_SUBSTATION"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*court\s*(station)?")] = "PREPARE_EVACUATION_POLICECHIEF_COURTSTATION"
# patterns[re.compile("(prepare|evacuation)\s*(police\s*(chief)?)?\s*apache\s*(station)?")] = "PREPARE_EVACUATION_POLICECHIEF_APACHESTATION"
#
# for pattern, action in patterns.items():
#     matches = pattern.finditer(user_foil)
#     for match in matches:
#         print(pattern," ", action)

def update_costs_for_foil(actions, cost):
    domain_new = open("pr-domain-new.pddl", "w")
    with open("pr-domain.pddl", "r") as domain:
            action_found = False
            for line in domain:
                for action in actions:
                    if action in line:
                        action_found = True
                        break

                if action_found == True and "total-cost" in line:
                    words = line.split(" ")
                    new_line = words[0] + " " + words[1]
                    domain_new.write(new_line + " " + str(cost)+")\n")
                    action_found = False
                else:
                    domain_new.write(line)

    domain_new.close()

update_costs_for_foil(why_not, -1000)


