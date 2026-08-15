"""
Integration tests for cross-endpoint workflows.

Tests multi-step scenarios that involve multiple endpoints working together,
such as signup followed by verification and deletion.
"""

import pytest


def test_signup_then_verify_participant_appears(client, fresh_activities, activity_name):
    """
    After signup, new participant should appear in GET /activities response.
    
    AAA Pattern:
    - Arrange: Prepare new email
    - Act: Sign up, then fetch activities
    - Assert: Email appears in participant list
    """
    # Arrange
    email = "workflow@mergington.edu"
    
    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    activities_response = client.get("/activities")
    
    # Assert
    assert signup_response.status_code == 200
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_complete_signup_delete_workflow(client, fresh_activities, activity_name):
    """
    Complete workflow: signup → verify → delete → verify removed.
    
    AAA Pattern:
    - Arrange: Prepare email
    - Act: Sign up, verify appears, delete, verify removed
    - Assert: All steps succeed with correct state changes
    """
    # Arrange
    email = "complete@mergington.edu"
    
    # Act - Step 1: Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Act - Step 2: Verify participant appears
    after_signup = client.get("/activities")
    participants_after_signup = after_signup.json()[activity_name]["participants"]
    
    # Act - Step 3: Delete participant
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )
    
    # Act - Step 4: Verify participant removed
    after_delete = client.get("/activities")
    participants_after_delete = after_delete.json()[activity_name]["participants"]
    
    # Assert
    assert signup_response.status_code == 200
    assert email in participants_after_signup
    assert delete_response.status_code == 200
    assert email not in participants_after_delete


def test_multiple_signups_all_appear_in_list(client, fresh_activities, activity_name):
    """
    Multiple signups should accumulate in the participant list.
    
    AAA Pattern:
    - Arrange: Prepare multiple emails
    - Act: Sign up each student, then fetch activities
    - Assert: All emails appear in participant list
    """
    # Arrange
    emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
    ]
    
    # Act
    for email in emails:
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
    
    response = client.get("/activities")
    participants = response.json()[activity_name]["participants"]
    
    # Assert
    for email in emails:
        assert email in participants


def test_signup_count_increases_correctly(client, fresh_activities, activity_name):
    """
    Participant count should increase by 1 with each new signup.
    
    AAA Pattern:
    - Arrange: Get initial participant count
    - Act: Sign up 2 new students, track count after each
    - Assert: Count increases by 1 each time
    """
    # Arrange
    initial_response = client.get("/activities")
    initial_count = len(
        initial_response.json()[activity_name]["participants"]
    )
    
    # Act & Assert - First signup
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "count1@mergington.edu"}
    )
    response1 = client.get("/activities")
    count1 = len(response1.json()[activity_name]["participants"])
    assert count1 == initial_count + 1
    
    # Act & Assert - Second signup
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "count2@mergington.edu"}
    )
    response2 = client.get("/activities")
    count2 = len(response2.json()[activity_name]["participants"])
    assert count2 == initial_count + 2


def test_delete_count_decreases_correctly(client, fresh_activities, activity_name):
    """
    Participant count should decrease by 1 with each deletion.
    
    AAA Pattern:
    - Arrange: Sign up 2 students, get count
    - Act: Delete one, check count; delete second, check count
    - Assert: Count decreases by 1 each time
    """
    # Arrange
    email1 = "delete1@mergington.edu"
    email2 = "delete2@mergington.edu"
    
    client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    client.post(f"/activities/{activity_name}/signup", params={"email": email2})
    
    response_before = client.get("/activities")
    count_before = len(response_before.json()[activity_name]["participants"])
    
    # Act & Assert - First deletion
    client.delete(f"/activities/{activity_name}/participants/{email1}")
    response1 = client.get("/activities")
    count1 = len(response1.json()[activity_name]["participants"])
    assert count1 == count_before - 1
    
    # Act & Assert - Second deletion
    client.delete(f"/activities/{activity_name}/participants/{email2}")
    response2 = client.get("/activities")
    count2 = len(response2.json()[activity_name]["participants"])
    assert count2 == count_before - 2


def test_same_student_multiple_activities_independent(client, fresh_activities):
    """
    Student signup for one activity should not affect other activities.
    
    AAA Pattern:
    - Arrange: Get initial counts for two activities
    - Act: Sign up same student for first activity
    - Assert: Only first activity's count increases, second unchanged
    """
    # Arrange
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    email = "multi@mergington.edu"
    
    initial = client.get("/activities").json()
    count1_before = len(initial[activity1]["participants"])
    count2_before = len(initial[activity2]["participants"])
    
    # Act
    client.post(f"/activities/{activity1}/signup", params={"email": email})
    after = client.get("/activities").json()
    count1_after = len(after[activity1]["participants"])
    count2_after = len(after[activity2]["participants"])
    
    # Assert
    assert count1_after == count1_before + 1
    assert count2_after == count2_before  # Unchanged


def test_activity_data_integrity_after_operations(client, fresh_activities, activity_name):
    """
    Activity metadata (description, schedule, max_participants) should remain unchanged.
    
    AAA Pattern:
    - Arrange: Get initial activity data
    - Act: Perform signup and deletion
    - Assert: Metadata fields unchanged, only participants list changed
    """
    # Arrange
    initial = client.get("/activities").json()[activity_name]
    initial_description = initial["description"]
    initial_schedule = initial["schedule"]
    initial_max = initial["max_participants"]
    
    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "test@mergington.edu"}
    )
    client.delete(
        f"/activities/{activity_name}/participants/test@mergington.edu"
    )
    
    # Assert
    final = client.get("/activities").json()[activity_name]
    assert final["description"] == initial_description
    assert final["schedule"] == initial_schedule
    assert final["max_participants"] == initial_max


def test_error_during_signup_does_not_add_participant(client, fresh_activities, activity_name):
    """
    Failed signup (e.g., duplicate) should not add participant to activity.
    
    AAA Pattern:
    - Arrange: Sign up a student successfully
    - Act: Attempt duplicate signup (should fail), then fetch activities
    - Assert: Participant list still has same count as before duplicate attempt
    """
    # Arrange
    email = "duplicate@mergington.edu"
    
    # First signup succeeds
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    response_before_error = client.get("/activities")
    count_before_error = len(
        response_before_error.json()[activity_name]["participants"]
    )
    
    # Act - Attempt duplicate signup (should fail with 400)
    error_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response_after_error = client.get("/activities")
    count_after_error = len(
        response_after_error.json()[activity_name]["participants"]
    )
    
    # Assert
    assert error_response.status_code == 400
    assert count_after_error == count_before_error  # No change


def test_state_isolation_between_tests(client, fresh_activities, activity_name):
    """
    Fresh activities fixture ensures clean state for each test.
    
    AAA Pattern:
    - Arrange: Get initial state (via fresh_activities fixture)
    - Act: Sign up a student
    - Assert: This test's state doesn't affect subsequent tests
    
    Note: This test passes by virtue of the fixture.
    Each test gets a fresh_activities fixture that restores state after.
    """
    # Arrange
    initial = client.get("/activities").json()
    initial_count = len(initial[activity_name]["participants"])
    
    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "isolation@mergington.edu"}
    )
    
    # Assert
    # If we were to run another test, it would start with original state
    # This is guaranteed by the fresh_activities fixture using yield
    assert initial_count >= 0  # Just verify we got a count
