# parse_ifc.py

import ifcopenshell

def parse_ifc_to_json(ifc_path):
    model = ifcopenshell.open(ifc_path)

    elements = {
        "walls": [],
        "doors": [],
        "rooms": []
    }

    # TODO: Extract and transform relevant IFC elements into simplified JSON format
    print("IFC file loaded. Found:")
    print(" - Walls:", len(model.by_type("IfcWall")))
    print(" - Doors:", len(model.by_type("IfcDoor")))
    print(" - Spaces:", len(model.by_type("IfcSpace")))

    return elements  # return empty for now