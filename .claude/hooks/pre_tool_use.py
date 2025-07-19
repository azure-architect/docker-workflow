#!/usr/bin/env python3
import json
import re
import sys
import os

def validate_python_file(file_path, content):
    """Validate Python file content before writing."""
    issues = []
    
    # Check max file length
    if len(content.splitlines()) > 500:
        issues.append("File exceeds 500 lines maximum length")
    
    # Check for required imports for certain components
    if 'email_client' in file_path and 'import ssl' not in content:
        issues.append("Email clients should import ssl for secure connections")
    
    # Check for security issues
    if re.search(r'os\.system\(', content):
        issues.append("Avoid using os.system() - use subprocess instead")
    
    # Check type annotations
    if not re.search(r'def\s+\w+\([^)]*\)\s*->\s*\w+', content):
        issues.append("Functions should include return type annotations")
    
    return issues

def validate_file(file_path, content):
    """Validate file content based on file type."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.py':
        return validate_python_file(file_path, content)
    elif ext == '.sql':
        # Add SQL-specific validations
        return []
    elif ext == '.md':
        # Add markdown-specific validations
        return []
    else:
        return []

try:
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    # For Write tool
    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        
        issues = validate_file(file_path, content)
        
        if issues:
            print("File validation issues:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            sys.exit(2)  # Block with feedback to Claude
    
    # For Edit tool
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        old_content = tool_input.get("old_content", "")
        new_content = tool_input.get("new_content", "")
        
        issues = validate_file(file_path, new_content)
        
        if issues:
            print("File validation issues:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            sys.exit(2)  # Block with feedback to Claude
    
    # Exit normally if no issues found
    sys.exit(0)
    
except Exception as e:
    print(f"Hook error: {str(e)}", file=sys.stderr)
    sys.exit(1)  # Non-blocking error