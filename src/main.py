from parse_ifc import parse_ifc_to_json
from agent import graph_assistant
from graph_builder import build_context_graph, load_ifc_topology
import networkx as nx

if __name__ == "__main__":
    bim_data = parse_ifc_to_json("data/sample.ifc")
    topology_graph = load_ifc_topology("data/sample.ifc")
    graph, bim_data_v2 = build_context_graph(bim_data, topology_graph)

    print("Nodes:")
    print(graph.nodes(data=True)) 
        
    prompt = input("Enter your graph query: ")
    _, summary = graph_assistant(prompt, graph)
    print("Summary text: ",summary)