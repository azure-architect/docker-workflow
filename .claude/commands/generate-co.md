# Create Change Order

## Feature file: $ARGUMENTS

Generate a complete Change Order (CO) for general feature implementation with thorough research. Ensure maximum context preservation to enable self-validation, iterative refinement, and resilience against context loss. Read the feature file first to understand what needs to be created, how the examples provided help, and any other considerations.

The AI agent only gets the context you are appending to the Change Order and training data. Assume the AI agent has access to the codebase and the same knowledge cutoff as you, so it's important that your research findings are included or referenced in the Change Order. The Agent has Websearch capabilities, so pass URLs to documentation and examples.

## Research Process

1. **Codebase Analysis**
   - Search for similar features/patterns in the codebase
   - Identify files to reference in Change Order
   - Note existing conventions to follow
   - Check test patterns for validation approach
   - Map dependencies and component relationships

2. **External Research**
   - Search for similar features/patterns online
   - Library documentation (include specific URLs)
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls
   - Industry standards and architectural patterns

3. **Decision Documentation**
   - Document alternatives considered and why they were rejected
   - Note constraints that shaped the approach
   - Capture rationale behind key design decisions
   - Record any trade-offs being made

4. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?
   - Constraints or performance requirements?

## Change Order Generation

Using templates/co_template.md as template:

### Critical Context to Include and pass to the AI agent as part of the Change Order
- **Project Context**: Overall architecture and patterns relevant to this change
- **Dependencies**: All internal and external dependencies with versions
- **Documentation**: URLs with specific sections
- **Code Examples**: Real snippets from codebase
- **Gotchas**: Library quirks, version issues, edge cases
- **Patterns**: Existing approaches to follow
- **Decision History**: Previous decisions that influence this implementation

### Implementation Blueprint
- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- List tasks to be completed to fulfill the Change Order in the order they should be completed
- Identify potential failure points and mitigation strategies

### Validation Gates (Must be Executable) eg for python
```bash
# Syntax/Style
ruff check --fix && mypy .

# Unit Tests
uv run pytest tests/ -v
```

*** CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE CHANGE ORDER ***

*** ULTRATHINK ABOUT THE CHANGE ORDER AND PLAN YOUR APPROACH THEN START WRITING THE CHANGE ORDER ***

## Output
Save as: `pipeline/1-planned/{feature-name}.md`

## Quality Checklist
- [ ] All necessary context included for resilience against context loss
- [ ] Complete dependency map included
- [ ] Decision history and rationale documented
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented
- [ ] Edge cases identified

Score the Change Order on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude codes)

Remember: The goal is one-pass implementation success through comprehensive context preservation that is resilient to context window limitations.