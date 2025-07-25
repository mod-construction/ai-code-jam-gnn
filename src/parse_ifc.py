
from __future__ import annotations
from typing import Dict, List
import json
import numpy as np
import ifcopenshell
import ifcopenshell.util.shape as ushape
import ifcopenshell.geom as geom
import random

from utils import measure_latency

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

FIRE_RATING_PSETS = {
    "IfcWall": "Pset_WallCommon",
    "IfcSlab": "Pset_SlabCommon",
    "IfcDoor": "Pset_DoorCommon",
  
}

_SETTINGS = geom.settings()

def _add_mock_relationships(
    elements: Dict[str, List[dict]],
    adj_range: tuple[int, int] = (1, 3),      # how many “adjacents” IDs per wall
    cont_range: tuple[int, int] = (1, 2),     # how many “containeds” IDs per wall
) -> None:
    """
    add:
      * adjacent_to  -> list[str]
      * contained_in -> list[str]

    IDs are drawn randomly from all other elements except for the wall itself.
    """
    # flat list of ALL global_ids
    all_ids: list[str] = [
        item["global_id"]
        for cat in elements.values()
        for item in cat
    ]

    for wall in elements["walls"]:
        # pool without the wall’s own ID
        pool = [gid for gid in all_ids if gid != wall["global_id"]]
        if not pool:        # skip if the IFC only had one element
            continue

        wall["adjacent_to"] = random.sample(
            pool, k=min(random.randint(*adj_range), len(pool))
        )
        wall["contained_in"] = random.sample(
            pool, k=min(random.randint(*cont_range), len(pool))
        )

@measure_latency
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


            #if ifcwall or ifcslab (for now) add "load_bearing" bool propery ro "props"
            props = {}
            lb_pset_name = LOAD_BEARING_PSETS.get(ifc_type)
            if lb_pset_name:
                psets = ifcopenshell.util.element.get_psets(obj) or {}
                props["load_bearing"] = bool(psets.get(lb_pset_name, {}).get("LoadBearing", False))

            fr_pset_name = FIRE_RATING_PSETS.get(ifc_type)
            if fr_pset_name:
                psets = ifcopenshell.util.element.get_psets(obj) or {}
                props["fire_rating"] = psets.get(fr_pset_name, {}).get("FireRating", None)



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



    #-------------------------------------------mock relationships--------------------------------------------------------
    _add_mock_relationships(elements)


    return elements



# out_path = "data/sample_elements.json"
# elements = parse_ifc_to_json("data/sample.ifc")
# with open(out_path, "w", encoding="utf-8") as f:
#     json.dump(elements, f, indent=2)   
# print(f"Wrote {out_path}")
