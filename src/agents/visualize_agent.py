import networkx as nx
import matplotlib.pyplot as plt

def visualize_agent(state):
    G_full = state["graph"]
    result = state.get("query_result", {})
    node_ids = result.get("nodes", [])
    edge_tuples = result.get("edges", [])

    H = nx.Graph()

    for node_id in node_ids:
        if node_id in G_full:
            H.add_node(node_id, **G_full.nodes[node_id])

    for u, v, attrs in edge_tuples:
        if u in H and v in H:
            H.add_edge(u, v, **attrs)

    pos = nx.spring_layout(H, seed=42)  
    def clean_label(node_id):
        return node_id.replace("$", "﹩")  

    node_labels = {
        n: f"{clean_label(n)}\n({H.nodes[n].get('type', '')})" for n in H.nodes()}
    edge_labels = {(u, v): d.get("relation", "") for u, v, d in H.edges(data=True)}

    plt.figure(figsize=(8, 6))
    nx.draw(H, pos, with_labels=True, labels=node_labels, node_size=2000, node_color="skyblue", font_size=10)
    nx.draw_networkx_edge_labels(H, pos, edge_labels=edge_labels, font_color='red')
    plt.title("Filtered BIM Context Subgraph")

    image_path = "Output_graph.png"
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    print(f"📸 Saved graph visualization to: {image_path}")

    return {
        "visualization_path": image_path
    }

if __name__ == "__main__":
    G = nx.Graph()
    G.add_node("Room_1", type="Room")
    G.add_node("Room_2", type="Room")
    G.add_node("Door_A", type="Door")
    G.add_edge("Room_1", "Door_A", relation="connected_by")
    G.add_edge("Room_2", "Door_A", relation="connected_by")

    test_state = {
        "graph": G,
        "query_result": {
            "nodes": ["Room_1", "Room_2", "Door_A"],
            "edges": [("Room_1", "Door_A", {"relation": "connected_by"}),
                      ("Room_2", "Door_A", {"relation": "connected_by"})]
        }
    }

    visualize_agent(test_state)
