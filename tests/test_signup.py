"""
Tests for POST /activities/{activity_name}/signup endpoint.

Tests successful signup, error handling (activity not found, duplicate signup),
and email parameter validation.
"""

import pytest


def test_signup_new_student_returns_200(client, fresh_activities, activity_name, test_email):
    """
    POST /signup for a new student should return HTTP 200.
    
    AAA Pattern:
    - Arrange: Prepare valid activity name and email from fixtures
    - Act: Make POST request to signup endpoint
    - Assert: Status code is 200
    """
    # Arrange
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200


def test_signup_new_student_returns_success_message(
    client, fresh_activities, activity_name
):
    """
    POST /signup should return a success message in the response body.
    
    AAA Pattern:
    - Arrange: Prepare valid activity and email
    - Act: Make POST request and parse JSON response
    - Assert: Response contains message about signup
    """
    # Arrange
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    data = response.json()
    
    # Assert
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_adds_participant_to_activity(
    client, fresh_activities, activity_name
):
    """
    POST /signup should add the student to the activity's participant list.
    
    AAA Pattern:
    - Arrange: Get initial participant count for activity
    - Act: Sign up new student, then fetch activities
    - Assert: Participant count increased by 1
    """
    # Arrange
    email = "newstudent@mergington.edu"
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])
    
    # Assert
    assert updated_count == initial_count + 1
    assert email in updated_response.json()[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404(client, fresh_activities):
    """
    POST /signup for nonexistent activity should return HTTP 404.
    
    AAA Pattern:
    - Arrange: Prepare request with invalid activity name
    - Act: Make POST request to nonexistent activity
    - Assert: Status code is 404
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404


def test_signup_nonexistent_activity_returns_error_message(client, fresh_activities):
    """
    POST /signup for nonexistent activity should return error message.
    
    AAA Pattern:
    - Arrange: Prepare request with invalid activity
    - Act: Make POST request and parse response
    - Assert: Response contains "detail" with error message
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )
    data = response.json()
    
    # Assert
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_duplicate_student_returns_400(client, fresh_activities, activity_name):
    """
    POST /signup for already-signed-up student should return HTTP 400.
    
    AAA Pattern:
    - Arrange: Sign up a student once
    - Act: Attempt to sign up the same student again
    - Assert: Status code is 400 (Bad Request)
    """
    # Arrange
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400


def test_signup_duplicate_student_returns_error_message(
    client, fresh_activities, activity_name
):
    """
    POST /signup for duplicate student should return error message.
    
    AAA Pattern:
    - Arrange: Sign up a student once
    - Act: Attempt duplicate signup and get response
    - Assert: Response contains appropriate error message
    """
    # Arrange
    email = "duplicate@mergington.edu"
    
    # First signup
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    data = response.json()
    
    # Assert
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_missing_email_parameter_returns_error(client, fresh_activities, activity_name):
    """
    POST /signup without email parameter should return an error.
    
    AAA Pattern:
    - Arrange: Prepare request without email parameter
    - Act: Make POST request without email
    - Assert: Response indicates missing parameter
    """
    # Arrange
    # (no email parameter provided)
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup")
    
    # Assert
    assert response.status_code != 200
    # Can be 422 (validation error) or 400 depending on FastAPI version


def test_signup_multiple_students_same_activity(client, fresh_activities, activity_name):
    """
    Multiple different students should be able to sign up for the same activity.
    
    AAA Pattern:
    - Arrange: Prepare two different emails
    - Act: Sign up both students to same activity
    - Assert: Both emails are in participant list
    """
    # Arrange
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    
    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email1}
    )
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email2}
    )
    response = client.get("/activities")
    participants = response.json()[activity_name]["participants"]
    
    # Assert
    assert email1 in participants
    assert email2 in participants


def test_signup_same_student_different_activities(client, fresh_activities):
    """
    Same student should be able to sign up for multiple different activities.
    
    AAA Pattern:
    - Arrange: Prepare one email and two activities
    - Act: Sign up student for both activities
    - Assert: Student appears in both activity participant lists
    """
    # Arrange
    email = "multiactivity@mergington.edu"
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    
    # Act
    client.post(f"/activities/{activity1}/signup", params={"email": email})
    client.post(f"/activities/{activity2}/signup", params={"email": email})
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert email in activities[activity1]["participants"]
    assert email in activities[activity2]["participants"]
