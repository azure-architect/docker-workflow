# Troubleshooting Guide

This guide helps you resolve common issues when using the Python project template with Claude Code.

## 🚨 Common Issues and Solutions

### Project Setup Issues

#### Issue: Script execution permission denied
```bash
$ python scripts/init_project.py
-bash: python: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x scripts/init_project.py

# Or run with python directly
python3 scripts/init_project.py --project-name "my-project" --author-name "Your Name" --author-email "you@example.com"
```

#### Issue: Virtual environment not found
```bash
$ source .venv/bin/activate
-bash: .venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Create virtual environment manually
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -e .[dev,test,docs]
```

#### Issue: Module import errors
```bash
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Option 1: Install in development mode
pip install -e .

# Option 2: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Option 3: Add to shell profile (permanent)
echo 'export PYTHONPATH="${PYTHONPATH}:${PWD}/src"' >> ~/.bashrc
source ~/.bashrc
```

### Development Environment Issues

#### Issue: Pre-commit hooks failing
```bash
$ git commit -m "My changes"
black....................................................................Failed
```

**Solution:**
```bash
# Run black manually to see issues
black . --check --diff

# Fix formatting issues
black .

# Fix imports
isort .

# Run all pre-commit hooks manually
pre-commit run --all-files

# Try commit again
git commit -m "My changes"
```

#### Issue: Type checking errors with mypy
```bash
$ mypy src
src/module.py:15: error: Function is missing a return type annotation
```

**Solution:**
```python
# Before (causes error):
def my_function(data):
    return data.upper()

# After (fixed):
def my_function(data: str) -> str:
    return data.upper()
```

#### Issue: Test failures after setup
```bash
$ pytest
tests/test_module.py::test_function FAILED
```

**Solution:**
```bash
# Run tests with verbose output
pytest -v -s

# Run specific test file
pytest tests/test_module.py -v

# Run with debugger on failure
pytest --pdb

# Check test dependencies
pip install -e .[test]
```

### Claude Code Integration Issues

#### Issue: Hook validation blocking code
```bash
File validation issues:
- Functions should include return type annotations
```

**Solution:**
```python
# Add return type annotations to all functions
def process_data(items: List[str]) -> Dict[str, int]:
    """Process items and return counts."""
    return {item: len(item) for item in items}

# For functions that don't return anything
def log_message(message: str) -> None:
    """Log a message."""
    print(message)
```

#### Issue: File length validation blocking large files
```bash
File validation issues:
- File exceeds 500 lines maximum length
```

**Solution:**
```python
# Break large files into smaller modules

# Before: large_module.py (600 lines)
# After:
# ├── large_module/
#     ├── __init__.py
#     ├── core.py (200 lines)
#     ├── utils.py (200 lines)
#     └── helpers.py (200 lines)
```

#### Issue: Security validation blocking subprocess calls
```bash
File validation issues:
- Avoid using os.system() - use subprocess instead
```

**Solution:**
```python
# Before (blocked):
import os
os.system("curl https://api.example.com")

# After (allowed):
import subprocess
result = subprocess.run(
    ["curl", "https://api.example.com"], 
    capture_output=True, 
    text=True, 
    check=True
)
```

#### Issue: Claude Code commands not working
```bash
/implement "Create user authentication"
# No response or error
```

**Solution:**
```bash
# Ensure you're in Claude Code interactive mode
# Commands should work in the Claude Code interface

# If using CLI, ensure proper permissions
# Check .claude/settings.json for command permissions

# Try simpler commands first
/document "src/auth.py"
```

### Docker and Containerization Issues

#### Issue: Docker build failing
```bash
$ docker build -t my-project .
ERROR: failed to solve: failed to compute cache key
```

**Solution:**
```bash
# Clean Docker cache
docker system prune -f

# Build without cache
docker build --no-cache -t my-project .

# Check Dockerfile syntax
docker build --progress=plain -t my-project .
```

#### Issue: Docker compose service not starting
```bash
$ docker-compose up
ERROR: Service 'app' failed to build
```

**Solution:**
```bash
# Check docker-compose.yml syntax
docker-compose config

# Build services individually
docker-compose build app

# Check logs
docker-compose logs app

# Start services in foreground for debugging
docker-compose up --no-deps app
```

#### Issue: Permission issues in Docker container
```bash
$ docker-compose exec app pytest
Permission denied: '/app/tests'
```

**Solution:**
```dockerfile
# In Dockerfile, ensure proper user permissions
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app
```

### Testing and Quality Assurance Issues

#### Issue: Coverage below threshold
```bash
$ pytest --cov=src --cov-fail-under=90
FAILED: coverage below 90%
```

**Solution:**
```bash
# Check coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Add tests for uncovered lines
# Focus on untested functions and branches

# Use Claude Code to generate tests
# /test "src/uncovered_module.py"
```

#### Issue: Slow test execution
```bash
$ pytest
========== 50 passed in 45.23s ==========
```

**Solution:**
```bash
# Profile slow tests
pytest --durations=10

# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"

# Use fixtures to reduce setup time
@pytest.fixture(scope="session")
def expensive_setup():
    # Setup once per test session
    pass
```

