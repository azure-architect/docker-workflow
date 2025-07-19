# Claude Code Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A streamlined Claude Code integration template with advanced hooks for context engineering and transcript preservation.

## ✨ Features

- **🧠 Context Engineering**: Preserve conversation context and session history
- **🪝 Advanced Hooks**: Pre/post tool execution and session completion hooks
- **📝 Transcript Storage**: Automatically save conversation transcripts in your project
- **💻 Code Extraction**: Extract and save code artifacts from conversations
- **🔍 Quality Validation**: Enforce coding standards and best practices

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

## 📁 Claude Code Structure

```
.claude/
├── hooks/                 # Hook implementations
│   ├── pre_tool_use.py    # Validates before file changes
│   ├── post_tool_use.py   # Formats after file changes
│   ├── stop.py            # Manages session completion
│   └── task_completion.py # Verifies task completion
├── commands/              # Reusable command templates
├── logs/                  # Generated logs and artifacts (gitignored)
│   ├── transcripts/       # Conversation history
│   ├── artifacts/         # Extracted code
│   └── summaries/         # Session summaries
├── settings.json          # Shared configuration
└── settings.local.json    # Local overrides (gitignored)
```

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

## 🔄 Usage with Projects

This template works with projects of any language or structure - it's not limited to Python projects. Simply clone it into any project directory to add Claude Code integration.

## 📄 License

This project is licensed under the MIT License.

---

**Enhance your development workflow with Claude Code! 🚀**