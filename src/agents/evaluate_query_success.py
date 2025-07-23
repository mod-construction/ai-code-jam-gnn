from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from agents.common_tools.define_llm import define_llm
import os
import json
from datetime import datetime

LOG_PATH = "logging.json"

class EvaluationResult(BaseModel):
    decision: str = Field(..., description="Must be 'pass' or 'retry'")
    error_explanation: str = Field(default="", description="If retry, provide explanation for failure")

def evaluate_query_success(state):
    model = define_llm("o3")
    query = state["query"]
    user_intent = state.get("user_intent")
    generated_query = state.get("generated_query")
    query_result = state.get("query_result")

    result_summary = f"Nodes: {len(query_result.get('nodes', []))}, Edges: {len(query_result.get('edges', []))}"

    parser = PydanticOutputParser(pydantic_object=EvaluationResult)

    EVALUATION_PROMPT = """
    You are a BIM query validation agent. Your job is to evaluate whether the graph query result correctly answers the user's original prompt.

    Consider:
    - Is the result empty?
    - Does the generated query reflect the user's true intent?
    - Do the node/edge types and filters seem appropriate?

    Respond using:
    {format_instructions}

    User's original query:
    {query}

    Parsed user intent:
    {user_intent}

    Structured graph query:
    {generated_query}

    Query result summary:
    {result_summary}
    """

    prompt = PromptTemplate(
        input_variables=["query", "user_intent", "generated_query", "result_summary"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=EVALUATION_PROMPT
    )

    chain = prompt | model | parser

    try:
        result = chain.invoke({
            "query": query,
            "user_intent": str(user_intent),
            "generated_query": str(generated_query),
            "result_summary": result_summary
        })
        print("\n -- Result of the evaluate node: -- ")
        print(result)
        print("-- result end --")
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "generated_query": generated_query,
            "error_explanation": result.error_explanation,
            "decision": result.decision
        }

    except Exception as e:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "generated_query": generated_query,
            "error_explanation": f"LLM validation error: {str(e)}",
            "decision": "retry"
        }

    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(log_entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        else:
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                json.dump([log_entry], f, indent=2)
    except Exception as log_err:
        print(f"⚠️ Failed to write to log file: {log_err}")

    return {
        "decision": log_entry["decision"],
        "error_explanation": log_entry["error_explanation"],
    }

if __name__ == "__main__":
    import json

    test_state = {
        "query": "Find all rooms on level 2 connected by doors.",
        "user_intent": {
            "include_node_types": ["Room"],
            "filter_node_attributes": {"level": "2"},
            "relations": ["connected_by"]
        },
        "generated_query": {
            "relation": "connected_by",
            "filter": {"level": "2"},
            "include_node_types": ["Room"],
            "explanation": "Query targets Room nodes on level 2 that are connected by doors."
        },
        "query_result": {
            "nodes": ["Room_201", "Room_202"],
            "edges": [("Room_201", "Room_202", {"relation": "connected_by"})]
        }
    }

    print("🧪 Evaluating query success...\n")
    print("User query:", test_state["query"])
    print("Parsed intent:", json.dumps(test_state["user_intent"], indent=2))
    print("Generated query:", json.dumps(test_state["generated_query"], indent=2))
    print(f"Query result: {len(test_state['query_result']['nodes'])} nodes, {len(test_state['query_result']['edges'])} edges")
    print("-" * 60)

    result = evaluate_query_success(test_state)

    if result["decision"] == "pass":
        print("Query evaluation passed!")
    else:
        print("Query evaluation failed:")
        print("Explanation:", result["error_explanation"])
