# retriever.py

from search_tools import search_tools

def gather_context(query: str) -> dict:
    context_results = {}
    for name, tool in search_tools.items():
        try:
            result = tool.run(query)
            context_results[name] = result
        except Exception as e:
            context_results[name] = f"Error from {name}: {e}"
    return context_results
