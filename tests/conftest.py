"""Pytest configuration and fixtures for ChildDiary Export tests."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import tkinter as tk


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_api_base_url():
    """Base URL for mocked API endpoints."""
    return "https://app.childdiary.net"


@pytest.fixture
def root_window():
    """Create a Tkinter root window for GUI tests."""
    # Skip if tkinter is not available
    pytest.importorskip("tkinter")
    
    # Create window off-screen to avoid visible flash
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
