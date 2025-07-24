import topologicpy
from topologicpy.Vertex import Vertex
from topologicpy.Face import Face
from topologicpy.Shell import Shell
from topologicpy.Cell import Cell
from topologicpy.Topology import Topology
import networkx as nx

def build_context_graph(bim_data, include_types=None):
    cells, ids = extract_elements(bim_data)
    adjacency = build_adjacency_dict(cells, ids)
    return update_bim_data_with_adjacency(bim_data, adjacency)

def extract_elements(bim_data):
    cells = []
    ids = []

    for category, elements in bim_data.items():
        for elem in elements:
            bbox = elem["BoundingBox"]
            cell = make_cell_from_bbox(bbox)
            cells.append(cell)
            ids.append(elem["global_id"])

    return cells, ids

def build_adjacency_dict(cells, ids):
    adjacency_dict = {id_: [] for id_ in ids}

    for i, cell1 in enumerate(cells):
        for j, cell2 in enumerate(cells):
            if i == j:
                continue
            shared = Topology.SharedTopologies(cell1, cell2)
            if any(shared.get(k) for k in ["faces", "edges", "vertices", "wires"]):
                adjacency_dict[ids[i]].append(ids[j])
    print("Adjacency Graph:", adjacency_dict)
    return adjacency_dict

def update_bim_data_with_adjacency(bim_data, adjacency_dict):
    for category, elements in bim_data.items():
        for elem in elements:
            elem_id = elem["global_id"]
            elem["adjacent_to"] = adjacency_dict.get(elem_id, [])
    return bim_data

def make_cell_from_bbox(bbox):
    xmin, ymin, zmin = bbox["xmin"], bbox["ymin"], bbox["zmin"]
    xmax, ymax, zmax = bbox["xmax"], bbox["ymax"], bbox["zmax"]

    v = [
        Vertex.ByCoordinates(xmin, ymin, zmin),  # 0
        Vertex.ByCoordinates(xmax, ymin, zmin),  # 1
        Vertex.ByCoordinates(xmax, ymax, zmin),  # 2
        Vertex.ByCoordinates(xmin, ymax, zmin),  # 3
        Vertex.ByCoordinates(xmin, ymin, zmax),  # 4
        Vertex.ByCoordinates(xmax, ymin, zmax),  # 5
        Vertex.ByCoordinates(xmax, ymax, zmax),  # 6
        Vertex.ByCoordinates(xmin, ymax, zmax)   # 7
    ]

    bottom = Face.ByVertices([v[0], v[1], v[2], v[3]])
    top    = Face.ByVertices([v[4], v[5], v[6], v[7]])
    front  = Face.ByVertices([v[0], v[1], v[5], v[4]])
    right  = Face.ByVertices([v[1], v[2], v[6], v[5]])
    back   = Face.ByVertices([v[2], v[3], v[7], v[6]])
    left   = Face.ByVertices([v[3], v[0], v[4], v[7]])

    cell = Cell.ByFaces([bottom, top, front, right, back, left])
    volume = Cell.Volume(cell)
    return cell
