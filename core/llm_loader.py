# llm_loader.py

# from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq  # ✅ correct Groq import

def load_llm(model_type, model_name):
    if model_type == "openai":
        pass
        # return ChatOpenAI(
        #     temperature=0.3,
        #     model=model_name,
        #     openai_api_key="sk-proj-...",  # replace with env variable in prod
        # )
    elif model_type == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model=model_name)
    elif model_type == "huggingface":
        from langchain_community.llms import HuggingFaceHub
        return HuggingFaceHub(repo_id=model_name)
    elif model_type == "groq":
        return ChatGroq(
            temperature=0.3,
            model_name=model_name,
        )
    else:
        raise ValueError("Invalid model type specified.")