#### Issue: Linting errors
```bash
$ pylint src
src/module.py:15:0: C0103: Invalid name "x" (invalid-name)
```

**Solution:**
```bash
# Fix specific pylint issues
# For invalid names, use descriptive names
x = data  # Bad
user_data = data  # Good

# Disable specific warnings if needed
# pylint: disable=invalid-name

# Configure pylint in pyproject.toml
[tool.pylint.messages_control]
disable = [
    "too-few-public-methods",
    "invalid-name",
]
```

### Performance Issues

#### Issue: Import time too slow
```bash
$ python -c "import src; print('OK')"
# Takes 5+ seconds
```

**Solution:**
```python
# Use lazy imports
def expensive_function():
    import heavy_library  # Import only when needed
    return heavy_library.process()

# Reduce import dependencies
# Move heavy imports to function level
# Use importlib for dynamic imports
```

#### Issue: Memory usage too high
```bash
# Process using excessive memory
```

**Solution:**
```python
# Use generators instead of lists
def process_large_data():
    for item in large_dataset:  # Generator
        yield process_item(item)
    # Instead of: return [process_item(item) for item in large_dataset]

# Use context managers for resources
with open('large_file.txt') as f:
    for line in f:  # Process line by line
        process_line(line)

# Profile memory usage
import tracemalloc
tracemalloc.start()
# ... your code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
```

### Deployment Issues

#### Issue: Package build failing
```bash
$ python -m build
ERROR: Invalid version string
```

**Solution:**
```bash
# Check version format in src/__init__.py
__version__ = "0.1.0"  # Good: semantic versioning

# Check version in pyproject.toml matches
[project]
version = "0.1.0"

# Validate package structure
python -m build --check
```

#### Issue: GitHub Actions failing
```bash
# CI pipeline failing on specific Python version
```

**Solution:**
```yaml
# Check .github/workflows/ci.yml
# Ensure all Python versions are supported

# Add debugging to workflow
- name: Debug environment
  run: |
    python --version
    pip list
    pytest --version

# Check specific test failures
pytest --tb=short -v
```

## 🔧 Debug Mode and Logging

### Enable Debug Logging
```python
# In your code
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message here")
```

### Environment Variables for Debugging
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Python debugging
export PYTHONPATH="${PWD}/src"
export PYTHONDONTWRITEBYTECODE=1

# Pytest debugging
export PYTEST_CURRENT_TEST=1
```

### Interactive Debugging
```python
# Add breakpoints in code
import pdb; pdb.set_trace()

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()

# Run pytest with debugger
pytest --pdb --pdb-trace
```

## 🚨 Emergency Recovery

### Restore Clean State
```bash
# Reset git repository
git reset --hard HEAD
git clean -fd

# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,test,docs]

# Reset pre-commit hooks
pre-commit uninstall
pre-commit install
```

### Backup and Recovery
```bash
# Create backup before major changes
tar -czf backup-$(date +%Y%m%d).tar.gz \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .

# Restore from backup
tar -xzf backup-20240101.tar.gz
```

## 📞 Getting Help

### Self-Diagnosis Checklist
- [ ] Virtual environment activated?
- [ ] Dependencies installed correctly?
- [ ] PYTHONPATH includes src/?
- [ ] Files have proper permissions?
- [ ] Git repository initialized?
- [ ] Pre-commit hooks installed?

### Debug Information Collection
```bash
# Collect system information
python --version
pip --version
git --version
docker --version

# Collect project information
pip list
pytest --version
black --version
mypy --version

# Collect environment information
echo $PYTHONPATH
echo $VIRTUAL_ENV
env | grep PYTHON
```

### Community Resources
- **Claude Code Documentation**: Check official docs
- **GitHub Issues**: Search for similar problems
- **Stack Overflow**: Tag questions with `python`, `pytest`, `claude-code`
- **Python Discord**: Get help from the community

### Creating Bug Reports
When reporting issues, include:
```
## Environment
- OS: macOS 13.0
- Python: 3.11.5
- Template Version: 1.0.0

## Steps to Reproduce
1. Run `python scripts/init_project.py`
2. Execute `pytest`
3. Error occurs

## Expected Behavior
Tests should pass

## Actual Behavior
Error: ModuleNotFoundError

## Additional Context
[Paste relevant logs, error messages, or configuration]
```

## 💡 Prevention Tips

### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash
# Update dependencies
pip install --upgrade pip
pip install -e .[dev,test,docs] --upgrade

# Update pre-commit hooks
pre-commit autoupdate

# Run quality checks
./scripts/qa_check.sh

# Update documentation
/document "Recent changes"
```

### Best Practices
1. **Commit Often**: Small, focused commits
2. **Test Early**: Write tests as you code
3. **Document Changes**: Keep docs updated
4. **Monitor Quality**: Run QA checks regularly
5. **Backup Work**: Use git branches liberally
6. **Stay Updated**: Keep dependencies current

This troubleshooting guide should help you resolve most common issues. Remember: when in doubt, start with the basics (virtual environment, dependencies, permissions) and work your way up to more complex issues! 🚀