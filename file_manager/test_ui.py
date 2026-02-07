"""
UI Tests for file_manager app - Playwright E2E Tests
Run with: pytest file_manager/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestFileManagerUI:
    """UI tests for file manager"""

    def test_file_manager_requires_login(self, page: Page):
        """Test that file manager requires authentication"""
        page.goto(f"{BASE_URL}/file_manager/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_file_manager_loads(self, authenticated_page: Page):
        """Test that file manager loads when authenticated"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/")
        expect(authenticated_page).to_have_url(re.compile(r".*/file_manager.*"))

    def test_file_manager_has_title(self, authenticated_page: Page):
        """Test that file manager has title"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/")
        title = authenticated_page.locator("h1, h2, .page-title")
        expect(title.first).to_be_visible()


class TestFileUploadUI:
    """UI tests for file upload"""

    def test_upload_page_loads(self, authenticated_page: Page):
        """Test that upload page loads"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/upload/")
        expect(authenticated_page).to_have_url(re.compile(r".*/upload.*"))

    def test_upload_has_form(self, authenticated_page: Page):
        """Test that upload page has form"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/upload/")
        form = authenticated_page.locator("form")
        expect(form.first).to_be_visible()

    def test_upload_has_file_input(self, authenticated_page: Page):
        """Test that upload page has file input"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/upload/")
        file_input = authenticated_page.locator("input[type='file']")
        expect(file_input.first).to_be_visible()


class TestFileListUI:
    """UI tests for file list"""

    def test_file_list_loads(self, authenticated_page: Page):
        """Test that file list loads"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/files/")
        expect(authenticated_page).to_have_url(re.compile(r".*/files.*"))

    def test_file_list_has_content(self, authenticated_page: Page):
        """Test that file list has content container"""
        authenticated_page.goto(f"{BASE_URL}/file_manager/files/")
        content = authenticated_page.locator("table, .file-list, .list-group, .card")
        expect(content.first).to_be_visible()
