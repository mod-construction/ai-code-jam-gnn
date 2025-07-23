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
}

# use world coordinates so our bounding box is in global space
_SETTINGS = geom.settings()
_SETTINGS.set(_SETTINGS.USE_WORLD_COORDS, True)


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
            # buiild shape
            shape = geom.create_shape(_SETTINGS, obj)

            #get vertices
            flat_verts = shape.geometry.verts
            verts = np.array(flat_verts, dtype=float).reshape(-1, 3)

            # bbox corners
            bbox_min, bbox_max = ushape.get_bbox(verts)

            # get name
            name =  getattr(obj, "Name", None)     

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
                }
            })

    # print summary
    print(f"IFC file loaded: {ifc_path}")
    for key, items in elements.items():
        print(f" - {key}: {len(items)}")

    return elements

#print(parse_ifc_to_json(ifc_path="data/sample.ifc"))
