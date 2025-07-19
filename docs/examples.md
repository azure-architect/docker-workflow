# Practical Examples and Tutorials

This guide provides hands-on examples of building common Python applications using the template.

## 📚 Tutorial Series

### Tutorial 1: Building a REST API with Authentication

Let's build a complete REST API with user authentication using this template.

#### Step 1: Project Setup
```bash
# Copy template and initialize
cp -r /path/to/template my-api-project
cd my-api-project

python scripts/init_project.py \
    --project-name "secure-api" \
    --author-name "Your Name" \
    --author-email "your.email@example.com"

source .venv/bin/activate
```

#### Step 2: Add Dependencies
```bash
# Add web framework dependencies to pyproject.toml
```

Edit `pyproject.toml`:
```toml
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "pydantic>=2.4.0",
]
```

```bash
# Install new dependencies
pip install -e .[dev,test]
```

#### Step 3: Create Models
```python
# src/models.py
"""Data models for the API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserResponse(UserBase):
    """User response model."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Authentication token model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
```

#### Step 4: Create Authentication Service
```python
# src/auth.py
"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt


class AuthService:
    """Handles user authentication and JWT tokens."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        """Initialize authentication service."""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # In-memory user storage (use database in production)
        self.users: Dict[str, Dict[str, Any]] = {}
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user."""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user_data = {
            "id": len(self.users) + 1,
            "username": username,
            "email": email,
            "full_name": full_name,
            "hashed_password": self.hash_password(password),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        self.users[username] = user_data
        return user_data
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user."""
        user = self.users.get(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return user
    
    def create_access_token(self, data: Dict[str, Any], 
                           expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return username."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
```

