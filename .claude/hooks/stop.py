#!/usr/bin/env python3
# Made executable via chmod +x
"""
Claude Code stop hook for comprehensive state capture and session analysis.
Runs whenever Claude concludes its response.
"""

import json
import sys
import os
import time
import re
import psutil
import shutil
from datetime import datetime
from pathlib import Path
import hashlib

# Configurable settings
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
ARTIFACTS_DIR = os.path.join(LOG_DIR, "artifacts")
SESSION_SUMMARY_DIR = os.path.join(LOG_DIR, "summaries")
TRANSCRIPTS_DIR = os.path.join(LOG_DIR, "transcripts")

def ensure_directories_exist():
    """Create necessary directories if they don't exist."""
    for directory in [LOG_DIR, ARTIFACTS_DIR, SESSION_SUMMARY_DIR, TRANSCRIPTS_DIR]:
        os.makedirs(directory, exist_ok=True)

def log_json(data, prefix="log"):
    """Log data to a JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join(LOG_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    return filepath

def extract_system_state():
    """Capture current system state information."""
    process = psutil.Process(os.getpid())
    return {
        "timestamp": datetime.now().isoformat(),
        "memory_usage_mb": process.memory_info().rss / (1024 * 1024),
        "cpu_percent": process.cpu_percent(),
        "open_files": len(process.open_files()),
        "threads": len(process.threads()),
        "system_time": time.time()
    }

def copy_transcript_to_project(transcript_path, session_id):
    """Copy the transcript file to the project's transcript directory."""
    if not os.path.exists(transcript_path):
        print(f"Transcript file not found: {transcript_path}", file=sys.stderr)
        return None
    
    # Copy to project transcript directory
    filename = f"{session_id}.jsonl"
    dest_path = os.path.join(TRANSCRIPTS_DIR, filename)
    
    try:
        shutil.copy2(transcript_path, dest_path)
        print(f"Transcript copied to project: {dest_path}", file=sys.stderr)
        return dest_path
    except Exception as e:
        print(f"Failed to copy transcript: {str(e)}", file=sys.stderr)
        return None

def parse_chat_transcript(transcript_path):
    """Parse the chat transcript to extract messages and tool calls."""
    if not os.path.exists(transcript_path):
        return {"error": f"Transcript file not found: {transcript_path}"}
    
    try:
        messages = []
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        message = json.loads(line)
                        messages.append(message)
                    except json.JSONDecodeError:
                        print(f"Error parsing transcript line: {line}", file=sys.stderr)
        
        return {
            "messages": messages,
            "message_count": len(messages)
        }
    except Exception as e:
        return {"error": f"Failed to parse transcript: {str(e)}"}

def extract_code_artifacts(transcript_data):
    """Extract code snippets and artifacts from the transcript."""
    artifacts = []
    
    if "messages" not in transcript_data:
        return []
    
    # Pattern to match code blocks in markdown
    code_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
    
    for message in transcript_data["messages"]:
        if message.get("role") == "assistant" and "content" in message:
            content = message["content"]
            
            # Find all code blocks
            matches = code_pattern.findall(content)
            for language, code in matches:
                language = language.strip() or "text"
                if code.strip():
                    artifact_id = hashlib.md5(code.encode()).hexdigest()[:10]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{language}_{artifact_id}_{timestamp}.{get_file_extension(language)}"
                    filepath = os.path.join(ARTIFACTS_DIR, filename)
                    
                    with open(filepath, "w") as f:
                        f.write(code)
                    
                    artifacts.append({
                        "language": language,
                        "size_bytes": len(code),
                        "path": filepath,
                        "id": artifact_id
                    })
    
    return artifacts

def get_file_extension(language):
    """Map language name to appropriate file extension."""
    extensions = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "html": "html",
        "css": "css",
        "json": "json",
        "bash": "sh",
        "shell": "sh",
        "sql": "sql",
        "rust": "rs",
        "go": "go",
        "ruby": "rb",
        "php": "php",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "csharp": "cs",
    }
    return extensions.get(language.lower(), "txt")

