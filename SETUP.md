# Quick Setup Guide

## For New Projects

```bash
git clone https://github.com/azure-architect/docker-workflow.git my-project
cd my-project
rm -rf .git
git init
```

## For Existing Projects

```bash
cd your-project
curl -L https://github.com/azure-architect/docker-workflow/archive/main.tar.gz | tar xz
cp -r docker-workflow-main/.claude .
cp -r docker-workflow-main/docs .
cp -r docker-workflow-main/templates .
cp docker-workflow-main/docker_*.py .
rm -rf docker-workflow-main
```

## Essential Configuration

1. **Add to .gitignore:**
   ```
   .claude/logs/
   .claude/settings.local.json
   *-deploy/
   .env
   ```

2. **Create CLAUDE.md:**
   ```markdown
   # Project Context
   
   ## Overview
   [Your project description]
   
   ## Docker Configuration
   Remote host: 192.168.0.135:2375
   Deployment path: /resources/[project-name]
   ```

3. **Test Docker:**
   ```bash
   python docker_control.py health
   ```

See [docs/setup-new-project.md](docs/setup-new-project.md) for detailed instructions.