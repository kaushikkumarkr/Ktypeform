from typing import Dict, Any, List, Optional
import re
from fastapi import HTTPException

class ValidationError(Exception):
    def __init__(self, message: str, field_id: str):
        self.message = message
        self.field_id = field_id
        super().__init__(message)

def validate_submission(schema: Dict[str, Any], data: Dict[str, Any]) -> None:
    """
    Validates submission data against the form schema.
    Raises ValidationError if invalid.
    """
    fields = schema.get("fields", [])
    
    for field in fields:
        field_id = field.get("id")
        field_type = field.get("type")
        required = field.get("required", False)
        
        value = data.get(field_id)
        
        # Check required
        if required and (value is None or value == ""):
            raise ValidationError(f"Field '{field.get('label', field_id)}' is required", field_id)
            
        if value is not None and value != "":
            # Type validation
            if field_type == "number":
                try:
                    float(value)
                except ValueError:
                    raise ValidationError(f"Field '{field_id}' must be a number", field_id)
                    
                min_val = field.get("min")
                max_val = field.get("max")
                if min_val is not None and float(value) < float(min_val):
                     raise ValidationError(f"Field '{field_id}' must be at least {min_val}", field_id)
                if max_val is not None and float(value) > float(max_val):
                     raise ValidationError(f"Field '{field_id}' must be at most {max_val}", field_id)

            elif field_type == "email":
                # Simple regex for email
                email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                if not re.match(email_regex, str(value)):
                    raise ValidationError(f"Field '{field_id}' must be a valid email", field_id)
            
            elif field_type == "select" or field_type == "radio":
                options = [opt["value"] for opt in field.get("options", [])]
                if value not in options:
                     raise ValidationError(f"Value '{value}' is not a valid option for field '{field_id}'", field_id)
