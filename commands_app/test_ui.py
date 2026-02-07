"""
UI Tests for commands_app - Playwright E2E Tests
Run with: pytest commands_app/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestCommandsDashboardUI:
    """UI tests for commands dashboard"""

    def test_dashboard_requires_login(self, page: Page):
        """Test that commands dashboard requires authentication"""
        page.goto(f"{BASE_URL}/commands/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_dashboard_loads(self, authenticated_page: Page):
        """Test that commands dashboard loads when authenticated"""
        authenticated_page.goto(f"{BASE_URL}/commands/")
        expect(authenticated_page).to_have_url(re.compile(r".*/commands.*"))

    def test_dashboard_has_title(self, authenticated_page: Page):
        """Test that dashboard has title"""
        authenticated_page.goto(f"{BASE_URL}/commands/")
        title = authenticated_page.locator("h1, h2, .page-title")
        expect(title.first).to_be_visible()


class TestScheduledTasksUI:
    """UI tests for scheduled tasks"""

    def test_task_list_loads(self, authenticated_page: Page):
        """Test that task list loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/tasks/")
        expect(authenticated_page).to_have_url(re.compile(r".*/tasks.*"))

    def test_task_list_has_content(self, authenticated_page: Page):
        """Test that task list displays content"""
        authenticated_page.goto(f"{BASE_URL}/commands/tasks/")
        content = authenticated_page.locator("table, .task-list, .list-group, .card")
        expect(content.first).to_be_visible()

    def test_task_create_page_loads(self, authenticated_page: Page):
        """Test that task create page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/tasks/create/")
        expect(authenticated_page).to_have_url(re.compile(r".*/create.*"))

    def test_task_create_has_form(self, authenticated_page: Page):
        """Test that create page has form"""
        authenticated_page.goto(f"{BASE_URL}/commands/tasks/create/")
        form = authenticated_page.locator("form")
        expect(form.first).to_be_visible()


class TestRunCommandUI:
    """UI tests for running commands"""

    def test_run_command_page_loads(self, authenticated_page: Page):
        """Test that run command page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/run/")
        expect(authenticated_page).to_have_url(re.compile(r".*/run.*"))

    def test_run_command_has_form(self, authenticated_page: Page):
        """Test that run command has form"""
        authenticated_page.goto(f"{BASE_URL}/commands/run/")
        form = authenticated_page.locator("form")
        expect(form.first).to_be_visible()


class TestCommandLogsUI:
    """UI tests for command logs"""

    def test_log_list_loads(self, authenticated_page: Page):
        """Test that command log list loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/logs/")
        expect(authenticated_page).to_have_url(re.compile(r".*/logs.*"))

    def test_log_list_has_content(self, authenticated_page: Page):
        """Test that log list has content"""
        authenticated_page.goto(f"{BASE_URL}/commands/logs/")
        content = authenticated_page.locator("table, .log-list, .list-group")
        expect(content.first).to_be_visible()


class TestMetricsUI:
    """UI tests for metrics"""

    def test_metrics_page_loads(self, authenticated_page: Page):
        """Test that metrics page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/metrics/")
        expect(authenticated_page).to_have_url(re.compile(r".*/metrics.*"))

    def test_metrics_has_content(self, authenticated_page: Page):
        """Test that metrics has content"""
        authenticated_page.goto(f"{BASE_URL}/commands/metrics/")
        content = authenticated_page.locator("canvas, .chart, .metric, .stat, .card, table")
        expect(content.first).to_be_visible()


class TestTaskExecutionsUI:
    """UI tests for task executions"""

    def test_executions_page_loads(self, authenticated_page: Page):
        """Test that executions page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/executions/")
        expect(authenticated_page).to_have_url(re.compile(r".*/executions.*"))


class TestDataImportExportUI:
    """UI tests for data import/export"""

    def test_imports_page_loads(self, authenticated_page: Page):
        """Test that imports page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/imports/")
        expect(authenticated_page).to_have_url(re.compile(r".*/imports.*"))

    def test_exports_page_loads(self, authenticated_page: Page):
        """Test that exports page loads"""
        authenticated_page.goto(f"{BASE_URL}/commands/exports/")
        expect(authenticated_page).to_have_url(re.compile(r".*/exports.*"))

