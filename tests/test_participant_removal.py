"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint.

Tests successful participant removal, error handling (activity not found,
participant not in activity), and participant list updates.
"""

import pytest


def test_delete_participant_returns_200(client, fresh_activities, activity_name):
    """
    DELETE /participants should return HTTP 200 for existing participant.
    
    AAA Pattern:
    - Arrange: Get an existing participant from the activity
    - Act: Make DELETE request to remove that participant
    - Assert: Status code is 200
    """
    # Arrange
    # Use an existing participant from the fixture data
    response = client.get("/activities")
    existing_participant = response.json()[activity_name]["participants"][0]
    
    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{existing_participant}"
    )
    
    # Assert
    assert delete_response.status_code == 200


def test_delete_participant_returns_success_message(client, fresh_activities, activity_name):
    """
    DELETE /participants should return success message.
    
    AAA Pattern:
    - Arrange: Get existing participant
    - Act: Delete participant and parse response
    - Assert: Response contains success message
    """
    # Arrange
    response = client.get("/activities")
    existing_participant = response.json()[activity_name]["participants"][0]
    
    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{existing_participant}"
    )
    data = delete_response.json()
    
    # Assert
    assert "message" in data
    assert existing_participant in data["message"]
    assert activity_name in data["message"]


def test_delete_participant_removes_from_list(client, fresh_activities, activity_name):
    """
    DELETE /participants should remove participant from activity's list.
    
    AAA Pattern:
    - Arrange: Get existing participant and initial count
    - Act: Delete participant, then fetch activities again
    - Assert: Participant count decreased and email no longer in list
    """
    # Arrange
    initial_response = client.get("/activities")
    participants = initial_response.json()[activity_name]["participants"]
    participant_to_remove = participants[0]
    initial_count = len(participants)
    
    # Act
    client.delete(
        f"/activities/{activity_name}/participants/{participant_to_remove}"
    )
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    updated_count = len(updated_participants)
    
    # Assert
    assert updated_count == initial_count - 1
    assert participant_to_remove not in updated_participants


def test_delete_nonexistent_activity_returns_404(client, fresh_activities):
    """
    DELETE /participants for nonexistent activity should return HTTP 404.
    
    AAA Pattern:
    - Arrange: Prepare request with invalid activity name
    - Act: Make DELETE request to nonexistent activity
    - Assert: Status code is 404
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/participants/{email}"
    )
    
    # Assert
    assert response.status_code == 404


def test_delete_nonexistent_activity_returns_error_message(client, fresh_activities):
    """
    DELETE for nonexistent activity should return error message.
    
    AAA Pattern:
    - Arrange: Prepare invalid activity and email
    - Act: Delete and parse response
    - Assert: Response contains "detail" with error
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/participants/{email}"
    )
    data = response.json()
    
    # Assert
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_nonexistent_participant_returns_404(client, fresh_activities, activity_name):
    """
    DELETE for participant not in activity should return HTTP 404.
    
    AAA Pattern:
    - Arrange: Prepare email that's not a participant
    - Act: Make DELETE request for non-participant
    - Assert: Status code is 404
    """
    # Arrange
    nonexistent_participant = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{nonexistent_participant}"
    )
    
    # Assert
    assert response.status_code == 404


def test_delete_nonexistent_participant_returns_error_message(
    client, fresh_activities, activity_name
):
    """
    DELETE for non-participant should return error message.
    
    AAA Pattern:
    - Arrange: Prepare non-participant email
    - Act: Delete and parse response
    - Assert: Response indicates participant not found
    """
    # Arrange
    nonexistent_participant = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{nonexistent_participant}"
    )
    data = response.json()
    
    # Assert
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_all_participants_leaves_empty_list(client, fresh_activities, activity_name):
    """
    Deleting all participants from an activity should leave empty list.
    
    AAA Pattern:
    - Arrange: Get all participants
    - Act: Delete each participant one by one
    - Assert: Final participant list is empty
    """
    # Arrange
    initial_response = client.get("/activities")
    participants = initial_response.json()[activity_name]["participants"].copy()
    
    # Act
    for participant in participants:
        client.delete(
            f"/activities/{activity_name}/participants/{participant}"
        )
    
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    
    # Assert
    assert len(final_participants) == 0


def test_delete_one_participant_keeps_others(client, fresh_activities, activity_name):
    """
    Deleting one participant should not affect others in same activity.
    
    AAA Pattern:
    - Arrange: Get initial participants
    - Act: Delete first participant, fetch updated list
    - Assert: Other participants still exist
    """
    # Arrange
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    
    if len(initial_participants) < 2:
        pytest.skip("Activity must have at least 2 participants for this test")
    
    participant_to_remove = initial_participants[0]
    other_participants = initial_participants[1:]
    
    # Act
    client.delete(
        f"/activities/{activity_name}/participants/{participant_to_remove}"
    )
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    
    # Assert
    for other_participant in other_participants:
        assert other_participant in updated_participants


def test_delete_same_participant_twice_returns_404(client, fresh_activities, activity_name):
    """
    Deleting same participant twice should return 404 on second attempt.
    
    AAA Pattern:
    - Arrange: Get a participant
    - Act: Delete once (succeeds), then delete again (should fail)
    - Assert: Second delete returns 404
    """
    # Arrange
    initial_response = client.get("/activities")
    participant = initial_response.json()[activity_name]["participants"][0]
    
    # Act
    first_delete = client.delete(
        f"/activities/{activity_name}/participants/{participant}"
    )
    second_delete = client.delete(
        f"/activities/{activity_name}/participants/{participant}"
    )
    
    # Assert
    assert first_delete.status_code == 200
    assert second_delete.status_code == 404
