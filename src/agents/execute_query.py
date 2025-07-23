import networkx as nx

def execute_query(state):
    G = state["graph"]
    query = state["generated_query"]

    relation = query.get("relation")
    filters = query.get("filter", {})
    allowed_types = query.get("include_node_types", [])

    filtered_nodes = []
    for node_id, attrs in G.nodes(data=True):
        if attrs.get("type") in allowed_types:
            match = all(str(attrs.get(k)) == str(v) for k, v in filters.items())
            if match:
                filtered_nodes.append(node_id)

    filtered_edges = []
    for u, v, edge_attrs in G.edges(data=True):
        if edge_attrs.get("relation") == relation:
            if u in filtered_nodes and v in filtered_nodes:
                filtered_edges.append((u, v, edge_attrs))
    print("\n -- Result of the query execution -- ")
    print("Filtered nodes: ", filtered_nodes)
    print("Filtered edges: ", filtered_edges)
    return {
        "query_result": {
            "nodes": filtered_nodes,
            "edges": filtered_edges,
        },
    }

if __name__ == "__main__":
    G = nx.Graph()
    G.add_node("Room_101", type="Room", level="2")
    G.add_node("Room_102", type="Room", level="2")
    G.add_node("Room_103", type="Room", level="1")
    G.add_edge("Room_101", "Room_102", relation="connected_by")
    G.add_edge("Room_101", "Room_103", relation="connected_by")

    state = {
        "graph": G,
        "generated_query": {
            "relation": "connected_by",
            "filter": {"level": "2"},
            "include_node_types": ["Room"],
            "explanation": "Test case"
        }
    }

    result = execute_query(state)
    print("Filtered Nodes:", result["query_result"]["nodes"])
    print("Filtered Edges:", result["query_result"]["edges"])
