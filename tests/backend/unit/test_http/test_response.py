"""Unit tests for HttpResponse class.

Tests the response wrapper functionality including property access,
JSON parsing, JSONPath extraction, header access, and file saving.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

import pytest

from morado.common.http.exceptions import HttpRequestError, JSONPathError
from morado.common.http.response import HttpResponse


class TestHttpResponse:
    """Test suite for HttpResponse class."""

    def test_status_code_property(self):
        """Test that status_code property returns the correct value."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.status_code == 200

    def test_headers_property(self):
        """Test that headers property returns a dictionary."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json", "X-Custom": "value"}
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.headers == {"Content-Type": "application/json", "X-Custom": "value"}

    def test_text_property(self):
        """Test that text property returns the response text."""
        mock_response = Mock()
        mock_response.text = "Hello, World!"
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.text == "Hello, World!"

    def test_content_property(self):
        """Test that content property returns bytes."""
        mock_response = Mock()
        mock_response.content = b"Binary content"
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.content == b"Binary content"

    def test_request_time_property(self):
        """Test that request_time property returns the correct value."""
        mock_response = Mock()
        
        response = HttpResponse(mock_response, 1.234)
        
        assert response.request_time == 1.234

    def test_json_parsing_success(self):
        """Test successful JSON parsing."""
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value", "number": 42}
        
        response = HttpResponse(mock_response, 0.5)
        result = response.json()
        
        assert result == {"key": "value", "number": 42}

    def test_json_parsing_failure(self):
        """Test JSON parsing with invalid JSON."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        
        response = HttpResponse(mock_response, 0.5)
        
        with pytest.raises(json.JSONDecodeError):
            response.json()

    def test_is_success_with_2xx_status(self):
        """Test is_success returns True for 2xx status codes."""
        for status_code in [200, 201, 204, 299]:
            mock_response = Mock()
            mock_response.status_code = status_code
            
            response = HttpResponse(mock_response, 0.5)
            
            assert response.is_success() is True

    def test_is_success_with_non_2xx_status(self):
        """Test is_success returns False for non-2xx status codes."""
        for status_code in [199, 300, 400, 404, 500]:
            mock_response = Mock()
            mock_response.status_code = status_code
            
            response = HttpResponse(mock_response, 0.5)
            
            assert response.is_success() is False

    def test_raise_for_status_success(self):
        """Test raise_for_status does not raise for 2xx status."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        response = HttpResponse(mock_response, 0.5)
        
        # Should not raise
        response.raise_for_status()

    def test_raise_for_status_error(self):
        """Test raise_for_status raises for error status codes."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "https://example.com/api"
        
        response = HttpResponse(mock_response, 0.5)
        
        with pytest.raises(HttpRequestError) as exc_info:
            response.raise_for_status()
        
        assert exc_info.value.status_code == 404
        assert "404" in str(exc_info.value)

    def test_jsonpath_extraction_single_match(self):
        """Test JSONPath extraction with single match."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"name": "John", "age": 30}}
        
        response = HttpResponse(mock_response, 0.5)
        result = response.jsonpath("$.data.name")
        
        assert result == "John"

    def test_jsonpath_extraction_multiple_matches(self):
        """Test JSONPath extraction with multiple matches."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"name": "Item1"},
                {"name": "Item2"},
                {"name": "Item3"}
            ]
        }
        
        response = HttpResponse(mock_response, 0.5)
        result = response.jsonpath("$.items[*].name")
        
        assert result == ["Item1", "Item2", "Item3"]

    def test_jsonpath_extraction_no_match(self):
        """Test JSONPath extraction with no matches."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"name": "John"}}
        
        response = HttpResponse(mock_response, 0.5)
        result = response.jsonpath("$.nonexistent")
        
        assert result is None

    def test_jsonpath_invalid_expression(self):
        """Test JSONPath with invalid expression."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "value"}
        
        response = HttpResponse(mock_response, 0.5)
        
        with pytest.raises(JSONPathError) as exc_info:
            response.jsonpath("$[invalid")
        
        assert exc_info.value.path == "$[invalid"

    def test_jsonpath_non_json_response(self):
        """Test JSONPath extraction on non-JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "doc", 0)
        
        response = HttpResponse(mock_response, 0.5)
        
        with pytest.raises(JSONPathError) as exc_info:
            response.jsonpath("$.data")
        
        assert "non-JSON response" in str(exc_info.value)

    def test_get_header_existing(self):
        """Test getting an existing header."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json", "X-Custom": "value"}
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.get_header("Content-Type") == "application/json"
        assert response.get_header("X-Custom") == "value"

    def test_get_header_case_insensitive(self):
        """Test that header access is case-insensitive."""
        mock_response = Mock()
        # Mock the case-insensitive behavior of requests headers
        mock_headers = Mock()
        mock_headers.get.side_effect = lambda name, default=None: {
            "content-type": "application/json",
            "Content-Type": "application/json",
            "CONTENT-TYPE": "application/json",
        }.get(name, default)
        mock_response.headers = mock_headers
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.get_header("content-type") == "application/json"
        assert response.get_header("Content-Type") == "application/json"
        assert response.get_header("CONTENT-TYPE") == "application/json"

    def test_get_header_nonexistent(self):
        """Test getting a non-existent header."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.get_header("X-Nonexistent") is None

    def test_get_header_with_default(self):
        """Test getting a non-existent header with default value."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        
        response = HttpResponse(mock_response, 0.5)
        
        assert response.get_header("X-Nonexistent", "default") == "default"

    def test_save_to_file_success(self):
        """Test saving response content to a file."""
        mock_response = Mock()
        mock_response.content = b"File content here"
        # Mock iter_content to return chunks
        mock_response.iter_content = Mock(return_value=[b"File content here"])
        
        response = HttpResponse(mock_response, 0.5)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_file.txt"
            response.save_to_file(str(filepath))
            
            assert filepath.exists()
            assert filepath.read_bytes() == b"File content here"

    def test_save_to_file_creates_directories(self):
        """Test that save_to_file creates parent directories."""
        mock_response = Mock()
        mock_response.content = b"Content"
        # Mock iter_content to return chunks
        mock_response.iter_content = Mock(return_value=[b"Content"])
        
        response = HttpResponse(mock_response, 0.5)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "nested" / "file.txt"
            response.save_to_file(str(filepath))
            
            assert filepath.exists()
            assert filepath.read_bytes() == b"Content"

    def test_save_to_file_failure(self):
        """Test save_to_file with invalid path."""
        mock_response = Mock()
        mock_response.content = b"Content"
        
        response = HttpResponse(mock_response, 0.5)
        
        # Try to save to a path with invalid characters (Windows)
        # Use a null byte which is invalid on all platforms
        with pytest.raises(IOError):
            response.save_to_file("invalid\x00path.txt")
