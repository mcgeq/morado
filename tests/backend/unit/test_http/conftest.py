"""Pytest configuration for HTTP client tests."""

import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))
