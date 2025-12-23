import ast
import operator
import re
from typing import Dict, Any, List

# Allowed operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
}

# Allowed functions
FUNCTIONS = {
    "min": min,
    "max": max,
    "round": round,
    "abs": abs,
    "sum": sum
}

class FormulaError(Exception):
    pass

class FormulaEvaluator:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def _eval(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in OPERATORS:
                raise FormulaError(f"Operator {op_type} not allowed")
            return OPERATORS[op_type](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in OPERATORS:
                raise FormulaError(f"Operator {op_type} not allowed")
            return OPERATORS[op_type](self._eval(node.operand))
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
               raise FormulaError("Function calls must be direct names")
            func_name = node.func.id
            if func_name not in FUNCTIONS:
                raise FormulaError(f"Function '{func_name}' not allowed")
            args = [self._eval(arg) for arg in node.args]
            return FUNCTIONS[func_name](*args if func_name != 'sum' else [args]) 
            # Note: sum() expects an iterable, but our args are unwrapped. 
            # Adjusting: sum takes iterable. python sum([1,2]). 
            # If user writes sum(1, 2) it fails. 
            # Let's handle generic args.
            
        elif isinstance(node, ast.Expression):
             return self._eval(node.body)
        else:
            raise FormulaError(f"Node type {type(node)} not allowed in safety sandbox")

    def evaluate(self, expression: str) -> float:
        """
        Evaluates a mathemtical expression.
        Expression should have field references resolved BEFORE calling this 
        OR we resolve them here. 
        Current approach: Pre-resolution.
        """
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval(tree.body)
        except Exception as e:
            raise FormulaError(f"Evaluation error: {str(e)}")

def process_formulas(formulas: List[Dict[str, Any]], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formulas format: 
    [ { "target_field": "total", "expression": "{{qty}} * {{price}}" } ]
    """
    computed = {}
    
    # Simple Topological sort issues? 
    # For MVP, assume order in list is correct execution order.
    
    # 1. Resolve variables
    # We allow formulas to reference previously computed values too.
    working_data = {**data} # Copy
    
    for f in formulas:
        target = f.get("target_field")
        raw_expr = f.get("expression", "")
        
        # Regex to find {{variable}}
        # We replace them with their numeric values.
        # If value is string, we might break.
        
        def replace_var(match):
            key = match.group(1)
            val = working_data.get(key, 0) # Default to 0 if missing
            if val is None or val == "": val = 0
            return str(val)
            
        # Replace {{key}} with value
        expr_with_values = re.sub(r"\{\{([^}]+)\}\}", replace_var, raw_expr)
        
        try:
            evaluator = FormulaEvaluator(working_data)
            result = evaluator.evaluate(expr_with_values)
            computed[target] = result
            working_data[target] = result
        except Exception as e:
            computed[target] = 0 # Or error?
            # Log error
            print(f"Formula Error for {target}: {e}")
            
    return computed
