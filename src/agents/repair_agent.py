from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from agents.common_tools.define_llm import define_llm
import json

model = define_llm()

class RepairedQuery(BaseModel):
    include_node_types: list[str] = Field(..., description="Relevant node types to include")
    filter: dict = Field(default_factory=dict, description="Filter conditions for node attributes")
    relation: str = Field(..., description="Type of relationship to use")
    explanation: str = Field(..., description="Explanation of what was fixed or improved")

def repair_agent(state):
    query = state.get("query", "")
    previous = state.get("generated_query", {})
    explanation = state.get("error_explanation", "")
    schema = state.get("schema", {})

    parser = PydanticOutputParser(pydantic_object=RepairedQuery)

    prompt_template = """
    You are a BIM graph query repair assistant.

    A previous query failed to return meaningful results. You must improve it based on the user's original question and the error explanation.

    ONLY use the provided node and edge types.

    Original user prompt:
    {query}

    Previous generated query:
    {previous}

    Explanation of failure:
    {explanation}

    Available schema: {schema}

    Fix the query and output in this format:
    {format_instructions}
    """

    prompt = PromptTemplate(
        input_variables=["query", "previous", "explanation", "schema"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=prompt_template
    )

    chain = prompt | model | parser

    try:
        result = chain.invoke({
            "query": query,
            "previous": json.dumps(previous),
            "explanation": explanation,
            "schema": schema
        })

        return {
            "generated_query": {
                "include_node_types": result.include_node_types,
                "filter": result.filter,
                "relation": result.relation,
                "explanation": result.explanation
            }
        }

    except Exception as e:
        return {
            "generated_query": {},
            "error": str(e)
        }
