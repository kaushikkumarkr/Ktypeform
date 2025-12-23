from typing import List, Dict, Any

def evaluate_rules(rules: List[Dict[str, Any]], data: Dict[str, Any]) -> Dict[str, bool]:
    """
    Evaluates rules to determine field visibility.
    Returns a dictionary of field_id -> is_visible.
    By default, all fields are visible unless a rule hides them.
    
    Rule Format Example:
    {
      "trigger": { "field": "age", "operator": "lt", "value": 18 },
      "action": { "target_field": "beer_brand", "effect": "hide" }
    }
    """
    # Initialize visibility map (we only track changes)
    # Ideally, we should know all fields to set default True, 
    # but for now we return overrides. The frontend/backend can merge.
    visibility_overrides = {} 
    
    for rule in rules:
        trigger = rule.get("trigger", {})
        action = rule.get("action", {})
        
        trigger_field = trigger.get("field")
        operator = trigger.get("operator")
        trigger_value = trigger.get("value")
        
        actual_value = data.get(trigger_field)
        
        is_triggered = False
        
        if actual_value is not None:
            # Type conversion for comparison if needed
            try:
                if isinstance(trigger_value, (int, float)) and isinstance(actual_value, (int, float, str)):
                     actual_value = float(actual_value)
                     trigger_value = float(trigger_value)
            except ValueError:
                pass # compare as strings

            if operator == "eq":
                is_triggered = actual_value == trigger_value
            elif operator == "neq":
                is_triggered = actual_value != trigger_value
            elif operator == "gt":
                try: is_triggered = actual_value > trigger_value
                except: pass
            elif operator == "lt":
                try: is_triggered = actual_value < trigger_value
                except: pass
            elif operator == "inc": # includes
                is_triggered = str(trigger_value) in str(actual_value)
        
        if is_triggered:
            target = action.get("target_field")
            effect = action.get("effect")
            
            if effect == "hide":
                visibility_overrides[target] = False
            elif effect == "show":
                visibility_overrides[target] = True
                
    return visibility_overrides
