# Setting Up Claude Code Docker Workflow in Projects

This guide explains how to integrate the Claude Code Docker Workflow into new or existing projects.

## Quick Start Options

### Option 1: Clone as New Project (Recommended for New Projects)

```bash
# Clone the repository as your new project
git clone https://github.com/azure-architect/docker-workflow.git my-new-project
cd my-new-project

# Remove the existing git history
rm -rf .git

# Initialize as your own repository
git init
git add .
git commit -m "Initial commit with Claude Code Docker Workflow"

# Add your own remote (if you have one)
git remote add origin https://github.com/yourusername/my-new-project.git
git push -u origin main
```

### Option 2: Add to Existing Project

```bash
# In your existing project root
cd /path/to/your/project

# Add as a submodule (keeps it updatable)
git submodule add https://github.com/azure-architect/docker-workflow.git .claude-docker
git submodule update --init --recursive

# Or copy specific components manually
curl -L https://github.com/azure-architect/docker-workflow/archive/main.tar.gz | tar xz
cp -r docker-workflow-main/.claude .
cp -r docker-workflow-main/docs .
cp -r docker-workflow-main/templates .
cp docker-workflow-main/docker_*.py .
rm -rf docker-workflow-main
```

### Option 3: Minimal Setup (Just Claude Code Hooks)

```bash
# For projects that only need Claude Code integration without Docker
cd /path/to/your/project

# Download just the .claude directory
svn export https://github.com/azure-architect/docker-workflow/trunk/.claude

# Or use sparse checkout
git init temp-claude
cd temp-claude
git remote add origin https://github.com/azure-architect/docker-workflow.git
git sparse-checkout init
git sparse-checkout set .claude
git pull origin main
cp -r .claude ../.
cd ..
rm -rf temp-claude
```

## Post-Setup Configuration

### 1. Update .gitignore

Add these entries to your `.gitignore`:

```bash
# Claude Code artifacts
.claude/logs/
.claude/settings.local.json

# Docker workflow temporary files
n8n-deploy/
*-deploy/
pipeline/1-planned/*.md
pipeline/2-in-progress/*.md
pipeline/3-testing/*.md

# Environment files (if not already ignored)
.env
.env.local
```

### 2. Customize Configuration

Create `.claude/settings.local.json` for project-specific overrides:

```json
{
  "docker": {
    "host": "your-server:2375",
    "critical_containers": ["your-db", "your-cache"]
  },
  "project": {
    "name": "My Project",
    "type": "web-app"
  }
}
```

### 3. Initialize CLAUDE.md

Create a `CLAUDE.md` file for your project context:

```bash
cat > CLAUDE.md << 'EOF'
# Project Context

## Overview
[Your project description]

## Architecture
[Key architectural decisions]

## Development Workflow
- Using Claude Code Docker Workflow
- Remote Docker host: [your-server]
- Deployment target: /resources/[project-name]

## Key Commands
- `python docker_control.py health` - Check Docker connection
- `python docker_dashboard.py` - Monitor containers
- `/generate-co` - Create Change Orders
- `/restore-context` - Restore session context

## Environment Variables
See `/resources/.env` on deployment server

EOF
```

### 4. Set Up Remote Docker Access

Configure Docker access in your environment:

```bash
# Option A: Environment variable
export DOCKER_HOST=tcp://192.168.0.135:2375

# Option B: Add to .bashrc or .zshrc
echo 'export DOCKER_HOST=tcp://192.168.0.135:2375' >> ~/.bashrc

# Option C: Create alias
alias docker-remote='docker -H tcp://192.168.0.135:2375'
```

## Project Structure After Setup

Your project should have this structure:

```
your-project/
├── .claude/                    # Claude Code integration
│   ├── hooks/                  # Validation and automation hooks
│   ├── commands/               # Reusable command templates
│   └── settings.json           # Configuration
├── docs/                       # Documentation
│   ├── docker-integration.md   # Docker workflow guide
│   ├── env-file-management.md  # Environment patterns
│   └── actual-workflow.md      # What actually works
├── pipeline/                   # Development pipeline
│   ├── 1-planned/
│   ├── 2-in-progress/
│   ├── 3-testing/
│   ├── 4-documented/
│   └── 5-archived/
├── templates/                  # Template files
│   └── co_template.md
├── docker_control.py           # Docker CLI tool
├── docker_dashboard.py         # Docker monitoring
├── CLAUDE.md                   # Project context
└── [your project files]
```

## First Steps After Setup

### 1. Test Docker Connection

```bash
python docker_control.py health
```

Expected output:
```
✅ Docker daemon is accessible at 192.168.0.135:2375
Docker version: 27.5.0
API version: 1.47
OS: linux
Architecture: x86_64
```

### 2. Create Your First Change Order

```bash
# In Claude Code
/generate-co Create a PostgreSQL database service for development
```

### 3. Set Up Environment File

Create a template `.env` for your project:

```bash
# Project Configuration
PROJECT_NAME=my-project
PROJECT_ENV=development

# Port Allocations
POSTGRES_EXTERNAL_PORT=5432
REDIS_EXTERNAL_PORT=6379
APP_EXTERNAL_PORT=8080

# Database Configuration
POSTGRES_USER=appuser
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=appdb

# API Keys (add as needed)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
```

## Updating the Workflow

If you used Option 2 (submodule), you can update to the latest version:

```bash
cd .claude-docker
git pull origin main
cd ..
git add .claude-docker
git commit -m "Update Claude Code Docker Workflow"
```

## Troubleshooting

### Common Issues

1. **Docker connection fails**
   - Check `DOCKER_HOST` environment variable
   - Verify remote Docker API is enabled
   - Check firewall rules for port 2375

2. **Hooks not running**
   - Ensure Python is installed
   - Check hook permissions: `chmod +x .claude/hooks/*.py`
   - Verify `.claude/settings.json` paths

3. **Missing dependencies**
   ```bash
   pip install docker rich
   ```

### Getting Help

- Check [actual-workflow.md](./actual-workflow.md) for what currently works
- Review [docker-troubleshooting.md](./docker-troubleshooting.md) for Docker issues
- See [env-file-management.md](./env-file-management.md) for configuration patterns

## Best Practices

1. **Always use Change Orders** for significant changes
2. **Document deployment patterns** in CLAUDE.md
3. **Use the pipeline workflow** to track progress
4. **Centralize configuration** in `/resources/.env`
5. **Test locally** before deploying to remote Docker

## Next Steps

- [ ] Customize `.claude/settings.json` for your project
- [ ] Set up your remote Docker environment
- [ ] Create initial Change Orders for your infrastructure
- [ ] Configure your `/resources/.env` file
- [ ] Test deployment workflow with a simple service

Remember: The workflow is designed to be adapted to your needs. Start with the basics and add complexity as needed.