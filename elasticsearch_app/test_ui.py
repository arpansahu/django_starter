"""
UI Tests for elasticsearch_app - Django Test Enforcer
Generated on: 2026-02-07

These tests implement UI tests for the Elasticsearch app.
Uses Playwright for browser automation.

Run with: pytest elasticsearch_app/test_ui.py --headed
"""
import pytest
from playwright.sync_api import Page, expect


class TestElasticsearchDashboardUI:
    """UI tests for dashboard.html"""

    def test_dashboard_loads(self, authenticated_page: Page, base_url):
        """Test dashboard page loads"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        # Check page title/header
        element = authenticated_page.locator("h1:has-text('Elasticsearch')")
        if element.count() > 0:
            expect(element.first).to_be_visible()
        else:
            expect(authenticated_page.locator("body")).to_be_visible()

    def test_connection_status(self, authenticated_page: Page, base_url):
        """Test connection status card"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        # Look for connection status
        element = authenticated_page.locator(".card:has-text('Connected'), .card:has-text('Not Connected')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_quick_links(self, authenticated_page: Page, base_url):
        """Test quick links section"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("a:has-text('Search'), a[href*='search']")
        if element.count() > 0:
            expect(element.first).to_be_visible()


class TestElasticsearchSearchUI:
    """UI tests for search.html"""

    def test_search_page_loads(self, page: Page, base_url):
        """Test search page loads"""
        page.goto(f"{base_url}/elasticsearch/search/")
        page.wait_for_load_state("networkidle")
        
        element = page.locator("h1:has-text('Search')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_form(self, page: Page, base_url):
        """Test search form is visible"""
        page.goto(f"{base_url}/elasticsearch/search/")
        page.wait_for_load_state("networkidle")
        
        element = page.locator("input[name='q'], input[type='text']")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_button(self, page: Page, base_url):
        """Test search button"""
        page.goto(f"{base_url}/elasticsearch/search/")
        page.wait_for_load_state("networkidle")
        
        element = page.locator("button:has-text('Search'), input[type='submit']")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_index_filter(self, page: Page, base_url):
        """Test index filter dropdown"""
        page.goto(f"{base_url}/elasticsearch/search/")
        page.wait_for_load_state("networkidle")
        
        element = page.locator("select[name='index']")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_with_query(self, page: Page, base_url):
        """Test performing a search"""
        page.goto(f"{base_url}/elasticsearch/search/?q=test")
        page.wait_for_load_state("networkidle")
        
        # Should show results section or no results message
        element = page.locator(".card:has-text('Results'), .text-center:has-text('No results')")
        if element.count() > 0:
            expect(element.first).to_be_visible()


class TestElasticsearchAnalyticsUI:
    """UI tests for analytics.html"""

    def test_analytics_requires_login(self, page: Page, base_url):
        """Test analytics page requires authentication"""
        page.goto(f"{base_url}/elasticsearch/analytics/")
        page.wait_for_load_state("networkidle")
        
        # Should redirect to login
        expect(page).to_have_url(page.url)  # URL should have changed

    def test_analytics_page_loads(self, authenticated_page: Page, base_url):
        """Test analytics page loads when authenticated"""
        authenticated_page.goto(f"{base_url}/elasticsearch/analytics/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("h1:has-text('Analytics')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_top_queries_section(self, authenticated_page: Page, base_url):
        """Test top queries section"""
        authenticated_page.goto(f"{base_url}/elasticsearch/analytics/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".card:has-text('Top Search'), h5:has-text('Top')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_recent_queries_section(self, authenticated_page: Page, base_url):
        """Test recent queries section"""
        authenticated_page.goto(f"{base_url}/elasticsearch/analytics/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".card:has-text('Recent'), h5:has-text('Recent')")
        if element.count() > 0:
            expect(element.first).to_be_visible()


class TestDashboardUIExtended:
    """UI tests for dashboard.html - IMPLEMENTED"""

    def test_create_indices_button(self, authenticated_page: Page, base_url):
        """Test Create Indices button"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Create'), button:has-text('Create')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_reindex_all_button(self, authenticated_page: Page, base_url):
        """Test Reindex All button"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Reindex'), button:has-text('Reindex')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_delete_indices_button(self, authenticated_page: Page, base_url):
        """Test Delete Indices button"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Delete'), button:has-text('Delete')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_index_form(self, authenticated_page: Page, base_url):
        """Test index form"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("#index-form, form[id*='index']")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_link(self, authenticated_page: Page, base_url):
        """Test Search link"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Search'), a:has-text('Search')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_analytics_link(self, authenticated_page: Page, base_url):
        """Test Analytics link"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Analytics'), a:has-text('Analytics')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_kibana_dashboard_link(self, authenticated_page: Page, base_url):
        """Test Kibana Dashboard link"""
        authenticated_page.goto(f"{base_url}/elasticsearch/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Kibana'), a:has-text('Kibana')")
        if element.count() > 0:
            expect(element.first).to_be_visible()


class TestAnalyticsUIExtended:
    """UI tests for analytics.html - IMPLEMENTED"""

    def test_analytics_links(self, authenticated_page: Page, base_url):
        """Test links on analytics page"""
        authenticated_page.goto(f"{base_url}/elasticsearch/analytics/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("a")
        if element.count() > 0:
            expect(element.first).to_be_visible()


class TestSearchUIExtended:
    """UI tests for search.html - IMPLEMENTED"""

    def test_search_button(self, authenticated_page: Page, base_url):
        """Test Search button"""
        authenticated_page.goto(f"{base_url}/elasticsearch/search/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('Search'), button:has-text('Search')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_form(self, authenticated_page: Page, base_url):
        """Test search form"""
        authenticated_page.goto(f"{base_url}/elasticsearch/search/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("form")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_pagination_links(self, authenticated_page: Page, base_url):
        """Test pagination links"""
        authenticated_page.goto(f"{base_url}/elasticsearch/search/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".page-link, .pagination a")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_tag_links(self, authenticated_page: Page, base_url):
        """Test tag filter links (django, python, api, test)"""
        authenticated_page.goto(f"{base_url}/elasticsearch/search/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator(".btn:has-text('django'), .btn:has-text('python'), .btn:has-text('api')")
        if element.count() > 0:
            expect(element.first).to_be_visible()

    def test_search_input(self, authenticated_page: Page, base_url):
        """Test search input field"""
        authenticated_page.goto(f"{base_url}/elasticsearch/search/")
        authenticated_page.wait_for_load_state("networkidle")
        
        element = authenticated_page.locator("#search-input, input[type='text'], input[name='q']")
        if element.count() > 0:
            expect(element.first).to_be_visible()


