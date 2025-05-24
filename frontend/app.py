import streamlit as st
import requests
import base64
import os
# Update this import
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class CitationSource(BaseModel):
    title: str = Field(..., min_length=3)
    url: str = Field(..., pattern=r'^https?://')
    source_type: Literal["web", "arxiv", "pubmed", "pdf", "image"] = Field("web")
    authors: Optional[List[str]] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    snippet: Optional[str] = None
    scraped_content: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)

class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    file_content: Optional[str] = None
    file_type: Optional[Literal["pdf", "image", "text"]] = None
    depth: Literal["quick", "balanced", "deep"] = "balanced"

class ResearchResponse(BaseModel):
    answer: str
    sources: List[CitationSource] = Field(default_factory=list)
    related_queries: List[str] = Field(default_factory=list)
    search_strategy: Dict = Field(default_factory=dict)
    processed_at: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)
# Configuration
API_URL = "http://localhost:8000"
MAX_FILE_SIZE_MB = 10

st.set_page_config(page_title="AI Research Assistant", layout="wide")

def main():
    st.title("🧠 AI Research Assistant")
    
    with st.expander("🔍 Research Input", expanded=True):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            query = st.text_area("Research Question", 
                               placeholder="Enter your research question...",
                               height=150)
            
        with col2:
            file = st.file_uploader("Upload Supporting Documents",
                                  type=["pdf", "txt", "png", "jpg", "jpeg"],
                                  accept_multiple_files=False,
                                  help="Optional: Upload PDFs, images, or text files")
            
            depth = st.selectbox("Research Depth",
                               ["Quick", "Balanced", "Deep"],
                               index=1)

    if st.button("🚀 Start Research", type="primary"):
        if not query and not file:
            st.warning("Please enter a question or upload a file")
            return
            
        with st.spinner("🔬 Conducting research..."):
            try:
                # Prepare request
                file_content = None
                file_type = None
                
                if file:
                    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        st.error(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")
                        return
                    file_content = base64.b64encode(file.read()).decode()
                    file_type = file.name.split('.')[-1].lower()
                
                response = requests.post(
                    f"{API_URL}/analyze",
                    json=ResearchRequest(
                        query=query,
                        file_content=file_content,
                        file_type=file_type,
                        depth=depth.lower()
                    ).dict(),
                    timeout=120
                ).json()
                
                res = ResearchResponse(**response)
                
                # Display results
                st.subheader("📝 Research Findings")
                st.markdown(res.answer)
                
                with st.expander(f"📚 Sources ({len(res.sources)})"):
                    for idx, source in enumerate(res.sources, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style="padding:15px; margin:10px 0; border-left:4px solid #4e79a7; background:#f8f9fa;">
                                <h4>Source #{idx}: {source.title}</h4>
                                <p><strong>Type:</strong> {source.source_type.upper()}</p>
                                {f"<p><a href='{source.url}' target='_blank'>🌐 Visit Source</a></p>" if source.url else ""}
                                {f"<p><strong>Snippet:</strong> {source.snippet[:300]}...</p>" if source.snippet else ""}
                                {f"<p><strong>Authors:</strong> {', '.join(source.authors[:3])}</p>" if source.authors else ""}
                                <p><strong>Confidence:</strong> {source.confidence:.0%}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                if res.warnings:
                    with st.expander("⚠️ Research Warnings"):
                        for warning in res.warnings:
                            st.warning(warning)
                
            except Exception as e:
                st.error(f"Research failed: {str(e)}")

if __name__ == "__main__":
    main()