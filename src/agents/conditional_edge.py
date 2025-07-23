def route_decision(state):
    if state.get("decision") == "pass":
        return "Pass"
    elif state.get("attempt", 0) < 2:
        return "Fail"
    else:
        print("Max attempts reached, skipping repair.")
        return "GiveUp"

def route_after_repair(state):
    attempts = state.get("attempt", 0)

    if state.get("query_result") and state["query_result"] != "None":
        return "Pass"  

    if attempts >= 2:
        print("Query repair failed after 2 attempts.")
        return "GiveUp"

    state["attempt"] = attempts + 1
    return "Fail"
