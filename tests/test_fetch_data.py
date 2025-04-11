import pytest
from src.fetch_data import filter_category

# Sample data mimicking the API structure
MOCK_DATA = {
    "count": 3,
    "nobelPrizes": [
        {'awardYear': '1901', 'category': {'en': 'Physics', 'no': 'Kjemi', 'se': 'Kemi'}, 'categoryFullName': {'en': 'The Nobel Prize in Physics', 'no': 'Nobelprisen i kjemi', 'se': 'Nobelpriset i kemi'}, 'dateAwarded': '1901-11-12', 'prizeAmount': 150782, 'prizeAmountAdjusted': 9704878, 'links': [{'rel': 'nobelPrize', 'href': 'https://api.nobelprize.org/2/nobelPrize/che/1901', 'action': 'GET', 'types': 'application/json'}], 'laureates': [{'id': '160', 'knownName': {'en': "Jacobus H. van 't Hoff"}, 'fullName': {'en': "Jacobus Henricus van 't Hoff"}, 'portion': '1', 'sortOrder': '1', 'motivation': {'en': 'in recognition of the extraordinary services he has rendered by the discovery of the laws of chemical dynamics and osmotic pressure in solutions', 'se': 'såsom ett erkännande av den utomordentliga förtjänst han inlagt genom upptäckten av lagarna för den kemiska dynamiken och för det osmotiska trycket i lösningar'}, 'links': [{'rel': 'laureate', 'href': 'https://api.nobelprize.org/2/laureate/160', 'action': 'GET', 'types': 'application/json'}]}]},
        {'awardYear': '1901', 'category': {'en': 'Chemistry', 'no': 'Kjemi', 'se': 'Kemi'}, 'categoryFullName': {'en': 'The Nobel Prize in Chemistry', 'no': 'Nobelprisen i kjemi', 'se': 'Nobelpriset i kemi'}, 'dateAwarded': '1901-11-12', 'prizeAmount': 150782, 'prizeAmountAdjusted': 9704878, 'links': [{'rel': 'nobelPrize', 'href': 'https://api.nobelprize.org/2/nobelPrize/che/1901', 'action': 'GET', 'types': 'application/json'}], 'laureates': [{'id': '160', 'knownName': {'en': "Jacobus H. van 't Hoff"}, 'fullName': {'en': "Jacobus Henricus van 't Hoff"}, 'portion': '1', 'sortOrder': '1', 'motivation': {'en': 'in recognition of the extraordinary services he has rendered by the discovery of the laws of chemical dynamics and osmotic pressure in solutions', 'se': 'såsom ett erkännande av den utomordentliga förtjänst han inlagt genom upptäckten av lagarna för den kemiska dynamiken och för det osmotiska trycket i lösningar'}, 'links': [{'rel': 'laureate', 'href': 'https://api.nobelprize.org/2/laureate/160', 'action': 'GET', 'types': 'application/json'}]}]},
        {'awardYear': '1901', 'category': {'en': 'Physics', 'no': 'Kjemi', 'se': 'Kemi'}, 'categoryFullName': {'en': 'The Nobel Prize in Physics', 'no': 'Nobelprisen i kjemi', 'se': 'Nobelpriset i kemi'}, 'dateAwarded': '1901-11-12', 'prizeAmount': 150782, 'prizeAmountAdjusted': 9704878, 'links': [{'rel': 'nobelPrize', 'href': 'https://api.nobelprize.org/2/nobelPrize/che/1901', 'action': 'GET', 'types': 'application/json'}], 'laureates': [{'id': '160', 'knownName': {'en': "Jacobus H. van 't Hoff"}, 'fullName': {'en': "Jacobus Henricus van 't Hoff"}, 'portion': '1', 'sortOrder': '1', 'motivation': {'en': 'in recognition of the extraordinary services he has rendered by the discovery of the laws of chemical dynamics and osmotic pressure in solutions', 'se': 'såsom ett erkännande av den utomordentliga förtjänst han inlagt genom upptäckten av lagarna för den kemiska dynamiken och för det osmotiska trycket i lösningar'}, 'links': [{'rel': 'laureate', 'href': 'https://api.nobelprize.org/2/laureate/160', 'action': 'GET', 'types': 'application/json'}]}]},
    ]
}

MOCK_DATA_EMPTY = {"count": 0, "nobelPrizes": []}
MOCK_DATA_NO_ANIMALS = {
    "count": 1,
    "nobelPrizes": [
        {'awardYear': '1901', 'category': {'en': 'Chemistry', 'no': 'Kjemi', 'se': 'Kemi'}, 'categoryFullName': {'en': 'The Nobel Prize in Chemistry', 'no': 'Nobelprisen i kjemi', 'se': 'Nobelpriset i kemi'}, 'dateAwarded': '1901-11-12', 'prizeAmount': 150782, 'prizeAmountAdjusted': 9704878, 'links': [{'rel': 'nobelPrize', 'href': 'https://api.nobelprize.org/2/nobelPrize/che/1901', 'action': 'GET', 'types': 'application/json'}], 'laureates': [{'id': '160', 'knownName': {'en': "Jacobus H. van 't Hoff"}, 'fullName': {'en': "Jacobus Henricus van 't Hoff"}, 'portion': '1', 'sortOrder': '1', 'motivation': {'en': 'in recognition of the extraordinary services he has rendered by the discovery of the laws of chemical dynamics and osmotic pressure in solutions', 'se': 'såsom ett erkännande av den utomordentliga förtjänst han inlagt genom upptäckten av lagarna för den kemiska dynamiken och för det osmotiska trycket i lösningar'}, 'links': [{'rel': 'laureate', 'href': 'https://api.nobelprize.org/2/laureate/160', 'action': 'GET', 'types': 'application/json'}]}]},
    ]
}


def test_filter_category_standard():
    """Test filtering with standard data."""
    result = filter_category(MOCK_DATA, category="Physics")
    assert len(result) == 2
    assert all(nobelPrize['category']['en'] == "Physics" for nobelPrize in result)


def test_filter_category_different_category():
    """Test filtering for a different category."""
    result = filter_category(MOCK_DATA, category="Chemistry")
    assert len(result) == 1
    assert result[0]['category']['en'] == "Chemistry"


def test_filter_category_no_match():
    """Test filtering when no nobelPrizes match."""
    result = filter_category(MOCK_DATA_NO_ANIMALS, category="Physics")
    assert len(result) == 0


def test_filter_category_empty_input():
    """Test filtering with empty input data."""
    result = filter_category(MOCK_DATA_EMPTY, category="Physics")
    assert len(result) == 0


def test_filter_category_none_input():
    """Test filtering with None input."""
    result = filter_category(None, category="Physics")
    assert len(result) == 0


def test_filter_category_missing_key():
    """Test filtering with data missing the 'nobelPrizes' key."""
    result = filter_category({"count": 0}, category="Physics")
    assert len(result) == 0
