"""
Shared Playwright test fixtures and configuration for Django Test Enforcer

UI tests run against a LIVE Django server (not the test database).
Ensure the Django server is running on the configured BASE_URL port.
For authenticated tests, ensure a test user exists in the database.
"""
import pytest
from playwright.sync_api import Page, expect


# Test configuration - Update this to match your local server
BASE_URL = "http://localhost:8016"


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for tests"""
    return BASE_URL


@pytest.fixture(scope="session")
def test_user_credentials():
    """
    Test user credentials for authenticated tests.
    
    IMPORTANT: Create this user in your database before running authenticated tests:
        python manage.py shell
        >>> from django.contrib.auth import get_user_model
        >>> User = get_user_model()
        >>> user = User.objects.create_user(email='testuser@example.com', username='testuser', password='TestPass123!')
        >>> user.is_active = True
        >>> user.save()
    """
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    }


@pytest.fixture
def authenticated_page(page: Page, test_user_credentials, base_url):
    """Login and return authenticated page"""
    page.goto(f"{base_url}/login/", timeout=60000)
    page.fill("input[name='username']", test_user_credentials["email"])
    page.fill("input[name='password']", test_user_credentials["password"])
    
    # Use force=True and no_wait_after to avoid hanging on navigation
    page.locator("button[type='submit']").click(force=True, no_wait_after=True)
    
    # Explicitly wait for navigation to complete
    page.wait_for_url(lambda url: "/login" not in url, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=60000)
    
    # Check if login succeeded (not still on login page with errors)
    current_url = page.url
    if "/login" in current_url:
        # Try to check for error messages
        error_visible = page.locator(".alert-danger, .errorlist, .error").count() > 0
        if error_visible:
            pytest.skip("Login failed - create test user: testuser@example.com / TestPass123!")
    
    return page
