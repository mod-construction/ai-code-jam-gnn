# # parse_ifc.py

# import ifcopenshell

# def parse_ifc_to_json(ifc_path):
#     model = ifcopenshell.open(ifc_path)

#     elements = {
#         "walls": [],
#         "doors": [],
#         "rooms": []
#     }

#     # TODO: Extract and transform relevant IFC elements into simplified JSON format
#     print("IFC file loaded. Found:")
#     print(" - Walls:", len(model.by_type("IfcWall")))
#     print(" - Doors:", len(model.by_type("IfcDoor")))
#     print(" - Spaces:", len(model.by_type("IfcSpace")))

#     return elements  # return empty for now

# parse_ifc.py

from __future__ import annotations
from typing import Dict, List

import numpy as np
import ifcopenshell
import ifcopenshell.util.shape as ushape
import ifcopenshell.geom as geom

# ——————————————————————————————————————————————————————————————
# our types
TYPE_TO_KEY = {
    "IfcWall": "walls",
    "IfcSlab": "slabs",
    "IfcSpace": "rooms",
    "IfcDoor": "doors"
}

LOAD_BEARING_PSETS = {
    "IfcWall": "Pset_WallCommon",
    "IfcSlab": "Pset_SlabCommon",
    
}

_SETTINGS = geom.settings()

def parse_ifc_to_json(ifc_path):
    """
    Reads an IFC file and returns a dict:
    {
      "walls": [ {global_id, name, BoundingBox}, … ],
      "slabs": [ … ],
      "rooms": [ … ]
    }
    """
    model = ifcopenshell.open(str(ifc_path))
    elements: Dict[str, List[dict]] = {key: [] for key in TYPE_TO_KEY.values()}

    for ifc_type, out_key in TYPE_TO_KEY.items():
        for obj in model.by_type(ifc_type):
            # build shape
            shape = geom.create_shape(_SETTINGS, obj)

            # get vertices
            verts = ushape.get_element_vertices(obj, shape.geometry)

            # bbox corners
            bbox_min, bbox_max = ushape.get_bbox(verts)

            # get name
            name =  getattr(obj, "Name", None)    



            #if ifcwall or ifcslab (for now) add "load_bearing" bool propery to "props"
            props = {}
            pset_name = LOAD_BEARING_PSETS.get(ifc_type)
            if pset_name:
                psets = ifcopenshell.util.element.get_psets(obj) or {}
                props["load_bearing"] = bool(psets.get(pset_name, {}).get("LoadBearing", False))



            # append
            elements[out_key].append({
                "global_id": obj.GlobalId,
                "name": name,
                "BoundingBox": {
                    "xmin": float(bbox_min[0]),
                    "ymin": float(bbox_min[1]),
                    "zmin": float(bbox_min[2]),
                    "xmax": float(bbox_max[0]),
                    "ymax": float(bbox_max[1]),
                    "zmax": float(bbox_max[2]),
                },
                "props": props
            })


    # print summary
    print(f"IFC file loaded: {ifc_path}")
    for key, items in elements.items():
        print(f" - {key}: {len(items)}")

    return elements

print(parse_ifc_to_json(ifc_path="data/sample.ifc"))
