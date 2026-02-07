"""
UI Tests for messaging_system app - Playwright E2E Tests
Run with: pytest messaging_system/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestMessagingUI:
    """UI tests for messaging system"""

    def test_messaging_requires_login(self, page: Page):
        """Test that messaging requires authentication"""
        page.goto(f"{BASE_URL}/messaging/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_messaging_dashboard_loads(self, authenticated_page: Page):
        """Test that messaging dashboard loads"""
        authenticated_page.goto(f"{BASE_URL}/messaging/")
        expect(authenticated_page).to_have_url(re.compile(r".*/messaging.*"))

    def test_messaging_has_title(self, authenticated_page: Page):
        """Test that messaging has title"""
        authenticated_page.goto(f"{BASE_URL}/messaging/")
        title = authenticated_page.locator("h1, h2, .page-title")
        expect(title.first).to_be_visible()


class TestRabbitMQUI:
    """UI tests for RabbitMQ"""

    def test_rabbitmq_status_page(self, authenticated_page: Page):
        """Test RabbitMQ status page"""
        authenticated_page.goto(f"{BASE_URL}/messaging/rabbitmq/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_rabbitmq_test_connection(self, authenticated_page: Page):
        """Test RabbitMQ connection test page"""
        authenticated_page.goto(f"{BASE_URL}/messaging/test-rabbitmq/")
        expect(authenticated_page.locator("body")).to_be_visible()


class TestMessageProducerUI:
    """UI tests for message producer"""

    def test_producer_page_loads(self, authenticated_page: Page):
        """Test that producer page loads"""
        authenticated_page.goto(f"{BASE_URL}/messaging/send/")
        expect(authenticated_page.locator("body")).to_be_visible()


class TestMessageListUI:
    """UI tests for message list"""

    def test_message_list_loads(self, authenticated_page: Page):
        """Test that message list loads"""
        authenticated_page.goto(f"{BASE_URL}/messaging/messages/")
        expect(authenticated_page.locator("body")).to_be_visible()
