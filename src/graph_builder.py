import networkx as nx
from topologicpy import Topology
from topologicpy import Cluster
from topologicpy.Graph import Graph
from topologicpy.Vertex import Vertex
from topologicpy.Cell import Cell
from topologicpy.Face import Face
from topologicpy.Shell import Shell
from topologicpy.Dictionary import Dictionary

def build_context_graph(bim_data, graph):
    G = nx.Graph()

    # Step 1: Flatten bim_data for easy lookup by global_id
    global_id_to_elem = {}
    for category, items in bim_data.items():
        for elem in items:
            global_id = elem["global_id"]
            elem.setdefault("adjacent_to", set())
            elem.setdefault("contained_in", set())
            global_id_to_elem[global_id] = elem
            G.add_node(global_id, **elem)

    # Step 2: Extract vertices from Topologic graph
    vertices = Graph.Vertices(graph)
    edges = Graph.Edges(graph)

    # Step 3: Map Topologic vertices to global_ids
    vertex_to_id = {}
    for v in vertices:
        d = Topology.Topology.Dictionary(v)
        keys= d.Keys()
        gid = Dictionary.ValueAtKey(d, "IFC_global_id")
        if gid in global_id_to_elem:
            vertex_to_id[v] = gid


    # Step 4: Process edges to build NetworkX graph and update adjacency
    for edge in edges:
        verts = Topology.Topology.Vertices(edge)
        if len(verts) != 2:
            continue
        v1, v2 = verts
        id1 = vertex_to_id.get(v1)
        id2 = vertex_to_id.get(v2)

        if id1 and id2:
            G.add_edge(id1, id2)
            global_id_to_elem[id1]["adjacent_to"].add(id2)
            global_id_to_elem[id2]["adjacent_to"].add(id1)
    

    return G, bim_data

def load_ifc_topology(ifc_path, return_type="cells", verbose=True):

    try:
        graph = Graph.ByIFCPath(str(ifc_path), includeTypes=["IfcWall", "IfcSlab", "IfcSpace"],
        transferDictionaries=True)
        
        if verbose:
            print(f"[✓] IFC loaded from: {ifc_path}")
            print(f"[→] Topology type: {type(graph)}")
        
        return  graph

    except Exception as e:
        print(f"[✗] Failed to load IFC: {e}")
        return None
