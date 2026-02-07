"""
UI Tests for api_app - Playwright E2E Tests
Run with: pytest api_app/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestAPIDashboardUI:
    """UI tests for API Dashboard"""

    def test_api_dashboard_requires_login(self, page: Page):
        """Test that API dashboard requires authentication"""
        page.goto(f"{BASE_URL}/api/dashboard/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_api_dashboard_loads_when_authenticated(self, authenticated_page: Page):
        """Test that API dashboard loads when logged in"""
        authenticated_page.goto(f"{BASE_URL}/api/dashboard/")
        expect(authenticated_page).to_have_url(re.compile(r".*/api/dashboard.*"))


class TestSwaggerUI:
    """UI tests for Swagger documentation"""

    def test_swagger_ui_loads(self, page: Page):
        """Test that Swagger UI loads"""
        page.goto(f"{BASE_URL}/api/schema/swagger-ui/")
        expect(page).to_have_url(re.compile(r".*/swagger.*"))

    def test_swagger_ui_content(self, page: Page):
        """Test that Swagger UI displays content"""
        page.goto(f"{BASE_URL}/api/schema/swagger-ui/")
        page.wait_for_load_state("networkidle")
        expect(page.locator("body")).to_be_visible()

    def test_redoc_loads(self, page: Page):
        """Test that ReDoc loads"""
        page.goto(f"{BASE_URL}/api/schema/redoc/")
        expect(page).to_have_url(re.compile(r".*/redoc.*"))


class TestAPIEndpointsUI:
    """UI tests for API endpoints"""

    def test_products_api(self, authenticated_page: Page):
        """Test products API endpoint"""
        authenticated_page.goto(f"{BASE_URL}/api/products/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_reviews_api(self, authenticated_page: Page):
        """Test reviews API endpoint"""
        authenticated_page.goto(f"{BASE_URL}/api/reviews/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_orders_api(self, authenticated_page: Page):
        """Test orders API endpoint"""
        authenticated_page.goto(f"{BASE_URL}/api/orders/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_users_api(self, authenticated_page: Page):
        """Test users API endpoint"""
        authenticated_page.goto(f"{BASE_URL}/api/users/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_health_api(self, page: Page):
        """Test health check endpoint"""
        page.goto(f"{BASE_URL}/api/health/")
        expect(page.locator("body")).to_be_visible()
