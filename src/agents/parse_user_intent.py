from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from agents.common_tools.define_llm import define_llm
import json



class UserIntent(BaseModel):
    category: List[str] = Field(..., description="Category of nodes to include (e.g., room, Wall)")
    include_node_names: List[str] = Field(..., description="Names of nodes to include (e.g., Curtain wall door, Foundation beam)")
    filter_node_attributes: Dict[str, str] = Field(default_factory=dict, description="Filters on node attributes like load_bearing, fire_rating")
    relations: List[str] = Field(..., description="Type of relationship to use (e.g., contained_in, adjacent_to)")


def parse_user_intent(state):
    model = define_llm()
    query = state["query"]
    schema = state["schema"]

    print(f"\n[parse_user_intent] User query: {query}")
    print(f"[parse_user_intent] Available node names: {schema['node_names']}")
    print(f"[parse_user_intent] Available categories: {schema['categories']}")
    print(f"[parse_user_intent] Available edge types: {schema['edge_types']}")
    print(f"[parse_user_intent] Available node attributes: {schema['node_attributes']}")


    parser = PydanticOutputParser(pydantic_object=UserIntent)

    prompt_template = """
    You are a BIM graph assistant. Your task is to extract structured query intent from a user's prompt.

    ONLY use the provided node types and edge types when interpreting the user's query.

    Available schema: {schema}

    Format your output strictly as follows (no extra keys, no explanation):
    {format_instructions}

    User prompt:
    {query}
    """

    prompt = PromptTemplate(
        input_variables=["query", "schema"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=prompt_template
    )

    chain = prompt | model | parser


    try:
        result = chain.invoke({
            "query": query,
            "schema": schema
        })
        
        generated_query = {
            "category": result.category,
            "include_node_names": result.include_node_names,
            "filter": result.filter_node_attributes,
            "relation": result.relations[0] if result.relations else "",
            "explanation": "Parsed directly from user intent"
        }

        print("[parse_user_intent] Parsed user intent:")
        print(f"   - categories: {generated_query['category']}")
        print(f"   - include_node_names: {generated_query['include_node_names']}")
        print(f"   - filter: {generated_query['filter']}")
        print(f"   - relation: {generated_query['relation']}")

        return {
            "generated_query": generated_query,
        
        }

    except Exception as e:
        return {
            "user_intent": {},
            "error": str(e)
        }

if __name__ == "__main__":
    sample_state = {
        "query": "Find all rooms on level 2 connected by doors.",
        "schema" : {
        "node_types": ["Wall", "Room", "Slab"],
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
            }
        }
        },
    }

    print("Testing `parse_user_intent` agent...\n")
    print("User Query:", sample_state["query"])
    print("Schema:")
    print("  Node types:", sample_state["schema"]["node_types"])
    print("  Edge types:", sample_state["schema"]["edge_types"])
    print("-" * 60)

    result = parse_user_intent(sample_state)

    print("Result: ", result)