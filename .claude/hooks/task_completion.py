#!/usr/bin/env python3
import json
import sys
import os
import subprocess
import re

def check_test_coverage(component_path):
    """Check if tests exist for the component and have sufficient coverage."""
    component_name = os.path.basename(component_path).replace('.py', '')
    test_path = f"tests/test_{component_name}.py"
    
    if not os.path.exists(test_path):
        return False, f"Missing tests for {component_name}"
    
    # Run pytest with coverage
    try:
        result = subprocess.run(
            ['pytest', test_path, '--cov', component_path, '-v'], 
            capture_output=True, 
            text=True
        )
        
        # Extract coverage percentage
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
        if match:
            coverage = int(match.group(1))
            if coverage < 80:
                return False, f"Test coverage is {coverage}%, minimum required is 80%"
        else:
            return False, "Could not determine test coverage"
    except subprocess.CalledProcessError:
        return False, f"Tests failed for {component_name}"
    
    return True, None

def check_task_completion(transcript_path):
    """Check if the current task has been completed successfully."""
    try:
        # Parse the task from the transcript
        # This is a simplified approach - in practice, you'd need to parse the JSONL transcript
        current_dir = os.getcwd()
        python_files = []
        
        # Find Python files modified in the last session
        for root, _, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        # Check for issues in each file
        issues = []
        for file_path in python_files:
            # Check if file has docstrings
            with open(file_path, 'r') as f:
                content = f.read()
                if '"""' not in content:
                    issues.append(f"Missing docstrings in {file_path}")
            
            # Check test coverage
            has_tests, test_issue = check_test_coverage(file_path)
            if not has_tests:
                issues.append(test_issue)
        
        if issues:
            return False, issues
        
        return True, None
    except Exception as e:
        return False, [f"Error checking task completion: {str(e)}"]

try:
    input_data = json.load(sys.stdin)
    transcript_path = input_data.get("transcript_path", "")
    stop_hook_active = input_data.get("stop_hook_active", False)
    
    # Avoid infinite loops
    if stop_hook_active:
        sys.exit(0)
    
    # Check if task is complete
    is_complete, issues = check_task_completion(transcript_path)
    
    if not is_complete:
        # Return a JSON response to block stopping
        json_response = {
            "decision": "block",
            "reason": "The current task is not fully complete. Please address the following issues:\n" + 
                     "\n".join([f"- {issue}" for issue in issues]) +
                     "\n\nPlease fix these issues before moving to the next task."
        }
        print(json.dumps(json_response))
        sys.exit(0)  # Use exit code 0 with JSON response
    
    # Exit normally if task is complete
    sys.exit(0)
    
except Exception as e:
    print(f"Hook error: {str(e)}", file=sys.stderr)
    sys.exit(1)  # Non-blocking error