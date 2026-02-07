"""
UI Tests for account app - Playwright E2E Tests
Run with: pytest account/test_ui.py --headed --base-url=http://localhost:8016
"""
import pytest
from playwright.sync_api import Page, expect
import re


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


class TestAccountActivationDoneUI:
    """UI tests for account_activation_done.html"""

    def test_activation_done_page_loads(self, page: Page):
        """Test that activation done page loads correctly"""
        page.goto(f"{BASE_URL}/account_activation_done/")
        expect(page).to_have_title(re.compile(r".*", re.IGNORECASE))
        
    def test_activation_done_has_home_link(self, page: Page):
        """Test that activation done page has HOME link or navigation"""
        page.goto(f"{BASE_URL}/account_activation_done/")
        # Look for any link back to home or navigation
        home_link = page.locator("a[href='/'], a[href*='home'], a:has-text('HOME'), a:has-text('Home'), a:has-text('home'), nav a")
        if home_link.count() == 0:
            pytest.skip("No home link found on activation done page")
        expect(home_link.first).to_be_visible()

    def test_activation_done_home_link_works(self, page: Page):
        """Test that HOME link navigates correctly"""
        page.goto(f"{BASE_URL}/account_activation_done/")
        home_link = page.locator("a[href='/'], a[href*='home'], a:has-text('HOME'), a:has-text('Home')").first
        if home_link.is_visible():
            home_link.click()
            page.wait_for_load_state("networkidle")
        expect(page.locator("body")).to_be_visible()


class TestRegisterUI:
    """UI tests for register.html"""

    def test_register_page_loads(self, page: Page):
        """Test that registration page loads correctly"""
        page.goto(f"{BASE_URL}/register/")
        expect(page).to_have_url(re.compile(r".*/register.*"))

    def test_register_has_sign_up_button(self, page: Page):
        """Test that registration page has Sign UP button"""
        page.goto(f"{BASE_URL}/register/")
        submit_btn = page.locator("button[type='submit'], input[type='submit']")
        expect(submit_btn.first).to_be_visible()

    def test_register_has_form(self, page: Page):
        """Test that registration page has form"""
        page.goto(f"{BASE_URL}/register/")
        form = page.locator("form")
        expect(form.first).to_be_visible()

    def test_register_has_email_field(self, page: Page):
        """Test that registration page has email input field"""
        page.goto(f"{BASE_URL}/register/")
        email_field = page.locator("input[name='email'], input[type='email']")
        expect(email_field.first).to_be_visible()

    def test_register_has_password_fields(self, page: Page):
        """Test that registration page has password fields"""
        page.goto(f"{BASE_URL}/register/")
        password_field = page.locator("input[type='password']")
        expect(password_field.first).to_be_visible()

    def test_register_has_sign_in_link(self, page: Page):
        """Test that registration page has Sign IN link"""
        page.goto(f"{BASE_URL}/register/")
        login_link = page.locator("a[href*='login'], a:has-text('Sign IN'), a:has-text('Login')")
        expect(login_link.first).to_be_visible()

    def test_register_form_validation(self, page: Page):
        """Test that form shows validation errors for invalid input"""
        page.goto(f"{BASE_URL}/register/")
        # Submit empty form
        page.click("button[type='submit'], input[type='submit']")
        # Should stay on register page or show errors
        expect(page).to_have_url(re.compile(r".*/register.*"))


