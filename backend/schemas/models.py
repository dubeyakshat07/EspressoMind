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