import pytest
from src.fetch_data import filter_entries

# Sample data mimicking the API structure
MOCK_DATA = {
    "count": 3,
    "entries": [
        {"API": "Cat Facts", "Description": "Daily cat facts", "Category": "Animals"},
        {"API": "Dogs", "Description": "Cheer yourself up with random dog images", "Category": "Animals"},
        {"API": "Public APIs", "Description": "A collective list", "Category": "Development"}
    ]
}

MOCK_DATA_EMPTY = {"count": 0, "entries": []}
MOCK_DATA_NO_ANIMALS = {
    "count": 1,
    "entries": [
        {"API": "Public APIs", "Description": "A collective list", "Category": "Development"}
    ]
}


def test_filter_entries_standard():
    """Test filtering with standard data."""
    result = filter_entries(MOCK_DATA, category="Animals")
    assert len(result) == 2
    assert all(entry['Category'] == "Animals" for entry in result)


def test_filter_entries_different_category():
    """Test filtering for a different category."""
    result = filter_entries(MOCK_DATA, category="Development")
    assert len(result) == 1
    assert result[0]['Category'] == "Development"


def test_filter_entries_no_match():
    """Test filtering when no entries match."""
    result = filter_entries(MOCK_DATA_NO_ANIMALS, category="Animals")
    assert len(result) == 0


def test_filter_entries_empty_input():
    """Test filtering with empty input data."""
    result = filter_entries(MOCK_DATA_EMPTY, category="Animals")
    assert len(result) == 0


def test_filter_entries_none_input():
    """Test filtering with None input."""
    result = filter_entries(None, category="Animals")
    assert len(result) == 0


def test_filter_entries_missing_key():
    """Test filtering with data missing the 'entries' key."""
    result = filter_entries({"count": 0}, category="Animals")
    assert len(result) == 0
