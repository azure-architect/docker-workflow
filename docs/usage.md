# Usage Guide: Step-by-Step Coding with Python Template

This comprehensive guide walks you through the complete development workflow using this Python project template with Claude Code integration.

## 📋 Table of Contents

1. [Initial Project Setup](#initial-project-setup)
2. [Daily Development Workflow](#daily-development-workflow)
3. [Claude Code Integration](#claude-code-integration)
4. [Code Development Process](#code-development-process)
5. [Testing Workflow](#testing-workflow)
6. [Quality Assurance Process](#quality-assurance-process)
7. [Deployment Process](#deployment-process)
8. [Troubleshooting](#troubleshooting)

## 🚀 Initial Project Setup

### Step 1: Copy Template and Initialize

```bash
# Copy template to your project location
cp -r /Volumes/Samsung/mo/projects/ai-automation/claude-code /path/to/your/new-project
cd /path/to/your/new-project

# Run initialization script
python scripts/init_project.py \
    --project-name "my-awesome-project" \
    --author-name "Your Name" \
    --author-email "your.email@example.com"
```

**What this does:**
- ✅ Customizes all template files with your project details
- ✅ Initializes git repository with initial commit
- ✅ Creates `.venv/` virtual environment
- ✅ Installs all development dependencies
- ✅ Sets up pre-commit hooks
- ✅ Runs initial validation checks

### Step 2: Verify Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify installation
python -c "import src; print('✅ Package imports successfully')"
pytest --version
black --version
mypy --version

# Run initial tests (should pass)
pytest
```

### Step 3: Configure Development Environment

```bash
# Optional: Configure your IDE
# For VS Code, the template works out of the box
# For PyCharm, set interpreter to .venv/bin/python

# Optional: Set up additional environment variables
echo "DEBUG=true" > .env
echo "LOG_LEVEL=DEBUG" >> .env
```

## 🔄 Daily Development Workflow

### Morning Routine (Start of Work Session)

```bash
# 1. Navigate to project
cd /path/to/your/project

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Pull latest changes (if team project)
git pull origin main

# 4. Update dependencies if needed
pip install -e .[dev,test,docs]

# 5. Run quick health check
pytest --lf  # Run only last failed tests
```

### Feature Development Cycle

#### Step 1: Plan Your Feature
```bash
# Create feature branch
git checkout -b feature/user-authentication

# Optional: Use Claude Code planning
# Open Claude Code and describe your feature
# Use /implement command for structured planning
```

#### Step 2: Write Code
```bash
# Create your module in src/
touch src/auth.py

# Start with basic structure (Claude Code will help enforce patterns)
```

**Example: Creating an authentication module**

```python
# src/auth.py
"""User authentication module."""

from typing import Optional, Dict, Any
import hashlib
import secrets
from datetime import datetime, timedelta


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class UserAuthenticator:
    """Handles user authentication and token management."""
    
    def __init__(self, secret_key: str) -> None:
        """Initialize authenticator with secret key."""
        self.secret_key = secret_key
        self.tokens: Dict[str, Dict[str, Any]] = {}
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure algorithm."""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', 
                                  password.encode('utf-8'), 
                                  salt.encode('utf-8'), 
                                  100000).hex() + ':' + salt
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        password_hash, salt = hashed.split(':')
        return secrets.compare_digest(
            password_hash,
            hashlib.pbkdf2_hmac('sha256',
                               password.encode('utf-8'),
                               salt.encode('utf-8'),
                               100000).hex()
        )
    
    def create_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create authentication token for user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        self.tokens[token] = {
            'user_id': user_id,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate token and return user_id if valid."""
        if token not in self.tokens:
            return None
            
        token_data = self.tokens[token]
        if datetime.utcnow() > token_data['expires_at']:
            del self.tokens[token]
            return None
            
        return token_data['user_id']
```

#### Step 3: Write Tests Immediately

```bash
# Create test file
touch tests/test_auth.py
```

```python
# tests/test_auth.py
"""Tests for authentication module."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.auth import UserAuthenticator, AuthenticationError


@pytest.fixture
def authenticator():
    """Create authenticator instance for testing."""
    return UserAuthenticator("test-secret-key")


class TestUserAuthenticator:
    """Test cases for UserAuthenticator class."""
    
    def test_hash_password_creates_unique_hashes(self, authenticator):
        """Test that same password creates different hashes."""
        password = "test_password"
        hash1 = authenticator.hash_password(password)
        hash2 = authenticator.hash_password(password)
        
        assert hash1 != hash2
        assert ':' in hash1  # Should contain salt separator
        assert ':' in hash2
    
    def test_verify_password_success(self, authenticator):
        """Test successful password verification."""
        password = "test_password"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(password, hashed) is True
    
    def test_verify_password_failure(self, authenticator):
        """Test failed password verification."""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = authenticator.hash_password(password)
        
        assert authenticator.verify_password(wrong_password, hashed) is False
    
    def test_create_token_returns_string(self, authenticator):
        """Test token creation returns string."""
        token = authenticator.create_token("user123")
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token in authenticator.tokens
    
    def test_validate_token_success(self, authenticator):
        """Test successful token validation."""
        user_id = "user123"
        token = authenticator.create_token(user_id)
        
        validated_user_id = authenticator.validate_token(token)
        assert validated_user_id == user_id
    
    def test_validate_token_invalid(self, authenticator):
        """Test validation of invalid token."""
        result = authenticator.validate_token("invalid_token")
        assert result is None
    
    @patch('src.auth.datetime')
    def test_validate_token_expired(self, mock_datetime, authenticator):
        """Test validation of expired token."""
        # Mock current time for token creation
        creation_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = creation_time
        
        token = authenticator.create_token("user123", expires_in=3600)
        
        # Mock time 2 hours later (past expiration)
        expired_time = creation_time + timedelta(hours=2)
        mock_datetime.utcnow.return_value = expired_time
        
        result = authenticator.validate_token(token)
        assert result is None
        assert token not in authenticator.tokens  # Should be cleaned up
```

#### Step 4: Run Quality Checks

```bash
# Run tests first
pytest tests/test_auth.py -v

# Run type checking
mypy src/auth.py

# Format code
black src/auth.py tests/test_auth.py
isort src/auth.py tests/test_auth.py

# Run all quality checks
pre-commit run --all-files
```

#### Step 5: Commit Your Changes

```bash
# Add files
git add src/auth.py tests/test_auth.py

# Commit (pre-commit hooks will run automatically)
git commit -m "Add user authentication module

- Implement UserAuthenticator class with password hashing
- Add secure token generation and validation
- Include comprehensive test suite with 100% coverage
- Follow security best practices for password storage"

# Push to remote
git push origin feature/user-authentication
```

## 🤖 Claude Code Integration

### Using Claude Code Commands

#### `/implement` Command
```bash
# In Claude Code, use the implement command for structured development
/implement "Create a user authentication system with password hashing and token management"
```

**Claude Code will:**
- Analyze requirements
- Plan implementation with proper architecture
- Create code following template patterns
- Enforce type annotations and documentation
- Follow security best practices

#### `/test` Command
```bash
# Generate comprehensive test suite
/test "src/auth.py"
```

**Claude Code will:**
- Analyze your code structure
- Generate unit tests for all methods
- Create integration tests where appropriate
- Include edge cases and error conditions
- Achieve 90%+ test coverage

#### `/document` Command
```bash
# Generate documentation
/document "src/auth.py"
```

**Claude Code will:**
- Generate comprehensive docstrings
- Create usage examples
- Document configuration options
- Include troubleshooting guides

### Working with Claude Code Hooks

The template includes validation hooks that run before code is written:

**Pre-tool Validation:**
- ✅ Enforces 500-line maximum per file
- ✅ Requires return type annotations
- ✅ Blocks `os.system()` usage (security)
- ✅ Requires SSL for email clients
- ✅ Validates file-specific patterns

**Example: Hook preventing insecure code**
```python
# This would be blocked by hooks:
import os
os.system("rm -rf /")  # ❌ Blocked: Use subprocess instead

# This is allowed:
import subprocess
subprocess.run(["rm", "file.txt"], check=True)  # ✅ Secure pattern
```

## 🧪 Testing Workflow

### Test-Driven Development (TDD)

#### Step 1: Write Failing Test
```python
# tests/test_new_feature.py
def test_feature_not_implemented_yet():
    """Test for feature we haven't built yet."""
    from src.new_module import NewFeature
    
    feature = NewFeature()
    result = feature.process_data("test")
    assert result == "processed: test"
```

#### Step 2: Run Test (Should Fail)
```bash
pytest tests/test_new_feature.py -v
# Should show ImportError or AttributeError
```

#### Step 3: Implement Minimum Code
```python
# src/new_module.py
class NewFeature:
    def process_data(self, data: str) -> str:
        return f"processed: {data}"
```

#### Step 4: Run Test (Should Pass)
```bash
pytest tests/test_new_feature.py -v
# Should pass now
```

#### Step 5: Refactor and Improve
```python
# Improve implementation while keeping tests green
```

### Testing Best Practices

#### Use Test Markers
```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_database_integration():
    """Integration test requiring database."""
    pass

@pytest.mark.slow
def test_performance_benchmark():
    """Slow test for performance checking."""
    pass
```

#### Run Different Test Categories
```bash
# Run only fast unit tests
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py::TestUserAuthenticator::test_hash_password
```

#### Mock External Dependencies
```python
from unittest.mock import Mock, patch

def test_api_call():
    """Test function that makes API calls."""
    with patch('src.module.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "success"}
        
        result = api_function()
        assert result["status"] == "success"
        mock_get.assert_called_once()
```

## 🔍 Quality Assurance Process

### Daily Quality Checks

```bash
# Full quality assurance pipeline
./scripts/qa_check.sh  # Create this script

# Or run individual tools:
black --check .          # Code formatting
isort --check-only .     # Import sorting
mypy src                 # Type checking
pylint src              # Code linting
bandit -r src           # Security scanning
pytest --cov=src        # Test coverage
```

### Creating QA Script
```bash
# Create scripts/qa_check.sh
touch scripts/qa_check.sh
chmod +x scripts/qa_check.sh
```

```bash
#!/bin/bash
# scripts/qa_check.sh - Complete quality assurance check

set -e  # Exit on any error

echo "🔍 Running Quality Assurance Checks..."

echo "📝 Checking code formatting..."
black --check .

echo "📦 Checking import sorting..."
isort --check-only .

echo "🔍 Type checking..."
mypy src

echo "🔍 Linting code..."
pylint src

echo "🔒 Security scanning..."
bandit -r src

echo "🧪 Running tests with coverage..."
pytest --cov=src --cov-report=term-missing --cov-fail-under=90

echo "✅ All quality checks passed!"
```

### Pre-commit Integration

```bash
# Install pre-commit hooks (done automatically by init script)
pre-commit install

# Run on all files
pre-commit run --all-files

# Test hooks
git add .
git commit -m "Test commit"  # Hooks will run automatically
```

## 🚀 Deployment Process

### Local Development to Production

#### Step 1: Prepare for Deployment
```bash
# Ensure all tests pass
pytest

# Build package
python -m build

# Check package
twine check dist/*
```

#### Step 2: Version Management
```python
# Update version in src/__init__.py
__version__ = "0.2.0"

# Update version in pyproject.toml
version = "0.2.0"
```

#### Step 3: Create Release
```bash
# Tag release
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push tags
git push origin --tags
```

### Docker Deployment

#### Development Container
```bash
# Build development image
docker build -t my-project:dev .

# Run with development mount
docker-compose up -d

# Execute commands in container
docker-compose exec app pytest
docker-compose exec app black .
```

#### Production Container
```bash
# Build production image
docker build -t my-project:prod --target production .

# Run production container
docker run -d -p 8000:8000 my-project:prod
```

### CI/CD with GitHub Actions

The template includes complete CI/CD pipeline:

```yaml
# .github/workflows/ci.yml automatically:
# ✅ Tests on multiple Python versions (3.9-3.12)
# ✅ Tests on multiple OS (Ubuntu, Windows, macOS)
# ✅ Runs all quality checks
# ✅ Builds and uploads packages
# ✅ Uploads coverage reports
```

**Deployment Workflow:**
1. **Push to feature branch** → Run tests
2. **Create pull request** → Full CI pipeline
3. **Merge to main** → Deploy to staging
4. **Create release tag** → Deploy to production

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or install in development mode
pip install -e .
```

#### Test Failures
```bash
# Problem: Tests failing after changes
# Solution: Debug specific test
pytest tests/test_module.py::test_function -v -s --pdb

# Run with debugging
pytest --pdb-trace
```

#### Pre-commit Hook Failures
```bash
# Problem: Hooks failing on commit
# Solution: Run hooks manually and fix
pre-commit run --all-files

# Fix specific issues
black .          # Fix formatting
isort .          # Fix imports
mypy src         # Fix type issues
```

#### Docker Issues
```bash
# Problem: Container build failures
# Solution: Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache

# Debug container
docker-compose run --rm app bash
```

#### Performance Issues
```bash
# Problem: Slow tests
# Solution: Profile and optimize
pytest --durations=10  # Show slowest tests

# Run parallel tests
pytest -n auto  # Requires pytest-xdist
```

### Getting Help

#### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
pytest -v -s

# Use Python debugger
import pdb; pdb.set_trace()
```

#### Claude Code Support
```bash
# Use Claude Code for debugging
# Describe your issue and get targeted help
# Use /document command for explanations
# Use /implement command for fixes
```

### Emergency Recovery

#### Restore from Git
```bash
# Undo last commit
git reset --hard HEAD~1

# Restore specific file
git checkout HEAD -- src/module.py

# Clean working directory
git clean -fd
```

#### Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,test,docs]
```

---

## 🎯 Summary: Complete Development Workflow

1. **Setup**: Copy template → Run init script → Verify setup
2. **Plan**: Create feature branch → Plan with Claude Code
3. **Code**: Write code → Write tests → Run quality checks
4. **Review**: Commit changes → Push branch → Create PR
5. **Deploy**: Merge to main → Tag release → Deploy

This workflow ensures:
- ✅ High code quality through automated tools
- ✅ Comprehensive testing with good coverage
- ✅ Security best practices enforcement
- ✅ Consistent development patterns
- ✅ Smooth deployment process

**Happy coding with your Python template! 🚀**