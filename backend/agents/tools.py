from typing import List, Dict, Optional, Union
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import ArxivAPIWrapper, PubMedAPIWrapper
from langchain_community.document_loaders import PyMuPDFLoader
import os
import tempfile
import requests
import pytesseract
from PIL import Image
import io
import re
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Optional, Union
from langchain_community.utilities import ArxivAPIWrapper, PubMedAPIWrapper
from playwright.async_api import async_playwright
import requests
import re

class ResearchTools:
    def __init__(self):
        self.arxiv = ArxivAPIWrapper(top_k_results=5)
        self.pubmed = PubMedAPIWrapper(top_k_results=5)
        self.browser = None

    async def enhanced_web_search(self, query: str) -> List[Dict]:
        try:
            results = []
            # SearxNG search
            results += await self.searxng_search(query)
            # Academic search
            if self._needs_academic(query):
                results += self.arxiv_search(query)
                results += self.pubmed_search(query)
            return self._deduplicate(results)
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    async def searxng_search(self, query: str) -> List[Dict]:
        try:
            response = requests.get(
                "https://search.example.com/search",
                params={
                    'q': query,
                    'format': 'json',
                    'categories': 'general,scholar'
                },
                timeout=10
            )
            return [self._format_result(r) for r in response.json()["results"]]
        except Exception as e:
            print(f"SearxNG error: {str(e)}")
            return []

    def _format_result(self, result: Dict) -> Dict:
        return {
            "title": result.get("title", ""),
            "url": result.get("url", "#"),
            "snippet": result.get("content", "")[:500],
            "type": self._classify_type(result.get("url")),
            "domain": self._get_domain(result.get("url"))
        }

    async def enrich_with_scraping(self, results: List[Dict]) -> List[Dict]:
        if not self.browser:
            await self._init_browser()
        
        enriched = []
        for result in results[:5]:
            try:
                content = await self.scrape_page(result["url"])
                enriched.append({**result, "content": content})
            except:
                continue
        return enriched

    async def scrape_page(self, url: str) -> str:
        context = await self.browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=15000)
            return await page.evaluate('''() => document.body.innerText''')[:5000]
        finally:
            await context.close()

    def process_input(self, file_data: Union[str, bytes], input_type: str = "text") -> str:
        try:
            if input_type == "text":
                return file_data.decode() if isinstance(file_data, bytes) else file_data
            
            elif input_type == "image":
                image = Image.open(io.BytesIO(file_data))
                return pytesseract.image_to_string(image)
            
            elif input_type == "pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file_data)
                    tmp_path = tmp.name
                
                try:
                    loader = PyMuPDFLoader(tmp_path)
                    docs = loader.load()
                    return "\n\n".join(doc.page_content for doc in docs)
                finally:
                    os.unlink(tmp_path)
            
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
        
        except Exception as e:
            print(f"Input processing error: {str(e)}")
            raise

    async def smart_search(self, query: str, existing_context: str = "") -> List[Dict]:
        # First perform a web search
        web_results = self.searxng_search(query)
        
        # Then get academic sources if relevant
        academic_results = []
        if any(keyword in query.lower() for keyword in ['research', 'study', 'paper', 'academic']):
            academic_results.extend(self.arxiv_search(query))
            if any(keyword in query.lower() for keyword in ['medical', 'health', 'biology']):
                academic_results.extend(self.pubmed_search(query))
        
        # Scrape top 3 web results
        scraped_data = []
        for result in web_results[:3]:
            try:
                scraped = await self.scrape_page(result['url'])
                if scraped['status'] == 'success':
                    result['content'] = scraped['content'][:5000]
                    scraped_data.append(result)
            except:
                continue
        
        return scraped_data + academic_results

    # [Keep other existing methods like searxng_search, arxiv_search, etc.]