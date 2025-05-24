# llm_chain.py

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

def get_llm_chain(model="mistral") -> LLMChain:
    llm = ChatOllama(model=model, temperature=0.2)
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful AI research assistant. Use the following context to answer the research query with sources:

Query: {query}
Research Goal: {research_goal}
Context:
{context}

Answer concisely and cite your sources."""
    )
    return LLMChain(llm=llm, prompt=prompt)
