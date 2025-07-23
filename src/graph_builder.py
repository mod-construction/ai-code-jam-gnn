import networkx as nx
import json

def build_context_graph(bim_data):
    G = nx.Graph()

    for category, elements in bim_data.items():
        for element in elements:
            node_id = element["global_id"]
            node_attrs = {
                "id": node_id,
                "type": category,
                "name": element.get("name"),
                "bounding_box": element.get("BoundingBox", {}),
                "properties": element.get("props", {})
            }
            G.add_node(node_id, **node_attrs)

    for category, elements in bim_data.items():
        for element in elements:
            source_id = element["global_id"]

            for rel_type in ["adjacent_to", "contained_in"]:
                targets = element.get(rel_type, [])
                if not isinstance(targets, list):
                    continue 

                for target_id in targets:
                    if G.has_node(target_id):
                        G.add_edge(source_id, target_id, relation=rel_type)
                    else:
                        print(f"⚠️ Warning: '{source_id}' references unknown target '{target_id}' via '{rel_type}'")

    return G


if __name__ == "__main__":
    import os

    bim_data_path = "sample_data.json"
    print("Reading from:", os.path.abspath(bim_data_path))

    with open(bim_data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("✅ Data loaded successfully!")

    G = build_context_graph(data)

    print(f"📊 Graph Stats — Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print("🔹 Sample Node:", list(G.nodes(data=True))[0])
    if G.edges:
        print("🔸 Sample Edge:", list(G.edges(data=True))[0])
    else:
        print("No edges found.")
