import pytest
from app.api.v1.endpoints.health import health_check
from app.main import root

def test_health_endpoint():
    result = health_check()
    assert result["status"] == "healthy"
    assert "InterviewIQ AI" in result["project"]
    assert result["version"] == "1.0.0"

def test_root_endpoint():
    result = root()
    assert "InterviewIQ AI" in result["message"]
    assert "docs" in result
    assert "health" in result