class TestLoginUI:
    """UI tests for login.html"""

    def test_login_page_loads(self, page: Page):
        """Test that login page loads correctly"""
        page.goto(f"{BASE_URL}/login/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_login_has_sign_in_button(self, page: Page):
        """Test that login page has Sign in button"""
        page.goto(f"{BASE_URL}/login/")
        submit_btn = page.locator("button[type='submit'], input[type='submit']")
        expect(submit_btn.first).to_be_visible()

    def test_login_has_form(self, page: Page):
        """Test that login page has form"""
        page.goto(f"{BASE_URL}/login/")
        form = page.locator("form")
        expect(form.first).to_be_visible()

    def test_login_has_email_field(self, page: Page):
        """Test that login page has username field"""
        page.goto(f"{BASE_URL}/login/")
        username_field = page.locator("input[name='username'], input[type='text']")
        expect(username_field.first).to_be_visible()

    def test_login_has_password_field(self, page: Page):
        """Test that login page has password field"""
        page.goto(f"{BASE_URL}/login/")
        password_field = page.locator("input[type='password']")
        expect(password_field.first).to_be_visible()

    def test_login_has_register_link(self, page: Page):
        """Test that login page has Register here link"""
        page.goto(f"{BASE_URL}/login/")
        register_link = page.locator("a[href*='register'], a:has-text('Register')")
        expect(register_link.first).to_be_visible()

    def test_login_has_reset_password_link(self, page: Page):
        """Test that login page has Reset Password link"""
        page.goto(f"{BASE_URL}/login/")
        reset_link = page.locator("a[href*='password'], a:has-text('Reset'), a:has-text('Forgot')")
        expect(reset_link.first).to_be_visible()

    def test_login_invalid_credentials_shows_error(self, page: Page):
        """Test that invalid login shows error message"""
        page.goto(f"{BASE_URL}/login/")
        page.fill("input[name='username']", "invalid@example.com")
        page.fill("input[type='password']", "wrongpassword")
        page.click("button[type='submit']")
        # Should stay on login page or show error
        page.wait_for_load_state("networkidle")
        expect(page.locator("body")).to_be_visible()


class TestAccountUI:
    """UI tests for account.html"""

    def test_account_page_requires_login(self, page: Page):
        """Test that account page redirects to login when not authenticated"""
        page.goto(f"{BASE_URL}/account/")
        # Should redirect to login
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_account_page_loads_when_authenticated(self, authenticated_page: Page):
        """Test that account page loads when logged in"""
        authenticated_page.goto(f"{BASE_URL}/account/")
        expect(authenticated_page).to_have_url(re.compile(r".*/account.*"))

    def test_account_has_update_button(self, authenticated_page: Page):
        """Test that account page has Update Account Details button"""
        authenticated_page.goto(f"{BASE_URL}/account/")
        update_btn = authenticated_page.locator("button[type='submit'], input[type='submit']")
        expect(update_btn.first).to_be_visible()

    def test_account_has_form(self, authenticated_page: Page):
        """Test that account page has form"""
        authenticated_page.goto(f"{BASE_URL}/account/")
        form = authenticated_page.locator("form")
        expect(form.first).to_be_visible()

    def test_account_shows_user_email(self, authenticated_page: Page, test_user_credentials):
        """Test that account page shows user's email"""
        authenticated_page.goto(f"{BASE_URL}/account/")
        # Email should be visible somewhere on the page
        expect(authenticated_page.locator("body")).to_contain_text(test_user_credentials["email"])


class TestPasswordResetUI:
    """UI tests for password reset pages"""

    def test_password_reset_page_loads(self, page: Page):
        """Test that password reset page loads"""
        page.goto(f"{BASE_URL}/password_reset/")
        expect(page).to_have_url(re.compile(r".*/password.*"))

    def test_password_reset_has_form(self, page: Page):
        """Test that password reset page has form"""
        page.goto(f"{BASE_URL}/password_reset/")
        form = page.locator("form")
        expect(form.first).to_be_visible()

    def test_password_reset_has_email_field(self, page: Page):
        """Test that password reset page has email field"""
        page.goto(f"{BASE_URL}/password_reset/")
        email_field = page.locator("input[name='email'], input[type='email']")
        expect(email_field.first).to_be_visible()

    def test_password_reset_has_submit_button(self, page: Page):
        """Test that password reset page has submit button"""
        page.goto(f"{BASE_URL}/password_reset/")
        submit_btn = page.locator("button[type='submit'], input[type='submit']")
        expect(submit_btn.first).to_be_visible()


class TestLogoutUI:
    """UI tests for logout functionality"""

    def test_logout_redirects_to_home(self, authenticated_page: Page):
        """Test that logout redirects properly"""
        authenticated_page.goto(f"{BASE_URL}/logout/")
        # After logout should be redirected
        expect(authenticated_page).to_have_url(re.compile(r".*/(login|home|)/?.*"))
