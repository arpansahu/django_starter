"""
Kafka Service Layer
Handles Kafka producers, consumers, and stream processing
"""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
from django.conf import settings
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import ssl

logger = logging.getLogger(__name__)


class KafkaConnection:
    """Manages Kafka connection configuration"""
    
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
        self.security_protocol = settings.KAFKA_SECURITY_PROTOCOL
        self.sasl_mechanism = settings.KAFKA_SASL_MECHANISM
        self.sasl_username = settings.KAFKA_SASL_USERNAME
        self.sasl_password = settings.KAFKA_SASL_PASSWORD
    
    def get_config(self) -> Dict[str, Any]:
        """Get common Kafka configuration"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
        }
        
        if self.security_protocol in ['SASL_SSL', 'SASL_PLAINTEXT']:
            config['security_protocol'] = self.security_protocol
            config['sasl_mechanism'] = self.sasl_mechanism
            config['sasl_plain_username'] = self.sasl_username
            config['sasl_plain_password'] = self.sasl_password
            
            if self.security_protocol == 'SASL_SSL':
                # For SASL_SSL, configure SSL context
                # Note: Using CERT_NONE for development with self-signed certs
                # For production, use CERT_REQUIRED with proper CA certificates
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False  # Disable for self-signed certs
                ssl_context.verify_mode = ssl.CERT_NONE  # Accept self-signed certs
                
                # TODO: For production security, use:
                # ssl_context.verify_mode = ssl.CERT_REQUIRED
                # ssl_context.load_verify_locations(cafile='/path/to/ca-cert')
                # If mutual TLS: ssl_context.load_cert_chain(certfile, keyfile, password)
                
                config['ssl_context'] = ssl_context
        
        return config


class KafkaProducerService:
    """Produces messages to Kafka topics"""
    
    def __init__(self):
        self.conn = KafkaConnection()
        self.producer = None
    
    def get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self.producer is None:
            config = self.conn.get_config()
            config.update({
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'acks': 'all',  # Wait for all replicas
                'retries': 3,
                'max_in_flight_requests_per_connection': 1
            })
            
            try:
                self.producer = KafkaProducer(**config)
                logger.info("Kafka producer created successfully")
            except Exception as e:
                logger.error(f"Failed to create Kafka producer: {str(e)}")
                raise
        
        return self.producer
    
    def send_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """Send message to Kafka topic"""
        try:
            producer = self.get_producer()
            
            # Add metadata
            message['timestamp'] = datetime.now().isoformat()
            
            future = producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent to {topic} "
                f"[partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset}]"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def send_batch(
        self,
        topic: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send multiple messages to Kafka topic"""
        try:
            producer = self.get_producer()
            success_count = 0
            failed_count = 0
            
            for message in messages:
                message['timestamp'] = datetime.now().isoformat()
                try:
                    future = producer.send(topic, value=message)
                    future.get(timeout=10)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message in batch: {str(e)}")
                    failed_count += 1
            
            producer.flush()
            
            return {
                'total': len(messages),
                'success': success_count,
                'failed': failed_count
            }
            
        except Exception as e:
            logger.error(f"Batch send failed: {str(e)}")
            return {
                'total': len(messages),
                'success': 0,
                'failed': len(messages),
                'error': str(e)
            }
    
    def close(self):
        """Close producer"""
        if self.producer:
            self.producer.close()
            self.producer = None
            logger.info("Kafka producer closed")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Kafka connection"""
        try:
            producer = self.get_producer()
            # Try to get cluster metadata
            metadata = producer.bootstrap_connected()
            
            if metadata:
                return {
                    'status': 'success',
                    'message': 'Successfully connected to Kafka',
                    'bootstrap_servers': self.conn.bootstrap_servers,
                    'security_protocol': self.conn.security_protocol
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to connect to Kafka bootstrap servers',
                    'bootstrap_servers': self.conn.bootstrap_servers
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'bootstrap_servers': self.conn.bootstrap_servers
            }


class KafkaConsumerService:
    """Consumes messages from Kafka topics"""
    
    def __init__(self, topics: List[str], group_id: str):
        self.topics = topics
        self.group_id = group_id
        self.conn = KafkaConnection()
        self.consumer = None
    
    def get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer"""
        if self.consumer is None:
            config = self.conn.get_config()
            config.update({
                'group_id': self.group_id,
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': True,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda k: k.decode('utf-8') if k else None,
            })
            
            try:
                self.consumer = KafkaConsumer(*self.topics, **config)
                logger.info(f"Kafka consumer created for topics: {self.topics}")
            except Exception as e:
                logger.error(f"Failed to create Kafka consumer: {str(e)}")
                raise
        
        return self.consumer
    
    def consume_messages(self, callback, max_messages: Optional[int] = None):
        """Consume messages and process with callback"""
        try:
            consumer = self.get_consumer()
            message_count = 0
            
            for message in consumer:
                try:
                    callback(message)
                    message_count += 1
                    
                    if max_messages and message_count >= max_messages:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
            
            logger.info(f"Consumed {message_count} messages")
            
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}")
        finally:
            self.close()
    
    def get_messages(self, max_messages: int = 10, timeout_ms: int = 5000) -> List[Dict[str, Any]]:
        """Get batch of messages"""
        try:
            consumer = self.get_consumer()
            messages = []
            
            records = consumer.poll(timeout_ms=timeout_ms, max_records=max_messages)
            
            for topic_partition, msgs in records.items():
                for msg in msgs:
                    messages.append({
                        'topic': msg.topic,
                        'partition': msg.partition,
                        'offset': msg.offset,
                        'key': msg.key,
                        'value': msg.value,
                        'timestamp': msg.timestamp
                    })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
        finally:
            self.close()
    
    def close(self):
        """Close consumer"""
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            logger.info("Kafka consumer closed")


class KafkaAdminService:
    """Manage Kafka topics and configurations"""
    
    def __init__(self):
        self.conn = KafkaConnection()
    
    def create_topics(self, topics: List[str], num_partitions: int = 3, replication_factor: int = 1) -> Dict[str, Any]:
        """Create Kafka topics"""
        try:
            config = self.conn.get_config()
            admin_client = KafkaAdminClient(**config)
            
            topic_list = [
                NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)
                for topic in topics
            ]
            
            result = admin_client.create_topics(new_topics=topic_list, validate_only=False)
            admin_client.close()
            
            return {
                'status': 'success',
                'message': f'Created {len(topics)} topics',
                'topics': topics
            }
            
        except Exception as e:
            logger.error(f"Failed to create topics: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def list_topics(self) -> List[str]:
        """List all Kafka topics"""
        try:
            config = self.conn.get_config()
            admin_client = KafkaAdminClient(**config)
            topics = admin_client.list_topics()
            admin_client.close()
            return topics
        except Exception as e:
            logger.error(f"Failed to list topics: {str(e)}")
            return []


# Initialize global instances
kafka_producer = KafkaProducerService()
kafka_admin = KafkaAdminService()
