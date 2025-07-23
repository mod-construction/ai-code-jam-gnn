import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from graph_builder import build_context_graph
import graphviz
import networkx as nx
import json

from langgraph.graph import StateGraph, END

from agents.evaluate_query_success import evaluate_query_success
from agents.execute_query import execute_query
from agents.parse_user_intent import parse_user_intent
from agents.summarize_answer import summarize_answer
from agents.conditional_edge import route_after_repair, route_decision
from agents.visualize_agent import visualize_agent
from agents.repair_agent import repair_agent
from typing import TypedDict, List, Dict, Any


def graph_assistant(prompt, bim_data):
    # Build full context graph
    graph = build_context_graph(bim_data)

    initial_state = {
        "query": prompt,
        "graph": graph,
        "schema" : {
        "node_types": ["Wall", "Room", "Slab","Door"],
        "edge_types": ["adjacent_to", "contained_in"],
        "node_attributes": {
            "name": "string",
            "BoundingBox": {
                "xmin": "float",
                "ymin": "float",
                "zmin": "float",
                "xmax": "float",
                "ymax": "float",
                "zmax": "float"
            },
            "props": {"load_bearing": "boolean"  
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
    bim_data_path = "src/sample_data.json"
    with open(bim_data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("Data loaded succesffuly!")

    prompt = "Show me all walls"
    # show me all walls that has dry wall material
    print("\n Starting agentic workflow...")
    final_state, summary = graph_assistant(prompt, data)

    print("\n Summary of result:")
    print(summary)
    end_time = time.time()
    latency = int(end_time - start_time)
    print(f"Latency: {latency} seconds")
