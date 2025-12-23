from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.core.agents.graph import agent_graph

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    schema_json: Dict[str, Any]
    rules_json: List[Dict[str, Any]]
    formulas_json: List[Dict[str, Any]]
    pdf_template: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_form(request: GenerateRequest):
    """
    Agentic Endpoint: Generates a full form definition from a natural language prompt.
    """
    if not request.prompt:
         raise HTTPException(status_code=400, detail="Prompt is required")
         
    try:
        inputs = {"user_prompt": request.prompt}
        # Run graph
        result = await agent_graph.ainvoke(inputs)
        
        if result.get("error"):
            # We return partially generated content even if error for debugging
             return {
                "schema_json": result.get("schema_json", {}),
                "rules_json": result.get("rules_json", []),
                "formulas_json": result.get("formulas_json", []),
                "pdf_template": result.get("pdf_template"),
                "error": result.get("error")
            }
            
        return {
            "schema_json": result.get("schema_json", {}),
            "rules_json": result.get("rules_json", []),
            "formulas_json": result.get("formulas_json", []),
            "pdf_template": result.get("pdf_template"),
            "error": None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Execution Failed: {str(e)}")
