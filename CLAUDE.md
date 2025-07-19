# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code integration template that implements a structured development pipeline with advanced context engineering. The project provides a systematic approach to managing development tasks through distinct stages with comprehensive context preservation.

## Development Commands

### Core Workflow Commands
```bash
# Generate a Change Order from requirements
/generate-co <requirements-file>

# Execute an approved Change Order
/execute-co <co-file>

# Test implementation
/test-co <co-file>

# Document completed implementation
/document-co <co-file>

# Restore context after context loss
/restore-context
```

### Code Quality Commands
```bash
# Format Python code
black .

# Type checking
mypy .

# Linting
pylint .

# Import sorting
isort .

# Run tests
pytest .
```

### Docker Commands
```bash
# Docker operations are permitted for development
docker build -t <image-name> .
docker run <container-options>
```

## Architecture

### Pipeline Structure
The project uses a 5-stage development pipeline:

1. **1-planned/**: Generated Change Orders awaiting approval
2. **2-in-progress/**: Approved Change Orders under implementation  
3. **3-testing/**: Implementations undergoing testing
4. **4-documented/**: Completed implementations with documentation
5. **5-archived/**: Fully completed Change Orders

### Change Order System
- **Change Orders (COs)** are self-contained context capsules that preserve all necessary information for implementation
- Each CO follows the template in `templates/co_template.md`
- COs include project context, dependencies, decision history, and validation criteria
- This system ensures context resilience against context window limitations

### Hook System
The project implements comprehensive hooks for quality control:

- **PreToolUse**: Validates file content before changes (`.claude/hooks/pre_tool_use.py`)
- **PostToolUse**: Formats code and performs checks after changes (`.claude/hooks/post_tool_use.py`)  
- **Stop**: Captures session state and preserves transcripts (`.claude/hooks/stop.py`)

## Context Engineering Principles

### Context as Infrastructure
- Project context is treated as a foundational resource requiring deliberate engineering
- Change Orders serve as context preservation vehicles
- Pipeline structure maintains task state across sessions

### Context Resilience Strategy
- Use `/restore-context` to recover from context loss
- Session transcripts are automatically preserved in `.claude/logs/`
- Code artifacts are extracted and stored for reference
- Pipeline state provides task tracking continuity

### Implementation Approach
- Always start with comprehensive research and codebase analysis
- Document decisions and alternatives in Change Orders
- Follow existing patterns and conventions identified in the codebase
- Include executable validation gates in all Change Orders

## File Structure Conventions

```
.claude/
├── commands/           # Reusable command templates
├── hooks/             # Quality control hooks  
├── logs/              # Generated artifacts (gitignored)
└── settings.json      # Configuration

pipeline/              # Development pipeline stages
├── 1-planned/
├── 2-in-progress/
├── 3-testing/
├── 4-documented/
└── 5-archived/

templates/
└── co_template.md     # Change Order template
```

## Quality Standards

### Change Order Requirements
- Must include comprehensive project context
- Document all dependencies with versions
- Provide executable validation gates
- Reference existing codebase patterns
- Include decision history and rationale

### Code Standards
- Follow existing project conventions
- Include proper error handling
- Maintain context preservation throughout implementation
- Ensure one-pass implementation success through comprehensive planning

## Environment Configuration

- **PYTHONPATH**: Includes `./src` for Python imports
- **Permissions**: Git, Docker, Python tools, and file operations are allowed
- **Additional Directories**: `./docs/tasks/` is accessible for extended operations