def extract_tool_calls(transcript_data):
    """Extract and analyze all tool calls from the transcript."""
    tool_calls = []
    
    if "messages" not in transcript_data:
        return []
    
    for message in transcript_data["messages"]:
        if message.get("role") == "assistant" and "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                tool_calls.append({
                    "id": tool_call.get("id"),
                    "type": tool_call.get("type"),
                    "function": {
                        "name": tool_call.get("function", {}).get("name"),
                        "arguments": tool_call.get("function", {}).get("arguments"),
                    }
                })
    
    # Count tools by type
    tool_stats = {}
    for call in tool_calls:
        function_name = call.get("function", {}).get("name")
        if function_name:
            tool_stats[function_name] = tool_stats.get(function_name, 0) + 1
    
    return {
        "calls": tool_calls,
        "count": len(tool_calls),
        "by_type": tool_stats
    }

def generate_session_summary(transcript_data, system_state, artifacts, tool_calls, project_transcript_path=None):
    """Generate a summary of the session."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "session_duration_seconds": None,  # Will calculate if possible
        "message_count": transcript_data.get("message_count", 0),
        "system_state": system_state,
        "artifacts_generated": len(artifacts),
        "tool_calls_count": tool_calls.get("count", 0),
        "tool_calls_by_type": tool_calls.get("by_type", {}),
    }
    
    # Add project transcript path if available
    if project_transcript_path:
        summary["project_transcript_path"] = project_transcript_path
    
    # Try to calculate session duration
    messages = transcript_data.get("messages", [])
    if len(messages) >= 2:
        try:
            # Assuming first message has a timestamp
            first_message_time = messages[0].get("created_at")
            last_message_time = messages[-1].get("created_at")
            
            if first_message_time and last_message_time:
                # Parse ISO format timestamps
                start_time = datetime.fromisoformat(first_message_time.replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(last_message_time.replace("Z", "+00:00"))
                duration = (end_time - start_time).total_seconds()
                summary["session_duration_seconds"] = duration
        except Exception as e:
            print(f"Failed to calculate session duration: {e}", file=sys.stderr)
    
    return summary

def save_session_summary(summary):
    """Save session summary to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_summary_{timestamp}.json"
    filepath = os.path.join(SESSION_SUMMARY_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(summary, f, indent=2)
    
    return filepath

def announce_completion():
    """Announce completion with text-to-speech."""
    try:
        # If you have a TTS script, call it here
        tts_script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "utils", 
            "speech.py"
        )
        
        if os.path.exists(tts_script_path):
            message = "All set and ready for your next step."
            os.system(f"python3 {tts_script_path} \"{message}\"")
    except Exception as e:
        print(f"Failed to announce completion: {e}", file=sys.stderr)

def main():
    """Main function to handle the stop hook."""
    # Ensure all necessary directories exist
    ensure_directories_exist()
    
    # Read input from stdin (Claude Code passes JSON)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Could not parse input as JSON", file=sys.stderr)
        sys.exit(1)
    
    # Log the raw input data
    log_json(input_data, prefix="stop")
    
    # Extract system state
    system_state = extract_system_state()
    
    # Get the transcript path and session ID from the input
    transcript_path = input_data.get("transcript_path")
    session_id = input_data.get("session_id")
    
    # Copy transcript to project directory
    project_transcript_path = copy_transcript_to_project(transcript_path, session_id)
    
    # Parse the chat transcript
    transcript_data = parse_chat_transcript(transcript_path)
    
    # Extract code artifacts
    artifacts = extract_code_artifacts(transcript_data)
    
    # Extract tool calls
    tool_calls = extract_tool_calls(transcript_data)
    
    # Generate session summary
    session_summary = generate_session_summary(
        transcript_data, 
        system_state, 
        artifacts, 
        tool_calls,
        project_transcript_path
    )
    
    # Save session summary
    summary_path = save_session_summary(session_summary)
    
    # Log success message
    print(f"Session state captured successfully.", file=sys.stderr)
    print(f"Transcript processed: {transcript_path}", file=sys.stderr)
    if project_transcript_path:
        print(f"Transcript copied to project: {project_transcript_path}", file=sys.stderr)
    print(f"Summary saved to: {summary_path}", file=sys.stderr)
    print(f"Artifacts extracted: {len(artifacts)}", file=sys.stderr)
    
    # Announce completion using TTS
    # announce_completion()
    
    # Exit with success
    sys.exit(0)

if __name__ == "__main__":
    main()