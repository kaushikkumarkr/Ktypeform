from langgraph.graph import StateGraph, END
from app.core.agents.state import AgentState
from app.core.agents.nodes import generate_schema, generate_logic, generate_template

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("schema", generate_schema)
    workflow.add_node("logic", generate_logic)
    workflow.add_node("template", generate_template)
    
    # Define Edges: Linear Flow
    workflow.set_entry_point("schema")
    workflow.add_edge("schema", "logic")
    workflow.add_edge("logic", "template")
    workflow.add_edge("template", END)
    
    # Compile
    return workflow.compile()

agent_graph = build_graph()
