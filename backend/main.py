from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from agents.research_agent import ResearchAgent
from schemas.models import ResearchRequest, ResearchResponse
import asyncio

app = FastAPI()
agent = ResearchAgent()

@app.post("/analyze", response_model=ResearchResponse)
async def analyze_request(request: Request):
    try:
        content_type = request.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            data = await request.json()
            req = ResearchRequest(**data)
        else:
            form = await request.form()
            req = ResearchRequest(
                query=form.get("query", ""),
                file_content=await form["file"].read() if "file" in form else None,
                file_type=form.get("file_type")
            )
        
        result = await agent.run(
            query=req.query,
            file_content=req.file_content,
            file_type=req.file_type
        )
        
        return ResearchResponse(**result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ResearchResponse(
                answer=f"Error: {str(e)}",
                warnings=[str(e)]
            ).dict()
        )