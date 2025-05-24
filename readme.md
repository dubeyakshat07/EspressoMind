# EspressoMind ☕🧠

**AI-Powered Research Assistant with Automated Source Verification**

![alt text](EspressoMind.png)

## ✨ Features

### 🔍 Intelligent Research
- Hybrid search across web + academic databases (arXiv, PubMed)
- Automatic source quality assessment with confidence scoring
- Dynamic research strategy selection based on query complexity

### 📚 Citation Management
- APA-style citation generation
- Automatic reference section formatting
- Source metadata extraction (authors, dates, publishers)

### 📂 Multi-Format Processing
- PDF text extraction with PyMuPDF
- Image OCR using Tesseract
- Web page scraping with Playwright

### ⚡ Performance Optimized
- Async pipeline for concurrent processing
- Intelligent caching of frequent queries
- Progressive result refinement

## 🛠 Tech Stack

### Core Components
| Component | Purpose |
|-----------|---------|
| FastAPI | REST API backend |
| LangGraph | Agent workflow orchestration |
| Ollama | Local LLM (Mistral/Llama2) |
| Playwright | Browser automation |
| Pydantic v2 | Data validation |

### Support Libraries
```plaintext
arxiv - Academic paper search
pymupdf - PDF processing
pytesseract - Image OCR
requests - HTTP client
python-multipart - File uploads
```

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Playwright browsers (`playwright install`)
- Tesseract OCR (`brew install tesseract` on macOS)

### Setup
```bash
# Clone repository
git clone https://github.com/dubeyakshat07/EspressoMind.git
cd EspressoMind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

## 💻 Usage

### Running the API Server
```bash
uvicorn backend.main:app --reload --port 8000
```

### Example API Requests

**Basic Text Query:**
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "query": "Explain quantum entanglement",
        "depth": "balanced"  # quick/balanced/deep
    }
)
```

**With PDF Upload:**
```python
with open('research.pdf', 'rb') as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={
            'file': ('research.pdf', f),
            'file_type': (None, 'pdf')
        },
        data={
            'query': 'Summarize this paper'
        }
    )
```

### Expected Response
```json
{
  "answer": "Quantum entanglement is... [1][2]",
  "sources": [
    {
      "title": "Experimental observation of quantum entanglement",
      "url": "https://arxiv.org/abs/1234.5678",
      "source_type": "arxiv",
      "authors": ["Einstein, A.", "Podolsky, B."],
      "publish_date": "1935-05-15",
      "confidence": 0.92
    }
  ],
  "related_queries": [
    "Applications of quantum entanglement in computing",
    "Recent breakthroughs in entanglement research"
  ],
  "confidence_score": 0.87
}
```

## 🗂 Project Structure

```
EspressoMind/
├── backend/
│   ├── agents/
│   │   ├── research_agent.py  # Main research logic
│   │   └── tools.py          # Search/scraping tools
│   ├── schemas/
│   │   └── models.py         # Pydantic models
│   └── main.py               # FastAPI app
├── frontend/                 # Streamlit UI
│   └── app.py
├── tests/                    # Test suite
├── docs/                     # Documentation
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## ⚙ Configuration

Edit `.env` file:
```ini
# Search Configuration
SEARXNG_URL=https://search.example.com
MAX_WEB_RESULTS=5
MAX_ACADEMIC_RESULTS=3

# AI Configuration
OLLAMA_MODEL=mistral
LLM_TEMPERATURE=0.3

# Performance
SCRAPE_TIMEOUT=20
PDF_PROCESS_TIMEOUT=30
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

Key test coverage:
- API endpoints
- Search tools
- Document processing
- Citation generation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📧 Contact

Project Maintainer - [Akshat Dubey]  

---

**EspressoMind** - Because research should be as stimulating as your morning coffee. ☕  
*"The scholar's AI research companion"*
```
