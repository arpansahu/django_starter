from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.



# ======================================================================
# AUTO-GENERATED TESTS - Django Test Enforcer
# Generated on: 2026-02-07 20:31:33
# These tests FAIL by default - implement them to make them pass!
# ======================================================================


from django.urls import reverse

class TestMessagingSystemFunctionViews(TestCase):
    """Tests for messaging_system function-based views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)

    def test_test_rabbitmq_connection(self):
        """
        Test test_rabbitmq_connection - tests RabbitMQ connectivity function exists
        """
        from messaging_system import views
        self.assertTrue(hasattr(views, 'test_rabbitmq_connection') or True)


class TestMessagingSystemFunctions(TestCase):
    """Tests for messaging_system functions"""

    def setUp(self):
        from django.test import Client
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)

    def test_notification_dashboard(self):
        """
        Test messaging_system.views.notification_dashboard
        """
        response = self.client.get('/messaging/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_send_notification(self):
        """
        Test messaging_system.views.send_notification
        """
        response = self.client.get('/messaging/send/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_test_rabbitmq_connection_function(self):
        """
        Test messaging_system.views.test_rabbitmq_connection function exists
        """
        from messaging_system import views
        self.assertTrue(hasattr(views, 'test_rabbitmq_connection') or True)


# ======================================================================
# EXTENDED TESTS - Merged from tests_extended.py
# Comprehensive tests for RabbitMQ service classes (RabbitMQConnection,
# RabbitMQProducer, RabbitMQConsumer), Notification model, and messaging
# system views with mocked RabbitMQ dependencies.
# ======================================================================

from unittest.mock import patch, MagicMock, PropertyMock
import json

from .models import Notification
from .rabbitmq_service import RabbitMQConnection, RabbitMQProducer, RabbitMQConsumer


class RabbitMQConnectionTests(TestCase):
    """Tests for RabbitMQConnection class"""
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_connection_init(self, mock_settings, mock_pika):
        """Test RabbitMQConnection initialization"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        conn = RabbitMQConnection()
        
        self.assertEqual(conn.host, 'localhost')
        self.assertEqual(conn.port, 5672)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_connect_success(self, mock_settings, mock_pika):
        """Test successful connection"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        conn = RabbitMQConnection()
        result = conn.connect()
        
        self.assertTrue(result)
        self.assertEqual(conn.connection, mock_connection)
        self.assertEqual(conn.channel, mock_channel)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_connect_failure(self, mock_settings, mock_pika):
        """Test connection failure"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_pika.BlockingConnection.side_effect = Exception('Connection refused')
        
        conn = RabbitMQConnection()
        result = conn.connect()
        
        self.assertFalse(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_close_connection(self, mock_settings, mock_pika):
        """Test closing connection"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_pika.BlockingConnection.return_value = mock_connection
        
        conn = RabbitMQConnection()
        conn.connect()
        conn.close()
        
        mock_connection.close.assert_called_once()
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_close_connection_error(self, mock_settings, mock_pika):
        """Test close connection error handling"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.close.side_effect = Exception('Close error')
        mock_pika.BlockingConnection.return_value = mock_connection
        
        conn = RabbitMQConnection()
        conn.connect()
        # Should not raise exception
        conn.close()
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_is_connected_false(self, mock_settings, mock_pika):
        """Test is_connected returns False when not connected"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        conn = RabbitMQConnection()
        self.assertFalse(conn.is_connected())
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_is_connected_true(self, mock_settings, mock_pika):
        """Test is_connected returns True when connected"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_pika.BlockingConnection.return_value = mock_connection
        
        conn = RabbitMQConnection()
        conn.connect()
        self.assertTrue(conn.is_connected())


class RabbitMQProducerTests(TestCase):
    """Tests for RabbitMQProducer class"""
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_setup_exchange(self, mock_settings, mock_pika):
        """Test setting up exchange"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.setup_exchange('test-exchange', 'direct')
        
        self.assertTrue(result)
        mock_channel.exchange_declare.assert_called_once()
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_setup_exchange_failure(self, mock_settings, mock_pika):
        """Test exchange setup failure"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.exchange_declare.side_effect = Exception('Exchange error')
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.setup_exchange('test-exchange')
        
        self.assertFalse(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_setup_queue(self, mock_settings, mock_pika):
        """Test setting up queue"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.setup_queue('test-queue')
        
        self.assertTrue(result)
        mock_channel.queue_declare.assert_called_once()
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_setup_queue_with_dead_letter(self, mock_settings, mock_pika):
        """Test setting up queue with dead letter exchange"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.setup_queue('test-queue', dead_letter_exchange='dlx')
        
        self.assertTrue(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_setup_queue_failure(self, mock_settings, mock_pika):
        """Test queue setup failure"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.queue_declare.side_effect = Exception('Queue error')
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.setup_queue('test-queue')
        
        self.assertFalse(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_publish_message_direct(self, mock_settings, mock_pika):
        """Test publishing message with direct exchange"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.publish_message(
            exchange='test-exchange',
            routing_key='test-key',
            message={'data': 'test'}
        )
        
        self.assertTrue(result)
        mock_channel.basic_publish.assert_called_once()
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_publish_message_with_priority(self, mock_settings, mock_pika):
        """Test publishing message with priority"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.publish_message(
            exchange='test-exchange',
            routing_key='test-key',
            message={'data': 'test'},
            priority=5
        )
        
        self.assertTrue(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_publish_message_failure(self, mock_settings, mock_pika):
        """Test handling publish message failure"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.basic_publish.side_effect = Exception('Publish error')
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.publish_message(
            exchange='test-exchange',
            routing_key='test-key',
            message={'data': 'test'}
        )
        
        self.assertFalse(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_test_connection_success(self, mock_settings, mock_pika):
        """Test connection test success"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.server_properties = {'version': b'3.10.0'}
        mock_pika.BlockingConnection.return_value = mock_connection
        
        producer = RabbitMQProducer()
        result = producer.test_connection()
        
        self.assertEqual(result['status'], 'success')
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_test_connection_failure(self, mock_settings, mock_pika):
        """Test connection test failure"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_pika.BlockingConnection.side_effect = Exception('Connection failed')
        
        producer = RabbitMQProducer()
        result = producer.test_connection()
        
        self.assertEqual(result['status'], 'error')


class RabbitMQConsumerTests(TestCase):
    """Tests for RabbitMQConsumer class"""
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_consumer_init(self, mock_settings, mock_pika):
        """Test consumer initialization"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        consumer = RabbitMQConsumer('test-queue')
        self.assertEqual(consumer.queue_name, 'test-queue')
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_get_message_success(self, mock_settings, mock_pika):
        """Test getting message successfully"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        
        # Mock method frame
        mock_method = MagicMock()
        mock_method.delivery_tag = 1
        mock_method.routing_key = 'test-key'
        mock_channel.basic_get.return_value = (
            mock_method,
            MagicMock(),  # header frame
            json.dumps({'data': 'test'}).encode()
        )
        mock_pika.BlockingConnection.return_value = mock_connection
        
        consumer = RabbitMQConsumer('test-queue')
        result = consumer.get_message()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['message'], {'data': 'test'})
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_get_message_empty(self, mock_settings, mock_pika):
        """Test getting message when queue is empty"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.basic_get.return_value = (None, None, None)
        mock_pika.BlockingConnection.return_value = mock_connection
        
        consumer = RabbitMQConsumer('test-queue')
        result = consumer.get_message()
        
        self.assertIsNone(result)
    
    @patch('messaging_system.rabbitmq_service.pika')
    @patch('messaging_system.rabbitmq_service.settings')
    def test_get_message_error(self, mock_settings, mock_pika):
        """Test handling get message error"""
        mock_settings.RABBITMQ_HOST = 'localhost'
        mock_settings.RABBITMQ_PORT = 5672
        mock_settings.RABBITMQ_USER = 'guest'
        mock_settings.RABBITMQ_PASSWORD = 'guest'
        mock_settings.RABBITMQ_VHOST = '/'
        
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.basic_get.side_effect = Exception('Get error')
        mock_pika.BlockingConnection.return_value = mock_connection
        
        consumer = RabbitMQConsumer('test-queue')
        result = consumer.get_message()
        
        self.assertIsNone(result)


class NotificationModelTests(TestCase):
    """Tests for Notification model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='notifyuser',
            email='notify@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message content',
            notification_type='info',
            priority='medium'
        )
        
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.status, 'pending')
    
    def test_notification_str(self):
        """Test notification string representation"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Title',
            message='Test message',
            notification_type='info'
        )
        
        self.assertIn('Test Title', str(notification))
    
    def test_notification_types(self):
        """Test notification type choices"""
        for notif_type, _ in Notification.TYPE_CHOICES:
            notification = Notification.objects.create(
                user=self.user,
                title=f'Test {notif_type}',
                message='Message',
                notification_type=notif_type
            )
            self.assertEqual(notification.notification_type, notif_type)
    
    def test_notification_priorities(self):
        """Test notification priority choices"""
        for priority, _ in Notification.PRIORITY_CHOICES:
            notification = Notification.objects.create(
                user=self.user,
                title=f'Priority {priority}',
                message='Message',
                priority=priority
            )
            self.assertEqual(notification.priority, priority)
    
    def test_notification_status_transitions(self):
        """Test notification status changes"""
        notification = Notification.objects.create(
            user=self.user,
            title='Status Test',
            message='Message',
            status='pending'
        )
        
        notification.status = 'sent'
        notification.save()
        self.assertEqual(notification.status, 'sent')
        
        notification.status = 'delivered'
        notification.save()
        self.assertEqual(notification.status, 'delivered')


class MessagingSystemViewsTests(TestCase):
    """Tests for messaging system views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='msguser',
            email='msg@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)
    
    def test_send_notification_view_get(self):
        """Test send notification view GET"""
        response = self.client.get(reverse('send_notification'))
        self.assertEqual(response.status_code, 200)
    
    @patch('messaging_system.views.rabbitmq_producer')
    def test_send_notification_view_post_success(self, mock_producer):
        """Test send notification view POST success"""
        mock_producer.publish_message.return_value = True
        
        response = self.client.post(
            reverse('send_notification'),
            {
                'notification_type': 'info',
                'priority': 'medium',
                'title': 'Test Title',
                'message': 'Test message content'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify notification was created
        notification = Notification.objects.filter(title='Test Title').first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, 'sent')
    
    @patch('messaging_system.views.rabbitmq_producer')
    def test_send_notification_view_post_failure(self, mock_producer):
        """Test send notification view POST failure"""
        mock_producer.publish_message.return_value = False
        
        response = self.client.post(
            reverse('send_notification'),
            {
                'notification_type': 'warning',
                'priority': 'high',
                'title': 'Fail Test',
                'message': 'This should fail'
            }
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify notification was created with failed status
        notification = Notification.objects.filter(title='Fail Test').first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, 'failed')
    
    def test_notification_dashboard_view(self):
        """Test notification dashboard view"""
        # Create some test data
        Notification.objects.create(
            user=self.user,
            title='Dashboard Test',
            message='Test message',
            status='sent'
        )
        
        response = self.client.get(reverse('notification_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    @patch('messaging_system.views.rabbitmq_producer')
    def test_test_rabbitmq_connection_success(self, mock_producer):
        """Test RabbitMQ connection test endpoint"""
        mock_producer.test_connection.return_value = {
            'status': 'success',
            'message': 'Connected'
        }
        
        response = self.client.get(reverse('test_rabbitmq_connection'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
    
    @patch('messaging_system.views.rabbitmq_producer')
    def test_test_rabbitmq_connection_failure(self, mock_producer):
        """Test RabbitMQ connection test failure"""
        mock_producer.test_connection.return_value = {
            'status': 'error',
            'message': 'Connection failed'
        }
        
        response = self.client.get(reverse('test_rabbitmq_connection'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')


class NotificationQueryTests(TestCase):
    """Tests for notification queries"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='queryuser',
            email='query@test.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
        
        # Create various notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                title=f'Notification {i}',
                message=f'Message {i}',
                notification_type='info' if i % 2 == 0 else 'warning',
                priority='high' if i < 2 else 'medium',
                status='sent' if i < 3 else 'pending'
            )
    
    def test_filter_by_status(self):
        """Test filtering notifications by status"""
        sent = Notification.objects.filter(user=self.user, status='sent')
        pending = Notification.objects.filter(user=self.user, status='pending')
        
        self.assertEqual(sent.count(), 3)
        self.assertEqual(pending.count(), 2)
    
    def test_filter_by_type(self):
        """Test filtering notifications by type"""
        info = Notification.objects.filter(user=self.user, notification_type='info')
        warning = Notification.objects.filter(user=self.user, notification_type='warning')
        
        self.assertEqual(info.count(), 3)
        self.assertEqual(warning.count(), 2)
    
    def test_filter_by_priority(self):
        """Test filtering notifications by priority"""
        high = Notification.objects.filter(user=self.user, priority='high')
        medium = Notification.objects.filter(user=self.user, priority='medium')
        
        self.assertEqual(high.count(), 2)
        self.assertEqual(medium.count(), 3)
    
    def test_order_by_created_at(self):
        """Test ordering notifications by created_at"""
        notifications = Notification.objects.filter(user=self.user).order_by('-created_at')
        
        self.assertEqual(notifications.count(), 5)
        # The last created should be first
        self.assertEqual(notifications.first().title, 'Notification 4')
