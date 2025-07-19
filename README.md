# Claude Code Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A streamlined Claude Code integration template with advanced hooks for context engineering, transcript preservation, and a structured development pipeline.

## ✨ Features

- **🧠 Context Engineering**: Preserve conversation context and session history
- **🪝 Advanced Hooks**: Pre/post tool execution and session completion hooks
- **📝 Transcript Storage**: Automatically save conversation transcripts in your project
- **💻 Code Extraction**: Extract and save code artifacts from conversations
- **🔍 Quality Validation**: Enforce coding standards and best practices
- **📋 Pipeline Workflow**: Structured development process with clear stages
- **🔄 Context Resilience**: Built-in safeguards against context loss
- **🐳 Docker Integration**: CLI tools and API wrapper for container management (CLI/API only)

## 🚀 Quick Start

### Adding to an Existing Project

```bash
# In your existing project directory
git clone https://github.com/your-username/claude-code.git .claude

# Optionally remove git history
rm -rf .claude/.git

# Add to .gitignore
echo ".claude/logs/" >> .gitignore
echo ".claude/settings.local.json" >> .gitignore
```

### Initializing a New Project

```bash
# Create a new project with Claude Code integration
/init "Project Name" "Project Description"
```

The `/init` command will:
- Create a CLAUDE.md file with project context
- Set up the basic project structure
- Configure initial settings based on project type

## 📁 Claude Code Structure

```
.claude/
├── hooks/                 # Hook implementations
│   ├── pre_tool_use.py    # Validates before file changes
│   ├── post_tool_use.py   # Formats after file changes
│   ├── stop.py            # Manages session completion
│   └── task_completion.py # Verifies task completion
├── commands/              # Reusable command templates
│   ├── generate-co.md     # Generate Change Order from requirements
│   ├── execute-co.md      # Implement a Change Order
│   ├── implement.md       # Implement a component from specifications
│   ├── test.md            # Create tests for a component
│   ├── document.md        # Document a component
│   └── restore-context.md # Recover context after context loss
├── logs/                  # Generated logs and artifacts (gitignored)
│   ├── transcripts/       # Conversation history
│   ├── artifacts/         # Extracted code
│   └── summaries/         # Session summaries
├── settings.json          # Shared configuration
└── settings.local.json    # Local overrides (gitignored)

pipeline/                  # Development pipeline structure
├── 1-planned/             # COs that have been generated but not approved
├── 2-in-progress/         # Approved COs currently being executed
├── 3-testing/             # Implemented COs undergoing testing
├── 4-documented/          # Completed COs with documentation
└── 5-archived/            # Fully completed COs

templates/                 # Template files for various artifacts
└── co_template.md         # Comprehensive Change Order template
```

## 🔄 Development Pipeline Workflow

Claude Code uses a structured pipeline approach to manage development tasks through distinct stages:

1. **Planning Stage (1-planned/)**
   - Use `/generate-co <requirements>` to create a Change Order (CO) markdown document
   - The CO includes detailed requirements, implementation plan, and validation criteria
   - Review the CO and approve it to move to the next stage

2. **Implementation Stage (2-in-progress/)**
   - Use `/execute-co <co-file>` to implement the approved CO
   - Implementation follows the plan outlined in the CO
   - Code is created with proper structure, documentation, and error handling
   - The CO file is updated with implementation details

3. **Testing Stage (3-testing/)**
   - Use `/test-co <co-file>` to create and run tests for the implementation
   - Tests verify that the implementation meets all requirements
   - The CO file is updated with test results and coverage information
   - Failing tests may send the CO back to the implementation stage

4. **Documentation Stage (4-documented/)**
   - Use `/document-co <co-file>` to create comprehensive documentation
   - Documentation includes usage examples, configuration options, and API references
   - The CO file is updated with documentation details
   - Once documented, the feature is considered complete

5. **Archive Stage (5-archived/)**
   - Completed COs are moved to the archive for future reference
   - Archived COs provide valuable context for related features

This pipeline structure ensures:
- Clear tracking of development progress
- Preservation of context throughout the development process
- Consistent quality across all stages
- Smooth transitions between planning, implementation, testing, and documentation

## 🛡️ Context Resilience

Claude Code implements a comprehensive context resilience strategy to protect against context loss:

### Enhanced Change Orders
- Change Orders are designed to be self-contained context capsules
- Each CO includes comprehensive information about:
  - Project context relevant to the change
  - Complete dependency mapping
  - Decision history and rationale
  - Implementation details and considerations

### Context Restoration
- Use `/restore-context` to quickly recover from context loss
- The command analyzes:
  - Pipeline state and active tasks
  - Recent transcripts and session summaries
  - Project structure and key files
  - Implementation history and decisions
- Produces a detailed context report to bring Claude up to speed

### Transcript Preservation
- Session transcripts are automatically saved
- Stop hooks generate comprehensive session summaries
- Code artifacts are extracted and preserved
- The pipeline structure maintains task state information

By combining these approaches, Claude Code ensures that even if context is lost between sessions, it can be efficiently restored without significant loss of productivity.

## ⚙️ Hook System

### PreToolUse Hook
- Validates file content before changes are made
- Enforces coding standards (type annotations, security practices)
- Checks for required elements based on file type and purpose
- Blocks changes that would compromise context quality

### PostToolUse Hook
- Automatically formats code after changes
- Performs type checking
- Ensures consistent style across project files
- Can block tool completion if issues are detected

### Stop Hook
- Captures comprehensive session state
- Extracts and logs code artifacts from conversations
- Copies transcripts to the project directory
- Generates session summaries for reference

### Task Completion Hook
- Validates task completion criteria
- Checks test coverage
- Ensures documentation standards
- Can block task completion if requirements aren't met

## 🔧 Configuration

The `settings.json` file contains the core configuration:

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(mkdir -p *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/pre_tool_use.py"
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

You can override settings locally by creating a `.claude/settings.local.json` file (which won't be committed to git).

## 📚 Context Engineering Approach

This template implements a context engineering approach for AI-assisted project management, treating context as a deliberately engineered resource rather than an accidental byproduct.

The key principles include:
- **Context as Infrastructure**: Treat project context as a foundational resource
- **Systematic Discovery**: Use structured approaches to gather project understanding
- **Adaptive Planning**: Build plans that evolve while preserving core context
- **Continuous Context Management**: Maintain and update context throughout execution
- **Pipeline-Based Workflow**: Move tasks through clear stages to maintain context
- **Context Resilience**: Build redundancy into context preservation systems

## 🔄 Usage with Projects

This template works with projects of any language or structure - it's not limited to Python projects. Simply clone it into any project directory to add Claude Code integration.

## 📄 License

This project is licensed under the MIT License.

---

**Enhance your development workflow with Claude Code! 🚀**