#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def format_python_file(file_path):
    """Format Python file after it's written or edited."""
    try:
        # Run black formatter
        subprocess.run(['black', file_path], check=True, capture_output=True)
        
        # Run isort for import sorting
        subprocess.run(['isort', file_path], check=True, capture_output=True)
        
        # Run mypy for type checking
        mypy_result = subprocess.run(['mypy', file_path], capture_output=True, text=True)
        if mypy_result.returncode != 0:
            return f"mypy issues:\n{mypy_result.stdout}\n{mypy_result.stderr}"
        
        return None
    except subprocess.CalledProcessError as e:
        return f"Error formatting {file_path}: {e.stdout}\n{e.stderr}"

def process_file(file_path):
    """Process file based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.py':
        return format_python_file(file_path)
    
    # Add handlers for other file types as needed
    return None

try:
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})
    
    # For Write tool
    if tool_name in ["Write", "Edit", "MultiEdit"]:
        file_path = None
        if tool_name == "Write":
            file_path = tool_input.get("file_path", "")
        elif tool_name == "Edit":
            file_path = tool_input.get("file_path", "")
        elif tool_name == "MultiEdit":
            # Get path from first edit in the list
            edits = tool_input.get("edits", [])
            if edits and "file_path" in edits[0]:
                file_path = edits[0]["file_path"]
        
        if file_path:
            issues = process_file(file_path)
            if issues:
                # Return a JSON response to block the tool
                json_response = {
                    "decision": "block",
                    "reason": f"File formatting issues detected:\n{issues}\nPlease fix these issues before proceeding."
                }
                print(json.dumps(json_response))
                sys.exit(0)  # Use exit code 0 with JSON response
    
    # Exit normally if no issues found
    sys.exit(0)
    
except Exception as e:
    print(f"Hook error: {str(e)}", file=sys.stderr)
    sys.exit(1)  # Non-blocking error