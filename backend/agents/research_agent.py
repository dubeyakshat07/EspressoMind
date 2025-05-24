from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Annotated, Optional
import operator
from .tools import ResearchTools
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
import asyncio
import re
from datetime import datetime

class AgentState(TypedDict):
    query: str
    file_content: Optional[bytes]
    file_type: Optional[str]
    context: Annotated[List[Dict], operator.add]
    answer: str
    research_type: Optional[int]

class ResearchAgent:
    def __init__(self):
        self.tools = ResearchTools()
        self.llm = ChatOllama(model="gemma3:1b", temperature=0.3)
        self.workflow = self._create_workflow()
        self.search_strategy = {}
    
    def _create_workflow(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("analyze", self.analyze_input)
        workflow.add_node("research", self.perform_research)
        workflow.add_node("generate", self.generate_answer)
        
        workflow.add_edge("analyze", "research")
        workflow.add_edge("research", "generate")
        workflow.add_edge("generate", END)
        
        workflow.set_entry_point("analyze")
        return workflow.compile()
    
    async def analyze_input(self, state: AgentState):
        file_context = ""
        if state["file_content"]:
            file_context = self.tools.process_input(
                state["file_content"],
                state["file_type"] or "text"
            )
        
        prompt = ChatPromptTemplate.from_template("""
        Analyze this research request and respond with ONLY the number:
        1 - Direct factual answer
        2 - Web research required
        3 - Academic papers needed

        Query: {query}
        File Context: {file_context}
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "query": state["query"],
            "file_context": file_context[:2000]
        }).content.strip()
        
        decision = self._parse_research_decision(response)
        self.search_strategy["initial_decision"] = decision
        return {"research_type": decision}

    def _parse_research_decision(self, response: str) -> int:
        try:
            match = re.search(r'\b(1|2|3)\b', response)
            return int(match.group(1)) if match else 2
        except:
            return 2

    async def perform_research(self, state: AgentState):
        research_type = state.get("research_type", 2)
        self.search_strategy["final_type"] = research_type
        
        search_results = []
        try:
            if research_type == 2:
                results = await self.tools.enhanced_web_search(state["query"])
                search_results = await self.tools.enrich_with_scraping(results)
                self.search_strategy["sources"] = ["web", "scraped"]
            elif research_type == 3:
                search_results = self.tools.arxiv_search(state["query"])
                search_results += self.tools.pubmed_search(state["query"])
                self.search_strategy["sources"] = ["arxiv", "pubmed"]
        
        except Exception as e:
            print(f"Research error: {str(e)}")
        
        return {"context": search_results[:10]}

    async def generate_answer(self, state: AgentState):
        citations = self._generate_citations(state["context"])
        context_str = self._build_context_string(state["context"])
        
        prompt = ChatPromptTemplate.from_template("""
        Compose a comprehensive answer with citations:
        Query: {query}
        
        Research Context:
        {context}
        
        Guidelines:
        1. Use [1], [2] style citations
        2. Prioritize academic sources
        3. Highlight conflicting information
        4. Include key statistics
        5. Maintain scholarly tone""")
        
        chain = prompt | self.llm
        answer = chain.invoke({
            "query": state["query"],
            "context": context_str
        }).content
        
        return {
            "answer": f"{answer}\n\n## References\n{citations}",
            "context": state["context"]
        }

    async def run(self, query: str, file_content: Optional[bytes] = None, file_type: Optional[str] = None):
        start_time = datetime.now()
        warnings = []
        
        try:
            result = await self.workflow.ainvoke({
                "query": query,
                "file_content": file_content,
                "file_type": file_type,
                "context": [],
                "research_type": None
            })
            
            return {
                "answer": result["answer"],
                "sources": [self._create_citation_source(s) for s in result["context"]],
                "related_queries": await self._generate_related_queries(query, result["context"]),
                "search_strategy": self.search_strategy,
                "processed_at": datetime.now(),
                "confidence_score": self._calculate_confidence(result["context"]),
                "warnings": warnings
            }
        except Exception as e:
            return {
                "answer": f"Research error: {str(e)}",
                "sources": [],
                "related_queries": [],
                "search_strategy": {},
                "processed_at": datetime.now(),
                "confidence_score": 0.0,
                "warnings": [str(e)]
            }

    def _create_citation_source(self, source: Dict) -> Dict:
        return {
            "title": source.get("title", ""),
            "url": source.get("url", "#"),
            "source_type": source.get("type", "web"),
            "authors": source.get("authors", []),
            "publish_date": source.get("published"),
            "snippet": source.get("snippet"),
            "confidence": source.get("confidence", 0.0)
        }

    async def _generate_related_queries(self, query: str, sources: List[Dict]) -> List[str]:
        prompt = ChatPromptTemplate.from_template("""
        Generate 3 related research questions based on:
        Original: {query}
        Found sources: {sources}
        """)
        chain = prompt | self.llm
        response = chain.invoke({
            "query": query,
            "sources": "\n".join([s["title"] for s in sources[:3]])
        }).content
        return [q.strip() for q in response.split("\n") if q.strip()][:3]

    def _calculate_confidence(self, sources: List[Dict]) -> float:
        if not sources:
            return 0.0
        academic = len([s for s in sources if s["type"] in ["arxiv", "pubmed"]])
        return min(academic/len(sources) + 0.2 * len(sources)/10, 1.0)

    def _generate_citations(self, sources: List[Dict]) -> str:
        """Generate APA-style citations for all sources"""
        return "\n".join(
            [self._format_citation(source) for source in sources if source.get("url")]
        )

    def _format_citation(self, source: Dict) -> str:
        """Format citation based on source type"""
        if source["type"] == "arxiv":
            return self._format_arxiv_citation(source)
        elif source["type"] == "pubmed":
            return self._format_pubmed_citation(source)
        return self._format_web_citation(source)

    def _format_web_citation(self, source: Dict) -> str:
        """APA style web citation"""
        authors = f"{source.get('authors', '')} " if source.get("authors") else ""
        date = source.get("published", source.get("date", datetime.now().strftime("%Y")))
        return f"{authors}({date}). {source['title']}. Retrieved from {source['url']}"

    def _format_arxiv_citation(self, source: Dict) -> str:
        """APA style arXiv citation"""
        authors = ", ".join(source.get("authors", [])) if source.get("authors") else "Anonymous"
        year = source["published"][:4] if source.get("published") else "n.d."
        return f"{authors} ({year}). {source['title']}. arXiv preprint {source['url'].split('/')[-1]}"

    def _build_context_string(self, sources: List[Dict]) -> str:
        """Build research context string for LLM"""
        return "\n\n".join(
            f"Source {i+1} ({src['type']}): {src.get('content', src.get('summary', ''))[:1000]}"
            for i, src in enumerate(sources)
        )

    async def run(self, query: str, file_content: Optional[bytes] = None, file_type: Optional[str] = None):
        """Execute full research pipeline"""
        try:
            result = await self.workflow.ainvoke({
                "query": query,
                "file_content": file_content,
                "file_type": file_type,
                "context": [],
                "research_type": None
            })
            
            return {
                "answer": result["answer"],
                "sources": result["context"],
                "query": query
            }
        except Exception as e:
            return {
                "answer": f"Research error: {str(e)}",
                "sources": [],
                "query": query
            }