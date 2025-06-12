#!/usr/bin/env python3
"""
Hard Gate Assessment API

FastAPI-based REST API for analyzing GitHub repositories and returning JSON results.
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import uuid

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

from core.flow import Flow
from nodes.fetch_repo import FetchRepo
from nodes.analyze_code import AnalyzeCode
from nodes.format_output import FormatOutput

# Initialize FastAPI app
app = FastAPI(
    title="Hard Gate Assessment API",
    description="Analyze GitHub repositories for hard gate compliance",
    version="1.0.0"
)

# Request/Response Models
class AssessmentRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"
    github_token: Optional[str] = None

class AssessmentResponse(BaseModel):
    assessment_id: str
    project_name: str
    assessment_date: str
    assessment_type: str
    results: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    message: str
    assessment_id: Optional[str] = None

# In-memory storage for async assessment tracking
assessment_store = {}

def create_assessment_flow():
    """
    Create and return the hard gate assessment flow.
    """
    # Create nodes with shorter retry times for API responsiveness
    fetch_repo = FetchRepo(max_retries=2, wait=3)
    analyze_code = AnalyzeCode(max_retries=2, wait=5)
    format_output = FormatOutput()
    
    # Connect nodes in sequence
    fetch_repo >> analyze_code >> format_output
    
    # Create the flow
    return Flow(start=fetch_repo)

def run_assessment_sync(assessment_id: str, repo_url: str, branch: str, github_token: Optional[str]):
    """
    Run the assessment synchronously and store results.
    """
    try:
        # Initialize shared state
        shared = {
            "repo_url": str(repo_url),
            "branch": branch,
            "github_token": github_token,
            "output_format": "json"
        }
        
        # Create and run the assessment flow
        assessment_flow = create_assessment_flow()
        assessment_flow.run(shared)
        
        # Get the formatted JSON output
        formatted_output = shared.get("formatted_output")
        
        if not formatted_output or not isinstance(formatted_output, dict):
            raise ValueError("No valid assessment results generated")
        
        # Store successful result
        assessment_store[assessment_id] = {
            "status": "completed",
            "result": formatted_output,
            "error": None,
            "completed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Store error result
        assessment_store[assessment_id] = {
            "status": "failed",
            "result": None,
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Hard Gate Assessment API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze a GitHub repository",
            "GET /analyze/{assessment_id}": "Get assessment results",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    # Check if required environment variables are set
    llm_configured = any([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GOOGLE_API_KEY")
    ])
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_configured": llm_configured,
        "active_assessments": len([a for a in assessment_store.values() if a["status"] == "running"])
    }

@app.post("/analyze", response_model=Dict[str, str])
async def start_assessment(request: AssessmentRequest, background_tasks: BackgroundTasks):
    """
    Start a new hard gate assessment (async).
    """
    # Validate LLM configuration
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY environment variable."
        )
    
    # Generate assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Initialize assessment tracking
    assessment_store[assessment_id] = {
        "status": "running",
        "result": None,
        "error": None,
        "started_at": datetime.now().isoformat()
    }
    
    # Start background assessment
    background_tasks.add_task(
        run_assessment_sync,
        assessment_id,
        request.repo_url,
        request.branch,
        request.github_token
    )
    
    return {
        "assessment_id": assessment_id,
        "status": "started",
        "message": f"Assessment started for {request.repo_url}",
        "check_status_url": f"/analyze/{assessment_id}"
    }

@app.post("/analyze/sync", response_model=AssessmentResponse)
async def analyze_sync(request: AssessmentRequest):
    """
    Perform synchronous hard gate assessment (may be slow for large repositories).
    """
    # Validate LLM configuration
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY environment variable."
        )
    
    assessment_id = str(uuid.uuid4())
    
    try:
        # Initialize shared state
        shared = {
            "repo_url": str(request.repo_url),
            "branch": request.branch,
            "github_token": request.github_token,
            "output_format": "json"
        }
        
        # Create and run the assessment flow
        assessment_flow = create_assessment_flow()
        assessment_flow.run(shared)
        
        # Get the formatted JSON output
        formatted_output = shared.get("formatted_output")
        
        if not formatted_output or not isinstance(formatted_output, dict):
            raise HTTPException(status_code=500, detail="No valid assessment results generated")
        
        return AssessmentResponse(
            assessment_id=assessment_id,
            project_name=formatted_output.get("project_name", "Unknown"),
            assessment_date=formatted_output.get("assessment_date", datetime.now().isoformat()),
            assessment_type=formatted_output.get("assessment_type", "hard_gate_assessment"),
            results=formatted_output.get("results", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.get("/analyze/{assessment_id}")
async def get_assessment_result(assessment_id: str):
    """
    Get the result of a specific assessment.
    """
    if assessment_id not in assessment_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessment_store[assessment_id]
    
    if assessment["status"] == "running":
        return {
            "assessment_id": assessment_id,
            "status": "running",
            "message": "Assessment is still in progress",
            "started_at": assessment.get("started_at")
        }
    elif assessment["status"] == "failed":
        return ErrorResponse(
            error="assessment_failed",
            message=assessment["error"],
            assessment_id=assessment_id
        )
    else:
        # Completed successfully
        result = assessment["result"]
        return AssessmentResponse(
            assessment_id=assessment_id,
            project_name=result.get("project_name", "Unknown"),
            assessment_date=result.get("assessment_date", assessment.get("completed_at")),
            assessment_type=result.get("assessment_type", "hard_gate_assessment"),
            results=result.get("results", {})
        )

@app.delete("/analyze/{assessment_id}")
async def delete_assessment(assessment_id: str):
    """
    Delete assessment results from memory.
    """
    if assessment_id not in assessment_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    del assessment_store[assessment_id]
    return {"message": f"Assessment {assessment_id} deleted"}

@app.get("/analyze")
async def list_assessments():
    """
    List all assessments with their status.
    """
    assessments = []
    for assessment_id, data in assessment_store.items():
        assessments.append({
            "assessment_id": assessment_id,
            "status": data["status"],
            "started_at": data.get("started_at"),
            "completed_at": data.get("completed_at")
        })
    
    return {
        "assessments": assessments,
        "total": len(assessments)
    }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 