from langgraph.graph import StateGraph
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from search_tools import auto_tool_search
from typing import TypedDict

# Step 1: Define state schema
class WorkflowState(TypedDict):
    input: str
    search_result: str
    answer: str

# Step 2: Define LangGraph workflow
def build_workflow():
    embeddings = OllamaEmbeddings(model="mistral")
    vectorstore = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
    retriever = vectorstore.as_retriever()
    llm = Ollama(model="mistral")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # Create stateful graph
    graph = StateGraph(WorkflowState)

    # Node: Tool search
    def search_node(state: WorkflowState) -> WorkflowState:
        search_result = auto_tool_search(state["input"])
        return {**state, "search_result": search_result}

    # Node: Answer generation
    def qa_node(state: WorkflowState) -> WorkflowState:
        answer = qa_chain.run(state["input"])
        return {**state, "answer": answer}

    graph.add_node("search", search_node)
    graph.add_node("qa", qa_node)

    graph.set_entry_point("search")
    graph.add_edge("search", "qa")
    # graph.set_exit_point("qa")

    compiled = graph.compile()


    return compiled