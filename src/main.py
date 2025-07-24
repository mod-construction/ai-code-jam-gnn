from parse_ifc import parse_ifc_to_json
from agent import graph_assistant
from graph_builder import build_context_graph, load_ifc_topology

if __name__ == "__main__":
    bim_data = parse_ifc_to_json("data/sample.ifc")
    topology_graph = load_ifc_topology("data/sample.ifc")
    graph = build_context_graph(bim_data, topology_graph)
    prompt = input("Enter your graph query: ")
    graph, summary = graph_assistant(prompt, bim_data)
    print(summary)