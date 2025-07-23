from parse_ifc import parse_ifc_to_json
from agent import graph_assistant

if __name__ == "__main__":
    bim_data = parse_ifc_to_json("data/sample.ifc")
    prompt = input("Enter your graph query: ")
    graph, summary = graph_assistant(prompt, bim_data)
    print("\nSummary: \n", summary) # show me all walls
    # 2D Visualization /output_graph.png