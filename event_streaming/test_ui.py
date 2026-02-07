"""
UI Tests for event_streaming app - Playwright E2E Tests
Run with: pytest event_streaming/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestEventStreamingUI:
    """UI tests for event streaming"""

    def test_events_requires_login(self, page: Page):
        """Test that events requires authentication"""
        page.goto(f"{BASE_URL}/events/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_events_dashboard_loads(self, authenticated_page: Page):
        """Test that events dashboard loads"""
        authenticated_page.goto(f"{BASE_URL}/events/")
        expect(authenticated_page).to_have_url(re.compile(r".*/events.*"))

    def test_events_has_title(self, authenticated_page: Page):
        """Test that events has title"""
        authenticated_page.goto(f"{BASE_URL}/events/")
        title = authenticated_page.locator("h1, h2, .page-title")
        expect(title.first).to_be_visible()


class TestKafkaUI:
    """UI tests for Kafka"""

    def test_kafka_status_page(self, authenticated_page: Page):
        """Test Kafka status page"""
        authenticated_page.goto(f"{BASE_URL}/events/kafka/")
        expect(authenticated_page.locator("body")).to_be_visible()

    def test_kafka_test_connection(self, authenticated_page: Page):
        """Test Kafka connection test page"""
        authenticated_page.goto(f"{BASE_URL}/events/test-kafka/")
        expect(authenticated_page.locator("body")).to_be_visible()


class TestEventProducerUI:
    """UI tests for event producer"""

    def test_producer_page_loads(self, authenticated_page: Page):
        """Test that producer page loads"""
        authenticated_page.goto(f"{BASE_URL}/events/produce/")
        expect(authenticated_page.locator("body")).to_be_visible()


class TestEventListUI:
    """UI tests for event list"""

    def test_event_list_loads(self, authenticated_page: Page):
        """Test that event list loads"""
        authenticated_page.goto(f"{BASE_URL}/events/list/")
        expect(authenticated_page.locator("body")).to_be_visible()
