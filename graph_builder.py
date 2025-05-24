# graph_builder.py

from langgraph.graph import StateGraph, END
from retriever import gather_context
from llm_chain import get_llm_chain

def build_graph():
    builder = StateGraph()
    
    def fetch_context(state):
        query = state["query"]
        context_sources = gather_context(query)
        state["context"] = "\n\n".join([f"{k.upper()}:\n{v}" for k, v in context_sources.items()])
        return state

    def generate_answer(state):
        query = state["query"]
        context = state["context"]
        goal = state.get("research_goal", "Provide a detailed academic overview.")
        chain = get_llm_chain("mistral")
        result = chain.run({"query": query, "context": context, "research_goal": goal})
        state["answer"] = result
        return state

    builder.add_node("gather", fetch_context)
    builder.add_node("respond", generate_answer)

    builder.set_entry_point("gather")
    builder.add_edge("gather", "respond")
    builder.add_edge("respond", END)

    return builder.compile()
