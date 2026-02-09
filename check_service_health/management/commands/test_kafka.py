# check_service_health/management/commands/test_kafka.py

from django.core.management.base import BaseCommand
from django.conf import settings
import time
import uuid


class Command(BaseCommand):
    help = 'Test if Kafka is working properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed output'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Connection timeout in seconds (default: 10)'
        )

    def handle(self, *args, **options):
        verbose = options.get('detailed', False)
        timeout = options.get('timeout', 10)
        
        self.stdout.write(self.style.WARNING('Testing Kafka connection...'))
        
        try:
            from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
            from kafka.admin import NewTopic
            from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '❌ kafka-python package not installed. Run: pip install kafka-python'
            ))
            return
        
        # Get Kafka settings
        kafka_host = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        if isinstance(kafka_host, str):
            bootstrap_servers = kafka_host.split(',')
        else:
            bootstrap_servers = kafka_host
        
        # Get SASL/SSL settings
        security_protocol = getattr(settings, 'KAFKA_SECURITY_PROTOCOL', None)
        sasl_mechanism = getattr(settings, 'KAFKA_SASL_MECHANISM', None)
        sasl_username = getattr(settings, 'KAFKA_SASL_USERNAME', None)
        sasl_password = getattr(settings, 'KAFKA_SASL_PASSWORD', None)
        
        # Build connection kwargs
        connection_kwargs = {
            'bootstrap_servers': bootstrap_servers,
            'client_id': 'health_check_admin',
            'request_timeout_ms': timeout * 1000,
            'api_version': (3, 9, 0),  # Explicit API version for newer Kafka
        }
        
        # Add SASL/SSL if configured
        if security_protocol:
            connection_kwargs['security_protocol'] = security_protocol
        if sasl_mechanism:
            connection_kwargs['sasl_mechanism'] = sasl_mechanism
        if sasl_username:
            connection_kwargs['sasl_plain_username'] = sasl_username
        if sasl_password:
            connection_kwargs['sasl_plain_password'] = sasl_password
        
        test_topic = f'django_health_check_test_{uuid.uuid4().hex[:8]}'
        test_message = f'health_check_{time.time()}'
        
        # Producer/consumer kwargs (similar but without client_id)
        producer_kwargs = {k: v for k, v in connection_kwargs.items() if k != 'client_id'}
        producer_kwargs['value_serializer'] = lambda v: v.encode('utf-8')
        
        consumer_kwargs = {k: v for k, v in connection_kwargs.items() if k != 'client_id'}
        consumer_kwargs['auto_offset_reset'] = 'earliest'
        consumer_kwargs['consumer_timeout_ms'] = timeout * 1000
        consumer_kwargs['value_deserializer'] = lambda v: v.decode('utf-8')
        
        try:
            # 1. Test Admin Client (broker connectivity)
            self.stdout.write('Checking broker connectivity...')
            try:
                admin_client = KafkaAdminClient(**connection_kwargs)
                
                # Get cluster metadata
                cluster_metadata = admin_client._client.cluster
                brokers = cluster_metadata.brokers()
                
                self.stdout.write(self.style.SUCCESS(f'  ✅ Connected to Kafka cluster'))
                
                if verbose:
                    self.stdout.write(f'     Bootstrap servers: {", ".join(bootstrap_servers)}')
                    if security_protocol:
                        self.stdout.write(f'     Security: {security_protocol} / {sasl_mechanism}')
                    for broker in brokers:
                        self.stdout.write(f'     Broker: {broker.host}:{broker.port} (id: {broker.nodeId})')
                
            except NoBrokersAvailable:
                self.stdout.write(self.style.ERROR(f'  ❌ No brokers available at {bootstrap_servers}'))
                return
            
            # 2. List existing topics
            self.stdout.write('Listing topics...')
            topics = admin_client.list_topics()
            self.stdout.write(self.style.SUCCESS(f'  ✅ Found {len(topics)} topics'))
            
            if verbose and topics:
                for topic in list(topics)[:5]:
                    if not topic.startswith('_'):  # Skip internal topics
                        self.stdout.write(f'     - {topic}')
                if len(topics) > 5:
                    self.stdout.write(f'     ... and {len(topics) - 5} more')
            
            # 3. Create test topic
            self.stdout.write('Creating test topic...')
            try:
                new_topic = NewTopic(name=test_topic, num_partitions=1, replication_factor=1)
                admin_client.create_topics([new_topic])
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created topic: {test_topic}'))
            except TopicAlreadyExistsError:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Topic already exists: {test_topic}'))
            
            # 4. Test Producer
            self.stdout.write('Testing producer...')
            producer = KafkaProducer(**producer_kwargs)
            
            future = producer.send(test_topic, test_message)
            record_metadata = future.get(timeout=timeout)
            producer.flush()
            
            self.stdout.write(self.style.SUCCESS(
                f'  ✅ Message sent to partition {record_metadata.partition}, '
                f'offset {record_metadata.offset}'
            ))
            
            # 5. Test Consumer
            self.stdout.write('Testing consumer...')
            consumer = KafkaConsumer(
                test_topic,
                **consumer_kwargs
            )
            
            received = False
            for message in consumer:
                if message.value == test_message:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✅ Message received from partition {message.partition}'
                    ))
                    received = True
                    break
            
            if not received:
                self.stdout.write(self.style.WARNING('  ⚠️  Message not received (timeout)'))
            
            consumer.close()
            producer.close()
            
            # 6. Cleanup
            self.stdout.write('Cleaning up test topic...')
            try:
                admin_client.delete_topics([test_topic])
                self.stdout.write(self.style.SUCCESS('  ✅ Cleanup successful'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Cleanup warning: {e}'))
            
            admin_client.close()
            
            self.stdout.write(self.style.SUCCESS('\n✅ Kafka is healthy!'))
            
        except NoBrokersAvailable:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Kafka connection failed: No brokers available'
            ))
            self.stdout.write(self.style.WARNING(
                f'\nMake sure Kafka is running at {", ".join(bootstrap_servers)}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Kafka connection failed: {e}'))
            self.stdout.write(self.style.WARNING(
                f'\nMake sure Kafka is running at {", ".join(bootstrap_servers)}'
            ))
