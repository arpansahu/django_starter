from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class HomeViewTest(TestCase):
    """Test cases for HomeView"""
    
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        self.home_url = reverse('home')
    
    def test_home_view_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_home_view_accessible_when_logged_in(self):
        """Test that authenticated users can access home page"""
        # Force login using the force_login method
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bar.html')
    
    def test_home_view_uses_correct_template(self):
        """Test that correct template is used"""
        # Force login using the force_login method
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'bar.html')


class CeleryTaskViewsTest(TestCase):
    """Test cases for Celery task related views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.start_task_url = reverse('start-task')
        self.trigger_demo_task_url = reverse('trigger_demo_task')
    
    @patch('django_starter.views.long_running_task')
    def test_start_task_returns_task_id(self, mock_task):
        """Test that start_task returns a task ID"""
        # Mock the Celery task
        mock_task.delay.return_value = MagicMock(id='test-task-id-123')
        
        response = self.client.get(self.start_task_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'task_id': 'test-task-id-123'}
        )
        mock_task.delay.assert_called_once()
    
    @patch('django_starter.views.demo_task')
    def test_trigger_demo_task_returns_response(self, mock_task):
        """Test that trigger_demo_task returns proper JSON response"""
        # Mock the Celery task
        mock_task.delay.return_value = MagicMock(id='demo-task-id-456')
        
        response = self.client.get(self.trigger_demo_task_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['task_id'], 'demo-task-id-456')
        self.assertEqual(data['status'], 'Task has been triggered')
        mock_task.delay.assert_called_once()
    
    @patch('django_starter.views.long_running_task')
    def test_start_task_handles_post_request(self, mock_task):
        """Test that start_task handles POST requests"""
        mock_task.delay.return_value = MagicMock(id='post-task-id')
        
        response = self.client.post(self.start_task_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('task_id', response.json())


class URLRoutingTest(TestCase):
    """Test URL routing and reverse lookups"""
    
    def test_home_url_resolves(self):
        """Test that home URL resolves correctly"""
        url = reverse('home')
        self.assertEqual(url, '/')
    
    def test_start_task_url_resolves(self):
        """Test that start-task URL resolves correctly"""
        url = reverse('start-task')
        self.assertEqual(url, '/start-task/')
    
    def test_trigger_demo_task_url_resolves(self):
        """Test that trigger_demo_task URL resolves correctly"""
        url = reverse('trigger_demo_task')
        self.assertEqual(url, '/trigger-demo-task/')


class ErrorHandlingTest(TestCase):
    """Test error handling in views"""
    
    @patch('django_starter.views.long_running_task')
    def test_start_task_handles_celery_failure(self, mock_task):
        """Test that view handles Celery task failures gracefully"""
        mock_task.delay.side_effect = Exception('Celery connection error')
        
        with self.assertRaises(Exception):
            response = self.client.get(reverse('start-task'))
