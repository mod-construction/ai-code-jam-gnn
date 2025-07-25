import networkx as nx

def execute_query(state):
    G = state["graph"]
    query = state["generated_query"]

    relation = query.get("relation")
    filters = query.get("filter", {})
    allowed_names = query.get("include_node_names", []) or []
    allowed_categories = query.get("category", []) or []  # corrected key name

    # Normalize to lowercase
    allowed_names = [name.lower() for name in allowed_names]
    allowed_categories = [cat.lower() for cat in allowed_categories]

    filtered_nodes = []
    for node_id, attrs in G.nodes(data=True):
        node_name = attrs.get("name", "").lower()
        node_category = attrs.get("category", "").lower()

        name_match = any(name in node_name for name in allowed_names) if allowed_names else False
        category_match = node_category in allowed_categories if allowed_categories else False

        if name_match or category_match:
            attr_match = True
            for k, v in filters.items():
                val = attrs.get(k)
                if val is None:
                    val = attrs.get("props", {}).get(k)
                if val is None or str(val).lower() != str(v).lower():
                    attr_match = False
                    break

            if attr_match:
                filtered_nodes.append(node_id)


    filtered_edges = []
    for u, v, edge_attrs in G.edges(data=True):
        if edge_attrs.get("relation") == relation:
            if u in filtered_nodes and v in filtered_nodes:
                filtered_edges.append((u, v, edge_attrs))

    print("\n -- Result of the query execution -- ")
    print("Filtered nodes:", filtered_nodes)
    print("Filtered edges:", filtered_edges)

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
