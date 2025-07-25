import os
from dotenv import load_dotenv
#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model_name="gpt-4"):
    """Return a LangChain LLM object using OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    return ChatOpenAI(
        model=f"openrouter/openai/{model_name}",
        temperature=0,
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key
    )

def define_llm(model='gpt4o'):
    try:
        if (model=='gpt4o'):
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                max_retries =2
            )
            print("GPT 4o API is called")
            return llm
        if (model=='o3'):
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                max_retries =2
            )
            print("GPT o3 API is called")
            return llm
    except Exception as E:
        print("Error: ",E)