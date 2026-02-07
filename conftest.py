"""
Shared Playwright test fixtures and configuration
"""
import pytest
from playwright.sync_api import Page


# Test configuration
BASE_URL = "http://localhost:8016"


@pytest.fixture
def test_user_credentials():
    """Test user credentials"""
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    }


@pytest.fixture
def authenticated_page(page: Page, test_user_credentials):
    """Login and return authenticated page - skips if user doesn't exist"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", test_user_credentials["email"])
    page.fill("input[name='password']", test_user_credentials["password"])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    
    # Check if login succeeded (not still on login page with errors)
    current_url = page.url
    if "/login" in current_url:
        pytest.skip("Test user not found - create user testuser@example.com with password TestPass123!")
    
    return page
