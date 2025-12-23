from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    user_prompt: str
    schema_json: Dict[str, Any]
    rules_json: List[Dict[str, Any]]
    formulas_json: List[Dict[str, Any]]
    pdf_template: str
    error: Optional[str]
