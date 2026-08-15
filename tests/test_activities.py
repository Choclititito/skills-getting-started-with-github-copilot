"""
Tests for GET /activities endpoint.

Tests the retrieval of all activities with proper schema validation
and participant count verification.
"""

import pytest


def test_get_all_activities_returns_200(client, fresh_activities):
    """
    GET /activities should return HTTP 200 with all activities.
    
    AAA Pattern:
    - Arrange: No setup needed, activities are pre-populated in conftest
    - Act: Make GET request to /activities
    - Assert: Status code is 200
    """
    # Arrange
    # (activities fixture provides pre-populated data)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200


def test_get_all_activities_returns_dict(client, fresh_activities):
    """
    GET /activities should return a dictionary of activities.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Make GET request and parse JSON
    - Assert: Response is a dictionary
    """
    # Arrange
    # (activities fixture provides data)
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_required_activity(client, fresh_activities):
    """
    GET /activities should include Chess Club activity.
    
    AAA Pattern:
    - Arrange: Fixture provides known activities
    - Act: Make GET request and parse response
    - Assert: Chess Club is in the response
    """
    # Arrange
    # (activities fixture provides data with Chess Club)
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert "Chess Club" in data


def test_activity_has_required_fields(client, fresh_activities):
    """
    Each activity should have description, schedule, max_participants, and participants fields.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Make GET request and extract Chess Club
    - Assert: All required fields present
    """
    # Arrange
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    chess_club = data["Chess Club"]
    
    # Assert
    for field in required_fields:
        assert field in chess_club, f"Missing required field: {field}"


def test_activity_description_is_string(client, fresh_activities):
    """
    Activity description should be a non-empty string.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Get activities and extract description
    - Assert: Description is a string
    """
    # Arrange
    # (activities fixture provides data)
    
    # Act
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    description = chess_club["description"]
    
    # Assert
    assert isinstance(description, str)
    assert len(description) > 0


def test_activity_schedule_is_string(client, fresh_activities):
    """
    Activity schedule should be a non-empty string.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Get activities and extract schedule
    - Assert: Schedule is a string
    """
    # Arrange
    # (activities fixture provides data)
    
    # Act
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    schedule = chess_club["schedule"]
    
    # Assert
    assert isinstance(schedule, str)
    assert len(schedule) > 0


def test_activity_max_participants_is_integer(client, fresh_activities):
    """
    Activity max_participants should be a positive integer.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Get activities and extract max_participants
    - Assert: max_participants is a positive integer
    """
    # Arrange
    # (activities fixture provides data)
    
    # Act
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    max_participants = chess_club["max_participants"]
    
    # Assert
    assert isinstance(max_participants, int)
    assert max_participants > 0


def test_activity_participants_is_list(client, fresh_activities):
    """
    Activity participants should be a list of email strings.
    
    AAA Pattern:
    - Arrange: Fixture provides activities
    - Act: Get activities and extract participants
    - Assert: Participants is a list
    """
    # Arrange
    # (activities fixture provides data)
    
    # Act
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    participants = chess_club["participants"]
    
    # Assert
    assert isinstance(participants, list)
    assert all(isinstance(email, str) for email in participants)


def test_activity_participant_count_matches(client, fresh_activities):
    """
    Verify participant count is correct for an activity with known participants.
    
    AAA Pattern:
    - Arrange: Chess Club fixture has 2 initial participants
    - Act: Get activities and count participants
    - Assert: Participant list length is 2
    """
    # Arrange
    expected_count = 2  # Chess Club starts with michael@ and daniel@
    
    # Act
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    actual_count = len(chess_club["participants"])
    
    # Assert
    assert actual_count == expected_count


def test_get_activities_response_contains_all_common_activities(
    client, fresh_activities
):
    """
    GET /activities should include Chess Club, Programming Class, and Gym Class.
    
    AAA Pattern:
    - Arrange: Define expected activity names
    - Act: Get all activities
    - Assert: All expected activities are present
    """
    # Arrange
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity in expected_activities:
        assert activity in data, f"Expected activity '{activity}' not found"
