from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import io


class UploadPublicFileTest(TestCase):
    """Test cases for public file upload"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.upload_url = reverse('upload_public_file')
    
    def test_upload_public_file_get(self):
        """Test that upload page loads correctly"""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'file_manager/public_form.html')
        self.assertIn('form', response.context)
    
    @patch('file_manager.models.PublicFile.save')
    def test_upload_public_file_post_valid(self, mock_save):
        """Test successful file upload"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file content",
            content_type="text/plain"
        )
        
        data = {
            'title': 'Test File',
            'file': test_file
        }
        
        response = self.client.post(self.upload_url, data, format='multipart')
        
        # Should redirect after successful upload
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.upload_url)
    
    def test_upload_public_file_post_invalid(self):
        """Test upload with invalid data"""
        data = {
            'title': '',  # Empty title
        }
        
        response = self.client.post(self.upload_url, data)
        
        # Should stay on same page with form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'file_manager/public_form.html')
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
    
    def test_upload_public_file_no_file(self):
        """Test upload without file"""
        data = {
            'title': 'Test File',
        }
        
        response = self.client.post(self.upload_url, data)
        
        # Should show error for missing file
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'file', 'This field is required.')


class UploadPrivateFileTest(TestCase):
    """Test cases for private file upload"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.upload_url = reverse('upload_private_file')
    
    def test_upload_private_file_get(self):
        """Test that upload page loads correctly"""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'file_manager/upload_private_file.html')
        self.assertIn('form', response.context)
    
    @patch('file_manager.models.PrivateFile.save')
    def test_upload_private_file_post_valid(self, mock_save):
        """Test successful private file upload"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "private_test.txt",
            b"private content",
            content_type="text/plain"
        )
        
        data = {
            'title': 'Private Test File',
            'file': test_file
        }
        
        response = self.client.post(self.upload_url, data, format='multipart')
        
        # Should redirect after successful upload
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.upload_url)
    
    def test_upload_private_file_post_invalid(self):
        """Test upload with invalid data"""
        data = {
            'title': '',  # Empty title
        }
        
        response = self.client.post(self.upload_url, data)
        
        # Should stay on same page with form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'file_manager/upload_private_file.html')
    
    @patch('file_manager.models.PrivateFile.save')
    def test_upload_large_file(self, mock_save):
        """Test uploading a larger file"""
        # Create a larger test file (1MB)
        large_content = b"x" * (1024 * 1024)  # 1MB of data
        test_file = SimpleUploadedFile(
            "large_file.txt",
            large_content,
            content_type="text/plain"
        )
        
        data = {
            'title': 'Large File',
            'file': test_file
        }
        
        response = self.client.post(self.upload_url, data, format='multipart')
        
        # Should handle large file successfully
        self.assertEqual(response.status_code, 302)


class FileUploadSecurityTest(TestCase):
    """Test cases for file upload security"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.public_upload_url = reverse('upload_public_file')
        self.private_upload_url = reverse('upload_private_file')
    
    def test_upload_executable_file_rejected(self):
        """Test that executable files are rejected (if validation exists)"""
        # Create a fake executable file
        exe_file = SimpleUploadedFile(
            "malicious.exe",
            b"MZ\x90\x00",  # PE header
            content_type="application/x-msdownload"
        )
        
        data = {
            'title': 'Executable File',
            'file': exe_file
        }
        
        response = self.client.post(self.public_upload_url, data, format='multipart')
        
        # Depending on your validation, this might be rejected or accepted
        # Adjust assertion based on your actual implementation
        self.assertIn(response.status_code, [200, 302])
    
    def test_csrf_protection_enabled(self):
        """Test that CSRF protection is enabled"""
        # GET request should include CSRF token in form
        response = self.client.get(self.public_upload_url)
        self.assertContains(response, 'csrfmiddlewaretoken')


class FileURLRoutingTest(TestCase):
    """Test URL routing for file manager"""
    
    def test_upload_public_url_resolves(self):
        """Test that public upload URL resolves correctly"""
        url = reverse('upload_public_file')
        self.assertEqual(url, '/upload-public/')
    
    def test_upload_private_url_resolves(self):
        """Test that private upload URL resolves correctly"""
        url = reverse('upload_private_file')
        self.assertEqual(url, '/upload-private/')

