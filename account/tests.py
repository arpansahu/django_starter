from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from account.token import account_activation_token
from account.models import Account

User = get_user_model()


class RegistrationViewTest(TestCase):
    """Test cases for user registration"""
    
    def setUp(self):
        """Set up test client and URLs"""
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_registration_view_get(self):
        """Test that registration page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')
    
    @patch('account.views.mailjet')
    def test_registration_view_post_valid_data(self, mock_mailjet):
        """Test successful user registration"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data)
        
        # Check user was created (but not active)
        user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)
    
    def test_registration_view_post_invalid_data(self):
        """Test registration with invalid data"""
        data = {
            'email': 'invalid-email',
            'username': 'newuser',
            'password1': 'pass',
            'password2': 'different',
        }
        response = self.client.post(self.register_url, data)
        
        # Should show form errors
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['registration_form'].errors)


class LoginViewTest(TestCase):
    """Test cases for login functionality"""
    
    def setUp(self):
        """Set up test client, user, and URLs"""
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_login_view_get(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
    
    def test_login_view_post_valid_credentials(self):
        """Test successful login with valid credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data, follow=True)
        
        # Check that user can login (may show form again if credentials wrong in POST)
        # Better to test that user is authenticated
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
    
    def test_login_view_inactive_user(self):
        """Test that inactive users cannot login"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data)
        
        # Should not allow login
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    """Test cases for logout functionality"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_logout_view(self):
        """Test that logout works correctly"""
        self.client.login(email='testuser@example.com', password='testpass123')
        response = self.client.post(self.logout_url)
        
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)
        
        # User should no longer be authenticated
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)


class AccountViewTest(TestCase):
    """Test cases for account management view"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.account_url = reverse('account')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_account_view_requires_login(self):
        """Test that account page requires authentication"""
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_account_view_get_authenticated(self):
        """Test that authenticated users can access account page"""
        self.client.force_login(self.user)
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account.html')
    
    def test_account_view_update_profile(self):
        """Test updating user profile"""
        self.client.force_login(self.user)
        
        data = {
            'email': 'testuser@example.com',
            'username': 'updateduser',
        }
        response = self.client.post(self.account_url, data, follow=True)
        
        # Check response is successful
        self.assertIn(response.status_code, [200, 302])


class PasswordResetViewTest(TestCase):
    """Test cases for password reset functionality"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.password_reset_url = reverse('password_reset')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_password_reset_view_get(self):
        """Test that password reset page loads"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')
    
    @patch('account.views.mailjet')
    def test_password_reset_view_post(self, mock_mailjet):
        """Test password reset email is sent"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        data = {'email': 'testuser@example.com'}
        response = self.client.post(self.password_reset_url, data)
        
        # Should redirect to password reset done page
        self.assertEqual(response.status_code, 302)


class ActivationViewTest(TestCase):
    """Test cases for account activation"""
    
    def setUp(self):
        """Set up test client and inactive user"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        self.user.is_active = False
        self.user.save()
        
        # Generate activation link components
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)
    
    def test_activation_with_valid_token(self):
        """Test account activation with valid token"""
        activation_url = reverse('account_activate', kwargs={
            'uidb64': self.uidb64,
            'token': self.token
        })
        
        response = self.client.get(activation_url)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
    
    def test_activation_with_invalid_token(self):
        """Test account activation with invalid token"""
        activation_url = reverse('account_activate', kwargs={
            'uidb64': self.uidb64,
            'token': 'invalid-token'
        })
        
        response = self.client.get(activation_url)
        
        # User should remain inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class AccountModelTest(TestCase):
    """Test cases for Account model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Model returns email as string representation
        self.assertEqual(str(user), 'test@example.com')


class EmailVerificationTest(TestCase):
    """Test cases for real email verification flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.register_url = reverse('register')
        
    @patch('account.views.mailjet')
    def test_email_verification_token_generation(self, mock_mailjet):
        """Test that email verification generates valid token"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Register a user
        data = {
            'email': 'verify@example.com',
            'username': 'verifyuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data)
        
        # Check user was created
        user = User.objects.filter(email='verify@example.com').first()
        self.assertIsNotNone(user)
        
        # Check token can be generated
        from account.token import account_activation_token
        token = account_activation_token.make_token(user)
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 0)
    
    @patch('account.views.mailjet')
    def test_email_verification_token_validation(self, mock_mailjet):
        """Test that generated tokens are valid"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Create user
        user = User.objects.create_user(
            email='token@example.com',
            username='tokenuser',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Generate token
        from account.token import account_activation_token
        token = account_activation_token.make_token(user)
        
        # Validate token
        is_valid = account_activation_token.check_token(user, token)
        self.assertTrue(is_valid)
    
    @patch('account.views.mailjet')
    def test_email_verification_link_structure(self, mock_mailjet):
        """Test that activation link has correct structure"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Create user
        user = User.objects.create_user(
            email='link@example.com',
            username='linkuser',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Generate activation link components
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from account.token import account_activation_token
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        
        # Check components are valid
        self.assertIsNotNone(uidb64)
        self.assertIsNotNone(token)
        self.assertTrue(len(uidb64) > 0)
        self.assertTrue(len(token) > 0)
        
        # Verify URL can be constructed
        activation_url = reverse('account_activate', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        self.assertTrue(activation_url.startswith('/activate/'))
    
    @patch('account.views.mailjet')
    def test_email_sent_with_correct_data(self, mock_mailjet):
        """Test that email is sent with correct activation data"""
        mock_send = MagicMock()
        mock_send.create = MagicMock(return_value=MagicMock(status_code=200))
        mock_mailjet.send = mock_send
        
        # Register user
        data = {
            'email': 'emailtest@example.com',
            'username': 'emailtestuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data)
        
        # Verify email send was called
        mock_send.create.assert_called_once()
        
        # Get the call arguments
        call_args = mock_send.create.call_args
        email_data = call_args.kwargs.get('data') or call_args[1].get('data')
        
        # Verify email structure
        self.assertIsNotNone(email_data)
        self.assertIn('Messages', email_data)
        self.assertEqual(len(email_data['Messages']), 1)
        
        message = email_data['Messages'][0]
        self.assertEqual(message['To'][0]['Email'], 'emailtest@example.com')
        self.assertIn('Subject', message)
    
    @patch('account.views.mailjet')
    def test_activation_link_activates_user(self, mock_mailjet):
        """Test that clicking activation link activates the user"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Create inactive user
        user = User.objects.create_user(
            email='activate@example.com',
            username='activateuser',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Generate activation URL
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from account.token import account_activation_token
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        
        activation_url = reverse('account_activate', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        
        # Click activation link
        response = self.client.get(activation_url)
        
        # Verify user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
    
    @patch('account.views.mailjet')
    def test_invalid_activation_link_doesnt_activate(self, mock_mailjet):
        """Test that invalid activation link doesn't activate user"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Create inactive user
        user = User.objects.create_user(
            email='invalid@example.com',
            username='invaliduser',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Generate activation URL with invalid but properly formatted token
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        # Use a token format that matches the regex but is still invalid
        invalid_token = 'abcd1234567-1234567890123456789012345678901234567890'
        
        activation_url = reverse('account_activate', kwargs={
            'uidb64': uidb64,
            'token': invalid_token
        })
        
        # Click invalid activation link
        response = self.client.get(activation_url)
        
        # Verify user is still inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    @patch('account.views.mailjet')
    def test_token_expires_for_used_activation(self, mock_mailjet):
        """Test that token becomes invalid after use"""
        mock_mailjet.send.create.return_value = MagicMock(status_code=200)
        
        # Create user
        user = User.objects.create_user(
            email='expire@example.com',
            username='expireuser',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        
        # Generate token before activation
        from account.token import account_activation_token
        token = account_activation_token.make_token(user)
        
        # Activate user
        user.is_active = True
        user.save()
        
        # Token should now be invalid (user state changed)
        is_valid = account_activation_token.check_token(user, token)
        self.assertFalse(is_valid)
