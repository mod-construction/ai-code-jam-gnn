import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import networkx as nx

from langgraph.graph import StateGraph, END

from agents.evaluate_query_success import evaluate_query_success
from agents.execute_query import execute_query
from agents.parse_user_intent import parse_user_intent
from agents.summarize_answer import summarize_answer
from agents.conditional_edge import route_after_repair, route_decision
from agents.visualize_agent import visualize_agent
from agents.repair_agent import repair_agent
from typing import TypedDict, List, Dict, Any

from utils import measure_latency

def extract_unique_names(graph):

    import re

    unique_names = {
        attrs.get("name")
        for _, attrs in graph.nodes(data=True)
        if "name" in attrs
    }

    unique_names.discard(None)

    filtered_names = [
        name for name in unique_names
        if not name.startswith("Type") 
    ]

    filtered_names = sorted(filtered_names)

    print(f"Filtered down to {len(filtered_names)} meaningful 'name' values:")
    for name in filtered_names:
        print("-", name)
    return filtered_names

@measure_latency
def graph_assistant(prompt, graph):
    extract_names = extract_unique_names(graph)
    print("List of unique names: ",extract_unique_names)

    initial_state = {
        "query": prompt,
        "graph": graph,
        "schema": {
            "categories": ["doors", "rooms", "walls", "slabs"],
            "node_names": extract_names,
            "edge_types": ["adjacent_to", "contained_in"],
            "node_attributes": {
                "type": "string",     
                "name": "string",
                "bounding_box": {
                    "xmin": "float",
                    "ymin": "float",
                    "zmin": "float",
                    "xmax": "float",
                    "ymax": "float",
                    "zmax": "float"
                },
                "properties": {
                    "load_bearing": "boolean",
                    "fire_rating": "number"
                }
            }
        },
        "attempt": 0
    }


    class AgentState(TypedDict):
        query: str
        graph: nx.Graph
        schema: Dict[str, Any]  
        user_intent: Dict[str, Any]
        generated_query: Dict[str, Any]
        query_result: Dict[str, Any]
        attempt: int
        error_explanation: str
        summary_text: str
        visualization_path: str

    workflow = StateGraph(AgentState)

    workflow.add_node("generate_query_agent", parse_user_intent)
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("evaluate_agent", evaluate_query_success)
    workflow.add_node("summarize_agent", summarize_answer)
    workflow.add_node("repair_query_agent", repair_agent)
    workflow.add_node("visualize_result", visualize_agent)

    workflow.set_entry_point("generate_query_agent")

    workflow.add_edge("generate_query_agent", "execute_query")
    workflow.add_edge("execute_query", "evaluate_agent")

    workflow.add_conditional_edges("evaluate_agent", route_decision, {
        "Pass": "summarize_agent",
        "Fail": "repair_query_agent",
    })

    workflow.add_conditional_edges("repair_query_agent", route_after_repair, {
        "Pass": "execute_query",
        "Fail": "repair_query_agent",
        "GiveUp": "summarize_agent"
    })

    workflow.add_edge("summarize_agent", "visualize_result")
    workflow.add_edge("visualize_result", END)

    app = workflow.compile()
    final_state = app.invoke(initial_state)

    graph_obj = app.get_graph()
    png_data = graph_obj.draw_mermaid_png()
    with open("Agentic_workflow.png", "wb") as f:
        f.write(png_data)

    if final_state.get("query_result"):
        print(f"Visualizing result nodes: {final_state['query_result']}")

    return final_state, final_state.get("summary_text", "No summary generated.")
    
if __name__ == "__main__":
    import time
    start_time = time.time()
    # bim_data_path = "src/sample_data.json"
    # with open(bim_data_path, 'r', encoding='utf-8') as file:
    #     data = json.load(file)
    #     print("Data loaded succesffuly!")

    prompt = "Show me all walls that are load bearing"
    # show me all walls that has dry wall material
    print("\n Starting agentic workflow...")
    final_state, summary = graph_assistant(prompt)

    print("\n Summary of result:")
    print(summary)
    end_time = time.time()
    latency = int(end_time - start_time)
    print(f"Latency: {latency} seconds")
