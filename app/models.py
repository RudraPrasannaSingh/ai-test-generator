from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript" 
    CSHARP = "csharp"

class Framework(str, Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    XUNIT = "xunit"

class TestRequest(BaseModel):
    code: str = Field(..., description="Source code to generate tests for")
    language: Language = Language.PYTHON
    framework: Framework = Framework.PYTEST
    include_edge_cases: bool = True

class TestResponse(BaseModel):
    generated_tests: str
    test_count: int
    confidence_score: float
    processing_time_ms: int
    suggestions: List[str] = []
