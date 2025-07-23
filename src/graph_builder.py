import networkx as nx
import json

def build_context_graph(bim_data):
    G = nx.Graph()
    print(" Building context graph...")

    for category, elements in bim_data.items():
        print(f"\n Adding nodes for category: '{category}'")
        for element in elements:
            node_id = element["global_id"]
            node_attrs = {
                "name": element.get("name"),
                "id": node_id,
                "type": category,
                "bounding_box": element.get("BoundingBox", {}),
                "properties": element.get("props", {})
            }
            G.add_node(node_id, **node_attrs)
            print(f"  🟦 Added node: {node_id} ({element.get('name')})")

    print("\n Adding edges...")
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
                        print(f"Edge: {source_id} --[{rel_type}]--> {target_id}")
                    else:
                        print(f"Warning: {source_id} references unknown {target_id} via '{rel_type}'")

    print("\nContext graph built successfully.")
    return G
