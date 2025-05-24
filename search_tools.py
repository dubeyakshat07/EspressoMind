# search_tools.py

import asyncio
import requests
from langchain.tools import DuckDuckGoSearchResults
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.pubmed import PubMedAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.utilities.wikidata import WikidataAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.tools.wikidata.tool import WikidataQueryRun

class AsyncDuckDuckGo:
    name = "DuckDuckGo"
    def run(self, query):
        return DuckDuckGoSearchResults().run(query)

class SimplePubMed:
    name = "PubMed"
    def run(self, query):
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": "3"}
        r = requests.get(url, params=params).json()
        ids = r.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return "No PubMed results"
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        sparams = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        res = requests.get(summary_url, params=sparams).json()
        return "\n".join(f"{res['result'][i]['title']} ({res['result'][i].get('source', '')})" for i in ids)

wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
wikidata_tool = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())
arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())
pubmed_tool = PubmedQueryRun(api_wrapper=PubMedAPIWrapper())
duck_tool = AsyncDuckDuckGo()

search_tools = {
    "wikipedia": wikipedia_tool,
    "wikidata": wikidata_tool,
    "arxiv": arxiv_tool,
    "pubmed": pubmed_tool,
    "duckduckgo": duck_tool,
}
def auto_tool_search(query):
    results = []
    for name, tool in search_tools.items():
        try:
            result = tool.run(query)
            results.append(f"{name.upper()} Result:\n{result}")
        except Exception as e:
            results.append(f"{name.upper()} Error: {e}")
    return "\n\n".join(results)