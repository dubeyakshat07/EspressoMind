# run_graph.py

from graph_builder import build_graph

def ask_research_question(query: str, goal: str = "Summarize recent research"):
    graph = build_graph()
    inputs = {"query": query, "research_goal": goal}
    final_state = graph.invoke(inputs)
    return final_state["answer"]

if __name__ == "__main__":
    question = "What are the recent advances in cancer immunotherapy?"
    print(ask_research_question(question))
