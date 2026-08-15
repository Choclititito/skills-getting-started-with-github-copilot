"""
Pytest configuration and shared fixtures for FastAPI tests.

This module provides reusable fixtures for testing the Mergington High School
activity management API, including:
- A test client for making requests to the app
- Fresh in-memory activities state per test
- Parametrized test data (activity names, emails)
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient instance for the app.
    
    This client allows tests to make HTTP-like requests to the app
    without running an actual server.
    
    Scope: function (fresh client per test)
    
    Returns:
        TestClient: A test client connected to the app
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provides a fresh copy of the activities dict and restores it after each test.
    
    This fixture ensures test isolation by:
    1. Saving the original state at test start
    2. Allowing the test to modify activities via the app
    3. Restoring the original state after the test completes
    
    This prevents tests from affecting each other through shared state.
    
    Scope: function (fresh state per test)
    
    Yields:
        dict: A deep copy of the activities dict for this test
    """
    # Save the original state
    original_activities = copy.deepcopy(activities)
    
    # Yield to allow the test to run
    yield activities
    
    # Restore the original state after test completes
    activities.clear()
    activities.update(original_activities)


@pytest.fixture(
    params=[
        "Chess Club",
        "Programming Class",
        "Gym Class"
    ]
)
def activity_name(request):
    """
    Parametrized fixture providing common activity names.
    
    Tests using this fixture will run multiple times, once for each activity.
    This reduces code duplication when testing the same operation across
    different activities.
    
    Scope: function
    
    Returns:
        str: An activity name from the common activities in the app
    """
    return request.param


@pytest.fixture
def test_email():
    """
    Provides a consistent test email address for signup operations.
    
    Scope: function
    
    Returns:
        str: A test email address in the format "student@test.mergington.edu"
    """
    return "student@test.mergington.edu"
