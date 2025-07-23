from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from agents.common_tools.define_llm import define_llm
from collections import Counter
import networkx as nx
import json


class Summary(BaseModel):
    summary_text: str = Field(..., description="Natural language explanation of the graph query result")

def summarize_answer(state):
    model = define_llm()

    query_result = state["query_result"]
    nodes = query_result.get("nodes", [])
    edges = query_result.get("edges") or []

    G = state["graph"]
    node_types = [G.nodes[n].get("type", "Unknown") for n in nodes]
    node_type_counts = Counter(node_types)

    edge_type_counts = Counter()
    if edges:
        edge_types = [edge_data.get("relation", "unknown") for _, _, edge_data in edges]
        edge_type_counts = Counter(edge_types)


    parser = PydanticOutputParser(pydantic_object=Summary)

    prompt_template = """
    You are a BIM graph assistant. Your job is to summarize a subgraph extracted from a building model.

    Summarize the result using natural language. Mention:
    - How many nodes were found
    - What types of nodes and how many of each
    - How many edges and their types
    - Keep it short and useful (1-3 sentences max)

    Format:
    {format_instructions}

    Node type counts:
    {node_counts}

    Edge type counts:
    {edge_counts}
    """

    prompt = PromptTemplate(
        input_variables=["node_counts", "edge_counts"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=prompt_template
    )

    chain = prompt | model | parser

    try:
        result = chain.invoke({
            "node_counts": json.dumps(dict(node_type_counts)),
            "edge_counts": json.dumps(dict(edge_type_counts))
        })

        return {
            "summary_text": result.summary_text,
        }

    except Exception as e:
        return {
            "summary_text": "Failed to summarize result.",
            "error": str(e)
        }

if __name__ == "__main__":
    G = nx.Graph()
    G.add_node("Room_201", type="window")
    G.add_node("Room_202", type="table")
    G.add_node("Door_A", type="Door")
    G.add_edge("Room_201", "Door_A", relation="next_to")
    G.add_edge("Room_202", "Door_A", relation="connected_by")

    test_state = {
        "graph": G,
        "query_result": {
            "nodes": ["Room_201", "Room_202", "Door_A"],
            "edges": [("Room_201", "Door_A", {"relation": "next_to"}),
                      ("Room_202", "Door_A", {"relation": "connected_by"})]
        }
    }

    print("Running summarization agent...\n")
    result = summarize_answer(test_state)
    print("Summary:", result["summary_text"] if "summary_text" in result else "No summary.")
