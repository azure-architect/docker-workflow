# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This is a Python-based AI automation project. Use these commands:

### Code Quality
- `black src/` - Format Python code
- `isort src/` - Sort imports 
- `mypy src/` - Type checking
- `pylint src/` - Linting
- `pytest` - Run tests
- `python test:*` - Run specific test patterns

### Python Environment
- `PYTHONPATH` is automatically set to include `src/` directory
- Use `python scripts/monitor_csv_processing.py --monitor` for CSV monitoring tasks

### Docker Operations
- `docker compose up` - Start services
- `docker exec <container>` - Execute commands in containers

## Project Architecture

### Configuration Structure
- `.claude/settings.json` - Main Claude Code configuration
- `.claude/settings.local.json` - Local overrides and additional permissions
- `.claude/hooks/` - Pre/post tool execution hooks with validation
- `.claude/commands/` - Reusable command templates for documentation, implementation, and testing

### Hook System
The project uses a sophisticated hook system that validates code before writing:

#### Pre-Tool Validation (`.claude/hooks/pre_tool_use.py`)
- Enforces 500-line maximum file length
- Requires SSL imports for email clients
- Blocks `os.system()` usage (requires subprocess instead)
- Validates return type annotations on functions
- File-type specific validations for .py, .sql, .md files

#### Command Templates
- `/document <component>` - Generate comprehensive documentation
- `/implement <task>` - Create component implementations with proper architecture
- `/test <component>` - Generate pytest test suites with 90%+ coverage

### Development Patterns
- Use dependency injection patterns
- Implement proper error handling and logging
- Follow PEP 8 conventions
- Keep methods under 50 lines
- Include comprehensive docstrings and type annotations
- Use `docs/tasks/` directory for task specifications

### Security Considerations
- Email clients must use SSL connections
- Avoid shell injection via `os.system()`
- Use subprocess for system operations
- Redis CLI access is permitted for data operations

## Additional Directories
- `./docs/tasks/` - Task specification documents

## Documentation Reference
- Local Claude Code documentation: `/Volumes/Samsung/mo/knowledge/docs/Claude Code`