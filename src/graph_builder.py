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
        gid = Dictionary.ValueAtKey(d, "IFC_global_id")
        if gid in global_id_to_elem:
            vertex_to_id[v] = gid


    # Step 4: Process edges to build NetworkX graph and update adjacency
    for edge in edges:
        verts = Topology.Topology.Vertices(edge)
        if len(verts) != 2:
            continue
        v1, v2 = verts
        d1 = Topology.Topology.Dictionary(v1)
        id1 = Dictionary.ValueAtKey(d1, "IFC_global_id")
        d2 = Topology.Topology.Dictionary(v2)
        id2 = Dictionary.ValueAtKey(d2, "IFC_global_id")

        if id1 and id2:
            G.add_edge(id1, id2)
            if not isinstance(global_id_to_elem[id1]["adjacent_to"], set):
                global_id_to_elem[id1]["adjacent_to"] = set(global_id_to_elem[id1]["adjacent_to"])
            if not isinstance(global_id_to_elem[id2]["adjacent_to"], set):
                global_id_to_elem[id2]["adjacent_to"] = set(global_id_to_elem[id2]["adjacent_to"])
            
            global_id_to_elem[id1]["adjacent_to"].add(id2)
            global_id_to_elem[id2]["adjacent_to"].add(id1)

    # Step 5: Ensure adjacent_to sets are updated in bim_data
    for category, items in bim_data.items():
        for elem in items:
            gid = elem["global_id"]
            elem["adjacent_to"] = global_id_to_elem[gid]["adjacent_to"]
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    Graph.Show(graph)
    plot_graph(G)
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

import matplotlib.pyplot as plt

def plot_graph(G, title="Context Graph"):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)

    # Escape dollar signs in labels
    safe_labels = {
        node: data.get("global_id", str(node)).replace('$', r'\$')
        for node, data in G.nodes(data=True)
    }

    nx.draw_networkx_labels(G, pos, labels=safe_labels, font_size=9)

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()