#### Step 5: Create API Endpoints
```python
# src/api.py
"""FastAPI application."""

from datetime import timedelta
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .auth import AuthService
from .models import UserCreate, UserResponse, Token

# Initialize app and services
app = FastAPI(title="Secure API", version="1.0.0")
auth_service = AuthService("your-secret-key-here")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = auth_service.verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = auth_service.users.get(username)
    if user is None:
        raise credentials_exception
    
    return user


@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate) -> UserResponse:
    """Register a new user."""
    try:
        user_data = auth_service.create_user(
            username=user.username,
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        return UserResponse(**user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Login and get access token."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserResponse:
    """Get current user information."""
    return UserResponse(**current_user)


@app.get("/protected")
async def protected_route(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """Example protected route."""
    return {"message": f"Hello {current_user['username']}, this is a protected route!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Step 6: Write Comprehensive Tests
```python
# tests/test_auth.py
"""Tests for authentication service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.auth import AuthService


@pytest.fixture
def auth_service():
    """Create auth service for testing."""
    return AuthService("test-secret-key")


class TestAuthService:
    """Test authentication service."""
    
    def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "test_password"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed)
    
    def test_create_user_success(self, auth_service):
        """Test successful user creation."""
        user = auth_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert "hashed_password" in user
        assert user["is_active"] is True
        assert isinstance(user["created_at"], datetime)
    
    def test_create_user_duplicate(self, auth_service):
        """Test creating duplicate user raises error."""
        auth_service.create_user("testuser", "test@example.com", "password123")
        
        with pytest.raises(ValueError, match="Username already exists"):
            auth_service.create_user("testuser", "other@example.com", "password456")
    
    def test_authenticate_user_success(self, auth_service):
        """Test successful authentication."""
        auth_service.create_user("testuser", "test@example.com", "password123")
        
        user = auth_service.authenticate_user("testuser", "password123")
        assert user is not None
        assert user["username"] == "testuser"
    
    def test_authenticate_user_wrong_password(self, auth_service):
        """Test authentication with wrong password."""
        auth_service.create_user("testuser", "test@example.com", "password123")
        
        user = auth_service.authenticate_user("testuser", "wrongpassword")
        assert user is None
    
    def test_create_and_verify_token(self, auth_service):
        """Test token creation and verification."""
        token = auth_service.create_access_token({"sub": "testuser"})
        
        username = auth_service.verify_token(token)
        assert username == "testuser"
    
    def test_verify_invalid_token(self, auth_service):
        """Test verification of invalid token."""
        username = auth_service.verify_token("invalid_token")
        assert username is None
```

```python
# tests/test_api.py
"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api import app, auth_service


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_users():
    """Reset users before each test."""
    auth_service.users.clear()


class TestAPI:
    """Test API endpoints."""
    
    def test_register_user(self, client):
        """Test user registration."""
        response = client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["is_active"] is True
    
    def test_register_duplicate_user(self, client):
        """Test registering duplicate user."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # First registration should succeed
        response1 = client.post("/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration should fail
        response2 = client.post("/register", json=user_data)
        assert response2.status_code == 400
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        # Login
        response = client.post("/token", data={
            "username": "testuser",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post("/token", data={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_protected_route_with_token(self, client):
        """Test accessing protected route with valid token."""
        # Register and login
        client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        login_response = client.post("/token", data={
            "username": "testuser",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Access protected route
        response = client.get("/protected", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        assert "Hello testuser" in response.json()["message"]
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get("/protected")
        assert response.status_code == 401
```

#### Step 7: Run Quality Checks
```bash
# Run all quality checks
./scripts/qa_check.sh

# Run specific checks
pytest tests/ -v
mypy src/
black --check .
pylint src/
```

#### Step 8: Test the API
```bash
# Start the server
python -m src.api

# Test with curl (in another terminal)
# Register user
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"

# Use token for protected route
curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Tutorial 2: Building a Data Processing Pipeline

#### Step 1: Setup Project
```bash
cp -r /path/to/template data-pipeline
cd data-pipeline

python scripts/init_project.py \
    --project-name "data-pipeline" \
    --author-name "Your Name" \
    --author-email "your.email@example.com"
```

#### Step 2: Add Data Dependencies
```toml
# Add to pyproject.toml dependencies
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pydantic>=2.4.0",
    "sqlalchemy>=2.0.0",
    "aiofiles>=23.0.0",
]
```

#### Step 3: Create Data Models
```python
# src/models.py
"""Data models for processing pipeline."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class DataRecord(BaseModel):
    """Individual data record."""
    id: Optional[int] = None
    timestamp: datetime
    value: float
    category: str
    metadata: Optional[dict] = None


class ProcessingConfig(BaseModel):
    """Configuration for data processing."""
    batch_size: int = Field(default=1000, gt=0)
    max_retries: int = Field(default=3, ge=0)
    validation_strict: bool = True
    output_format: str = Field(default="csv", regex="^(csv|json|parquet)$")


class ProcessingResult(BaseModel):
    """Result of data processing operation."""
    processed_count: int
    failed_count: int
    duration_seconds: float
    output_file: str
    errors: List[str] = []
```

#### Step 4: Create Data Processor
```python
# src/processor.py
"""Data processing pipeline."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Iterator, Optional
import pandas as pd
import logging

from .models import DataRecord, ProcessingConfig, ProcessingResult

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes data records in batches."""
    
    def __init__(self, config: ProcessingConfig) -> None:
        """Initialize processor with configuration."""
        self.config = config
        self.processed_count = 0
        self.failed_count = 0
        self.errors: List[str] = []
    
    async def process_file(self, input_file: Path, output_dir: Path) -> ProcessingResult:
        """Process data file and save results."""
        start_time = datetime.utcnow()
        
        try:
            # Read data
            records = await self._read_data(input_file)
            
            # Process in batches
            processed_records = []
            async for batch in self._batch_processor(records):
                processed_records.extend(batch)
            
            # Save results
            output_file = await self._save_results(processed_records, output_dir)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                processed_count=self.processed_count,
                failed_count=self.failed_count,
                duration_seconds=duration,
                output_file=str(output_file),
                errors=self.errors
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.errors.append(str(e))
            raise
    
    async def _read_data(self, file_path: Path) -> List[DataRecord]:
        """Read data from file."""
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        records = []
        for _, row in df.iterrows():
            try:
                record = DataRecord(
                    timestamp=pd.to_datetime(row['timestamp']),
                    value=float(row['value']),
                    category=str(row['category']),
                    metadata=row.get('metadata')
                )
                records.append(record)
            except Exception as e:
                self.failed_count += 1
                self.errors.append(f"Invalid record: {e}")
                if self.config.validation_strict:
                    raise
        
        return records
    
    async def _batch_processor(self, records: List[DataRecord]) -> Iterator[List[DataRecord]]:
        """Process records in batches."""
        for i in range(0, len(records), self.config.batch_size):
            batch = records[i:i + self.config.batch_size]
            processed_batch = await self._process_batch(batch)
            yield processed_batch
    
    async def _process_batch(self, batch: List[DataRecord]) -> List[DataRecord]:
        """Process a single batch of records."""
        processed = []
        
        for record in batch:
            try:
                # Simulate processing (add your logic here)
                processed_record = await self._process_record(record)
                processed.append(processed_record)
                self.processed_count += 1
                
            except Exception as e:
                self.failed_count += 1
                self.errors.append(f"Processing error for record {record.id}: {e}")
                if self.config.validation_strict:
                    raise
        
        return processed
    
    async def _process_record(self, record: DataRecord) -> DataRecord:
        """Process individual record."""
        # Simulate async processing
        await asyncio.sleep(0.001)
        
        # Example processing: normalize value
        normalized_value = (record.value - 50) / 100
        
        return DataRecord(
            id=record.id,
            timestamp=record.timestamp,
            value=normalized_value,
            category=record.category.upper(),
            metadata={
                **(record.metadata or {}),
                "processed_at": datetime.utcnow().isoformat(),
                "original_value": record.value
            }
        )
    
    async def _save_results(self, records: List[DataRecord], output_dir: Path) -> Path:
        """Save processed records to file."""
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if self.config.output_format == "csv":
            output_file = output_dir / f"processed_{timestamp}.csv"
            df = pd.DataFrame([record.dict() for record in records])
            df.to_csv(output_file, index=False)
            
        elif self.config.output_format == "json":
            output_file = output_dir / f"processed_{timestamp}.json"
            data = [record.dict() for record in records]
            df = pd.DataFrame(data)
            df.to_json(output_file, orient="records", date_format="iso")
            
        else:
            raise ValueError(f"Unsupported output format: {self.config.output_format}")
        
        return output_file
```

#### Step 5: Create CLI Interface
```python
# src/cli.py
"""Command-line interface for data processor."""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional

from .processor import DataProcessor
from .models import ProcessingConfig


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


async def main() -> None:
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Data Processing Pipeline")
    parser.add_argument("input_file", type=Path, help="Input data file")
    parser.add_argument("--output-dir", type=Path, default="output", 
                       help="Output directory")
    parser.add_argument("--batch-size", type=int, default=1000,
                       help="Batch size for processing")
    parser.add_argument("--format", choices=["csv", "json"], default="csv",
                       help="Output format")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    config = ProcessingConfig(
        batch_size=args.batch_size,
        output_format=args.format
    )
    
    processor = DataProcessor(config)
    
    try:
        result = await processor.process_file(args.input_file, args.output_dir)
        
        print("✅ Processing completed successfully!")
        print(f"📊 Processed: {result.processed_count} records")
        print(f"❌ Failed: {result.failed_count} records")
        print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
        print(f"📁 Output: {result.output_file}")
        
        if result.errors:
            print(f"⚠️  Errors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 6: Create Sample Data and Tests
```python
# tests/test_processor.py
"""Tests for data processor."""

import pytest
import asyncio
import tempfile
from pathlib import Path
import pandas as pd
from datetime import datetime

from src.processor import DataProcessor
from src.models import ProcessingConfig, DataRecord


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'timestamp': ['2024-01-01T10:00:00', '2024-01-01T11:00:00'],
        'value': [25.5, 75.2],
        'category': ['type_a', 'type_b'],
    })


@pytest.fixture
def temp_files():
    """Create temporary files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        yield temp_path


@pytest.mark.asyncio
class TestDataProcessor:
    """Test data processor functionality."""
    
    async def test_process_csv_file(self, sample_data, temp_files):
        """Test processing CSV file."""
        # Create input file
        input_file = temp_files / "input.csv"
        sample_data.to_csv(input_file, index=False)
        
        # Process file
        config = ProcessingConfig(batch_size=1, output_format="csv")
        processor = DataProcessor(config)
        
        result = await processor.process_file(input_file, temp_files)
        
        # Verify results
        assert result.processed_count == 2
        assert result.failed_count == 0
        assert result.duration_seconds > 0
        assert Path(result.output_file).exists()
        
        # Verify output data
        output_df = pd.read_csv(result.output_file)
        assert len(output_df) == 2
        assert all(cat.isupper() for cat in output_df['category'])
    
    async def test_batch_processing(self, temp_files):
        """Test batch processing functionality."""
        # Create larger dataset
        large_data = pd.DataFrame({
            'timestamp': [f'2024-01-01T{i:02d}:00:00' for i in range(10)],
            'value': list(range(10)),
            'category': ['test'] * 10,
        })
        
        input_file = temp_files / "large_input.csv"
        large_data.to_csv(input_file, index=False)
        
        # Process with small batch size
        config = ProcessingConfig(batch_size=3, output_format="json")
        processor = DataProcessor(config)
        
        result = await processor.process_file(input_file, temp_files)
        
        assert result.processed_count == 10
        assert result.failed_count == 0
    
    async def test_error_handling(self, temp_files):
        """Test error handling with invalid data."""
        # Create invalid data
        invalid_data = pd.DataFrame({
            'timestamp': ['invalid-date', '2024-01-01T10:00:00'],
            'value': ['not-a-number', 50],
            'category': ['test', 'test'],
        })
        
        input_file = temp_files / "invalid_input.csv"
        invalid_data.to_csv(input_file, index=False)
        
        # Process with non-strict validation
        config = ProcessingConfig(validation_strict=False)
        processor = DataProcessor(config)
        
        result = await processor.process_file(input_file, temp_files)
        
        assert result.failed_count > 0
        assert len(result.errors) > 0
```

### Tutorial 3: Building a CLI Tool

Create a comprehensive command-line tool using the template:

```python
# src/cli_tool.py
"""Advanced CLI tool example."""

import click
import logging
from pathlib import Path
from typing import Optional

from .processor import DataProcessor
from .models import ProcessingConfig


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), help='Log file path')
def cli(verbose: bool, log_file: Optional[str]) -> None:
    """Data Processing CLI Tool."""
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              default='output', help='Output directory')
@click.option('--batch-size', '-b', default=1000, help='Batch size')
@click.option('--format', '-f', type=click.Choice(['csv', 'json']), 
              default='csv', help='Output format')
async def process(input_file: Path, output_dir: Path, batch_size: int, format: str) -> None:
    """Process data file."""
    config = ProcessingConfig(
        batch_size=batch_size,
        output_format=format
    )
    
    processor = DataProcessor(config)
    result = await processor.process_file(input_file, output_dir)
    
    click.echo(f"✅ Processed {result.processed_count} records")
    click.echo(f"📁 Output: {result.output_file}")


if __name__ == '__main__':
    cli()
```

## 🎯 Best Practices Summary

From these examples, follow these patterns:

1. **Start with Models**: Define your data structures first
2. **Write Tests Early**: TDD approach saves time
3. **Use Type Hints**: Helps with IDE support and catches errors
4. **Async When Appropriate**: For I/O bound operations
5. **Error Handling**: Always handle exceptions gracefully
6. **Configuration**: Use Pydantic models for config validation
7. **Logging**: Add proper logging throughout
8. **CLI Design**: Use click for professional CLI interfaces

This template provides the foundation for any Python project while enforcing best practices through tooling and Claude Code integration!