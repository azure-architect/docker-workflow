# Development Guide

This guide provides detailed instructions for developers working with this Python project template.

## Initial Setup

### 1. Clone and Initialize

```bash
# Copy template to new project
cp -r /path/to/template /path/to/new/project
cd /path/to/new/project

# Initialize project
python scripts/init_project.py \
    --project-name "your-project-name" \
    --author-name "Your Name" \
    --author-email "your.email@example.com"
```

### 2. Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify installation
pip list
python -c "import src; print('Success!')"
```

## Development Workflow

### Code Writing

1. **Write code in `src/`** with proper type annotations
2. **Add tests in `tests/`** with good coverage
3. **Document public APIs** with comprehensive docstrings
4. **Follow naming conventions** as defined in the style guide

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run tests matching pattern
pytest -k "test_pattern"

# Run only fast tests (exclude slow markers)
pytest -m "not slow"
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy src

# Linting
pylint src

# Security scanning
bandit -r src

# All quality checks at once
pre-commit run --all-files
```

## Development Patterns

### Type Annotations

All functions must have return type annotations:

```python
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items}

def optional_value(flag: bool) -> Optional[str]:
    """Return a value or None based on flag."""
    return "value" if flag else None
```

### Error Handling

Use proper exception handling patterns:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_operation(data: str) -> Optional[int]:
    """Safely convert string to integer."""
    try:
        return int(data)
    except ValueError as e:
        logger.warning(f"Failed to convert {data}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

### Testing Patterns

Write comprehensive tests with fixtures:

```python
import pytest
from unittest.mock import Mock, patch

def test_function_behavior(sample_data):
    """Test function with fixture data."""
    result = my_function(sample_data)
    assert result is not None
    assert len(result) > 0

@pytest.mark.slow
def test_integration_behavior():
    """Test that requires external resources."""
    # Integration test code here
    pass

def test_with_mock():
    """Test with mocked dependencies."""
    with patch('src.module.external_call') as mock_call:
        mock_call.return_value = "mocked"
        result = function_under_test()
        assert result == "expected"
        mock_call.assert_called_once()
```

### Documentation

Document all public APIs:

```python
def complex_function(data: List[Dict[str, Any]], 
                    options: Optional[Dict[str, bool]] = None) -> ProcessedResult:
    """Process complex data with optional configuration.
    
    Args:
        data: List of dictionaries containing raw data
        options: Optional configuration dict with processing flags
            - validate: Whether to validate input (default: True)
            - strict: Whether to use strict mode (default: False)
    
    Returns:
        ProcessedResult containing processed data and metadata
    
    Raises:
        ValueError: If data is empty or invalid
        ProcessingError: If processing fails
    
    Example:
        >>> data = [{"name": "test", "value": 42}]
        >>> result = complex_function(data, {"validate": True})
        >>> result.status
        'success'
    """
```

## Docker Development

### Basic Usage

```bash
# Build development image
docker build -t my-project .

# Run container
docker-compose up -d

# Execute commands in container
docker-compose exec app bash
docker-compose exec app pytest
docker-compose exec app black .
```

### Database Development

Uncomment database services in `docker-compose.yml`:

```bash
# Start with database
docker-compose up -d postgres

# Run migrations (if using Django/SQLAlchemy)
docker-compose exec app python manage.py migrate
```

## CI/CD Pipeline

### GitHub Actions

The CI pipeline runs on:
- **Push to main/develop**
- **Pull requests**
- **Multiple Python versions** (3.9, 3.10, 3.11, 3.12)
- **Multiple OS** (Ubuntu, Windows, macOS)

### Pipeline Steps

1. **Code Quality**: black, isort, mypy, pylint
2. **Security**: bandit scanning
3. **Testing**: pytest with coverage
4. **Build**: Package building and artifact upload

### Local CI Simulation

```bash
# Run the same checks as CI locally
black --check .
isort --check-only .
mypy src
pylint src
bandit -r src
pytest --cov=src
```

## Claude Code Integration

### Command Templates

- **`/document <component>`**: Generate documentation
- **`/implement <task>`**: Create implementations
- **`/test <component>`**: Generate test suites

### Validation Hooks

Pre-tool hooks enforce:
- **500-line file limit**
- **Return type annotations**
- **Security patterns** (no `os.system()`)
- **SSL requirements** for network code

### Best Practices

- Use the Claude Code command templates for consistency
- Let hooks guide code quality improvements
- Follow the patterns established in `.claude/commands/`

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

**Test failures:**
```bash
# Run specific test with verbose output
pytest tests/test_failing.py -v -s
```

**Pre-commit hook failures:**
```bash
# Fix formatting issues
black .
isort .

# Run hooks manually
pre-commit run --all-files
```

**Docker build issues:**
```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache
```

### Performance Optimization

**Slow tests:**
```bash
# Profile test execution
pytest --durations=10

# Run only fast tests
pytest -m "not slow"
```

**Large file handling:**
```bash
# Check file sizes
find . -type f -size +1M -not -path "./.git/*" -not -path "./.venv/*"
```

## Advanced Configuration

### Custom Tool Configuration

Edit `pyproject.toml` to customize tool behavior:

```toml
[tool.black]
line-length = 100  # Increase line length

[tool.mypy]
strict = true  # Enable strict mode

[tool.pytest.ini_options]
addopts = [
    "--strict-markers",
    "--verbose",
    "--tb=short",  # Shorter tracebacks
]
```

### Environment Variables

Create `.env` file for development:

```env
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://user:pass@localhost/db
```

Load in code:

```python
import os
from pathlib import Path

# Load .env file
env_file = Path.cwd() / ".env"
if env_file.exists():
    # Use python-dotenv or similar
    pass
```

## Contributing

1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** following development patterns
4. **Add tests** with good coverage
5. **Run quality checks**: `pre-commit run --all-files`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push branch**: `git push origin feature/amazing-feature`
8. **Create Pull Request**

---

This development guide ensures consistent, high-quality Python development with comprehensive tooling and Claude Code integration.