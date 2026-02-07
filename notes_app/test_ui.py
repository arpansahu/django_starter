"""
UI Tests for notes_app - Playwright E2E Tests
Run with: pytest notes_app/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://localhost:8016"


class TestNotesHomeUI:
    """UI tests for notes home"""

    def test_notes_requires_login(self, page: Page):
        """Test that notes requires authentication"""
        page.goto(f"{BASE_URL}/notes/")
        expect(page).to_have_url(re.compile(r".*/login.*"))

    def test_notes_home_loads(self, authenticated_page: Page):
        """Test that notes home loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/")
        expect(authenticated_page).to_have_url(re.compile(r".*/notes.*"))

    def test_notes_home_has_title(self, authenticated_page: Page):
        """Test that notes home has title"""
        authenticated_page.goto(f"{BASE_URL}/notes/")
        title = authenticated_page.locator("h1, h2, .page-title")
        expect(title.first).to_be_visible()


class TestNoteListUI:
    """UI tests for note list"""

    def test_note_list_loads(self, authenticated_page: Page):
        """Test that note list loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/list/")
        expect(authenticated_page).to_have_url(re.compile(r".*/list.*"))

    def test_note_list_has_content(self, authenticated_page: Page):
        """Test that note list has content"""
        authenticated_page.goto(f"{BASE_URL}/notes/list/")
        content = authenticated_page.locator("table, .note-list, .notes, .list-group, .card")
        expect(content.first).to_be_visible()


class TestNoteCreateUI:
    """UI tests for note creation"""

    def test_note_create_loads(self, authenticated_page: Page):
        """Test that note create page loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/create/")
        expect(authenticated_page).to_have_url(re.compile(r".*/create.*"))

    def test_note_create_has_form(self, authenticated_page: Page):
        """Test that create page has form"""
        authenticated_page.goto(f"{BASE_URL}/notes/create/")
        form = authenticated_page.locator("form")
        expect(form.first).to_be_visible()

    def test_note_create_has_title_field(self, authenticated_page: Page):
        """Test that create form has title field"""
        authenticated_page.goto(f"{BASE_URL}/notes/create/")
        title_field = authenticated_page.locator("input[name='title']")
        expect(title_field.first).to_be_visible()

    def test_note_create_has_content_field(self, authenticated_page: Page):
        """Test that create form has content field"""
        authenticated_page.goto(f"{BASE_URL}/notes/create/")
        content_field = authenticated_page.locator("textarea[name='content'], textarea")
        expect(content_field.first).to_be_visible()

    def test_note_create_has_submit(self, authenticated_page: Page):
        """Test that create form has submit button"""
        authenticated_page.goto(f"{BASE_URL}/notes/create/")
        submit_btn = authenticated_page.locator("button[type='submit'], input[type='submit']")
        expect(submit_btn.first).to_be_visible()


class TestNoteCategoriesUI:
    """UI tests for note categories"""

    def test_categories_page_loads(self, authenticated_page: Page):
        """Test that categories page loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/categories/")
        expect(authenticated_page).to_have_url(re.compile(r".*/categories.*"))

    def test_categories_has_content(self, authenticated_page: Page):
        """Test that categories has content"""
        authenticated_page.goto(f"{BASE_URL}/notes/categories/")
        content = authenticated_page.locator("table, .category-list, .list-group, ul")
        expect(content.first).to_be_visible()


class TestNoteTagsUI:
    """UI tests for note tags"""

    def test_tags_page_loads(self, authenticated_page: Page):
        """Test that tags page loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/tags/")
        expect(authenticated_page).to_have_url(re.compile(r".*/tags.*"))

    def test_tags_has_content(self, authenticated_page: Page):
        """Test that tags page has content"""
        authenticated_page.goto(f"{BASE_URL}/notes/tags/")
        content = authenticated_page.locator("table, .tag-list, .list-group, ul, .tag")
        expect(content.first).to_be_visible()


class TestNoteArchiveUI:
    """UI tests for archived notes"""

    def test_archived_page_loads(self, authenticated_page: Page):
        """Test that archived notes page loads"""
        authenticated_page.goto(f"{BASE_URL}/notes/archived/")
        expect(authenticated_page).to_have_url(re.compile(r".*/archived.*"))


class TestNoteSearchUI:
    """UI tests for note search"""

    def test_search_results_page(self, authenticated_page: Page):
        """Test that search results page works"""
        authenticated_page.goto(f"{BASE_URL}/notes/search/?q=test")
        expect(authenticated_page.locator("body")).to_be_visible()
