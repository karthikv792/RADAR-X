from foil_parser import get_actions

user_foil = "why deploy rescuers fire chief phoenix fire brickyard and address media transport chief instead of deploy small engines fire chief scotts fire lake and address media medi chief"
why, why_not = get_actions(user_foil, current_plan=set())
print("Why ", why)
print("Why Not ", why_not)