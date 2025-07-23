import networkx as nx
import json

def build_context_graph(bim_data, include_types=None):
    G = nx.Graph()

    for element in bim_data:
        node_id = element["id"]

        node_attrs = {
            "id": node_id,
            "type": element.get("type"),
            "level": element.get("level"),
            "position": element.get("position", {}),
            "dimensions": element.get("dimensions", {}),
            "metadata": element.get("metadata", {}),
        }

        G.add_node(node_id, **node_attrs)

    for element in bim_data:
        source_id = element["id"]
        relations = element.get("relations", {})

        for rel_type, targets in relations.items():
            for target_id in targets:
                if G.has_node(target_id):
                    if not G.has_edge(source_id, target_id):
                        G.add_edge(source_id, target_id, relation=rel_type)
                else:
                    print(f"⚠️ Warning: Target node '{target_id}' not found for relation '{rel_type}' from '{source_id}'.")

    return G

if __name__ == "__main__":
    bim_data_path = "sample_data.json"
    import os
    print(os.path.abspath("sample_data.json"))  
    with open(bim_data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("Data loaded succesffuly!")
    G = build_context_graph(data)
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print("Sample node:", list(G.nodes(data=True))[0])
    print("Sample edge:", list(G.edges(data=True))[0])