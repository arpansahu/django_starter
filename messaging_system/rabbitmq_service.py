"""
RabbitMQ Service Layer
Handles connection, message production, and consumption
"""

import pika
import json
import logging
from django.conf import settings
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Manages RabbitMQ connection with credentials"""
    
    def __init__(self):
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.vhost = settings.RABBITMQ_VHOST
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")
    
    def is_connected(self):
        """Check if connection is alive"""
        return self.connection and not self.connection.is_closed


class RabbitMQProducer:
    """Publishes messages to RabbitMQ with different routing strategies"""
    
    def __init__(self):
        self.conn = RabbitMQConnection()
    
    def setup_exchange(self, exchange_name: str, exchange_type: str = 'direct'):
        """Declare exchange"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            self.conn.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )
            logger.info(f"Exchange '{exchange_name}' declared (type: {exchange_type})")
            return True
        except Exception as e:
            logger.error(f"Failed to setup exchange: {str(e)}")
            return False
    
    def setup_queue(self, queue_name: str, dead_letter_exchange: Optional[str] = None):
        """Declare queue with optional dead letter exchange"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            arguments = {}
            if dead_letter_exchange:
                arguments['x-dead-letter-exchange'] = dead_letter_exchange
            
            self.conn.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments=arguments if arguments else None
            )
            logger.info(f"Queue '{queue_name}' declared")
            return True
        except Exception as e:
            logger.error(f"Failed to setup queue: {str(e)}")
            return False
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """Bind queue to exchange with routing key"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            self.conn.channel.queue_bind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key
            )
            logger.info(f"Queue '{queue_name}' bound to '{exchange_name}' with key '{routing_key}'")
            return True
        except Exception as e:
            logger.error(f"Failed to bind queue: {str(e)}")
            return False
    
    def publish_message(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[str, Any],
        priority: int = 0,
        message_id: Optional[str] = None
    ) -> bool:
        """Publish message to exchange with routing key"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            # Add metadata
            message['timestamp'] = datetime.now().isoformat()
            
            properties = pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                priority=priority,
                content_type='application/json',
                message_id=message_id or f"msg-{datetime.now().timestamp()}"
            )
            
            self.conn.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=properties
            )
            
            logger.info(f"Message published to {exchange}/{routing_key}: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            return False
        finally:
            self.conn.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection and return status"""
        try:
            success = self.conn.connect()
            if success:
                # Get server properties
                server_properties = self.conn.connection.server_properties if self.conn.connection else {}
                self.conn.close()
                return {
                    'status': 'success',
                    'message': 'Successfully connected to RabbitMQ',
                    'host': self.conn.host,
                    'port': self.conn.port,
                    'vhost': self.conn.vhost,
                    'server_version': server_properties.get('version', 'unknown')
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to connect to RabbitMQ',
                    'host': self.conn.host,
                    'port': self.conn.port
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'host': self.conn.host,
                'port': self.conn.port
            }


class RabbitMQConsumer:
    """Consumes messages from RabbitMQ queues"""
    
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.conn = RabbitMQConnection()
    
    def consume_messages(self, callback: Callable, auto_ack: bool = False):
        """Start consuming messages from queue"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            self.conn.channel.basic_qos(prefetch_count=1)
            self.conn.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            logger.info(f"Starting to consume from queue: {self.queue_name}")
            self.conn.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}")
        finally:
            self.conn.close()
    
    def get_message(self) -> Optional[Dict[str, Any]]:
        """Get a single message from queue (non-blocking)"""
        try:
            if not self.conn.is_connected():
                self.conn.connect()
            
            method_frame, header_frame, body = self.conn.channel.basic_get(
                queue=self.queue_name,
                auto_ack=True
            )
            
            if method_frame:
                message = json.loads(body)
                return {
                    'message': message,
                    'delivery_tag': method_frame.delivery_tag,
                    'routing_key': method_frame.routing_key
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting message: {str(e)}")
            return None
        finally:
            self.conn.close()


# Initialize global producer instance
rabbitmq_producer = RabbitMQProducer()
