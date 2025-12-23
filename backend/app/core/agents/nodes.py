import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.llm_router import llm_router
from app.core.agents.state import AgentState

def clean_json_output(text: str) -> str:
    """Helper to strip markdown code blocks from LLM output."""
    if isinstance(text, dict): return text # Already parsed
    return text.replace("```json", "").replace("```", "").strip()

# --- 1. Schema Generator ---
def generate_schema(state: AgentState) -> AgentState:
    print("--- Generating Schema ---")
    llm = llm_router.get_llm(temp=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert form builder. Output JSON only."),
        ("user", """
        Create a multi-step form schema for: {prompt}
        
        Output format (use "pages" array for multi-step forms):
        {{
            "title": "Form Title",
            "pages": [
                {{
                    "id": "page_1",
                    "title": "Page Title",
                    "fields": [
                        {{ "id": "field_id", "type": "text|email|number|select", "label": "Label", "required": true, "options": [...] }}
                    ]
                }}
            ]
        }}
        
        Rules:
        - Use 2-4 pages for typical forms.
        - Group related fields on the same page.
        - Field IDs must be unique across all pages.
        - Keep field IDs simple (e.g., 'email', 'name', 'qty').
        """)
    ])
    
    from langchain_core.output_parsers import StrOutputParser
    chain = prompt | llm | StrOutputParser()
    try:
        raw = chain.invoke({"prompt": state["user_prompt"]})
        cleaned = clean_json_output(raw)
        result = json.loads(cleaned)
        return {**state, "schema_json": result}
    except Exception as e:
        return {**state, "error": f"Schema Gen Failed: {e}"}

# --- 2. Logic Generator ---
def generate_logic(state: AgentState) -> AgentState:
    print("--- Generating Logic ---")
    ifstate_schema = state.get("schema_json")
    if not ifstate_schema:
        return state # Skip if failed prev step

    llm = llm_router.get_llm(temp=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Logic Engine. Output JSON only."),
        ("user", """
        Based on this schema: {schema}
        And User Request: {prompt}
        
        Generate Rules (Visibility) and Formulas (Calculations).
        
        Rules Format:
        [ {{ "trigger": {{ "field": "trigger_id", "operator": "eq|neq|gt|lt|inc", "value": "val" }}, "action": {{ "target_field": "target_id", "effect": "show|hide" }} }} ]
        
        Formulas Format:
        [ {{ "field": "target_id", "expression": "qty * price" }} ] (Use simple arithmetic and field IDs).
        
        Output:
        {{
            "rules": [...],
            "formulas": [...]
        }}
        """)
    ])
    
    from langchain_core.output_parsers import StrOutputParser
    chain = prompt | llm | StrOutputParser()
    try:
        raw = chain.invoke({"schema": json.dumps(ifstate_schema), "prompt": state["user_prompt"]})
        cleaned = clean_json_output(raw)
        result = json.loads(cleaned)
        return {
            **state, 
            "rules_json": result.get("rules", []), 
            "formulas_json": result.get("formulas", [])
        }
    except Exception as e:
        # Fallback to empty logic if parsing fails
        print(f"Logic Gen Warning: {e}")
        return {**state, "rules_json": [], "formulas_json": []}

# --- 3. Template Generator ---
def generate_template(state: AgentState) -> AgentState:
    print("--- Generating PDF Template ---")
    llm = llm_router.get_llm(temp=0.4) # Slightly more creative for HTML
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an HTML expert. Output raw HTML string only."),
        ("user", """
        Create a simple, professional HTML template for a PDF export based on this form schema: {schema}
        
        Use Jinja2 placeholders {{ field_id }} for dynamic data.
        Add basic inline CSS for styling (font-family: sans-serif).
        Include a 'Computed Results' section for any calculated fields if likely appropriate.
        
        Do not output markdown code blocks. Just the HTML string.
        """)
    ])
    
    # We expect a string, not JSON
    chain = prompt | llm
    try:
        result = chain.invoke({"schema": json.dumps(state["schema_json"])})
        # Clean up if model outputs markdown blocks
        content = result.content.replace("```html", "").replace("```", "").strip()
        return {**state, "pdf_template": content}
    except Exception as e:
        return {**state, "pdf_template": "<h1>Report</h1><p>Error generating template.</p>"}

