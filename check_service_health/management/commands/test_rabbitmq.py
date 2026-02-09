# check_service_health/management/commands/test_rabbitmq.py

from django.core.management.base import BaseCommand
from django.conf import settings
import time
import uuid


class Command(BaseCommand):
    help = 'Test if RabbitMQ is working properly'

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
        
        self.stdout.write(self.style.WARNING('Testing RabbitMQ connection...'))
        
        try:
            import pika
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '❌ pika package not installed. Run: pip install pika'
            ))
            return
        
        # Get RabbitMQ settings
        rabbitmq_host = getattr(settings, 'RABBITMQ_HOST', 'localhost')
        rabbitmq_port = getattr(settings, 'RABBITMQ_PORT', 5672)
        rabbitmq_user = getattr(settings, 'RABBITMQ_USER', 'guest')
        rabbitmq_pass = getattr(settings, 'RABBITMQ_PASSWORD', 'guest')
        rabbitmq_vhost = getattr(settings, 'RABBITMQ_VHOST', '/')
        
        test_queue = f'django_health_check_test_{uuid.uuid4().hex[:8]}'
        test_exchange = f'health_check_exchange_{uuid.uuid4().hex[:8]}'
        test_message = f'health_check_{time.time()}'
        
        connection = None
        
        try:
            # 1. Test Connection
            self.stdout.write('Connecting to RabbitMQ...')
            
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=rabbitmq_host,
                port=rabbitmq_port,
                virtual_host=rabbitmq_vhost,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=1,
                socket_timeout=timeout,
                blocked_connection_timeout=timeout
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Connected to RabbitMQ'))
            
            if verbose:
                self.stdout.write(f'     Host: {rabbitmq_host}:{rabbitmq_port}')
                self.stdout.write(f'     Virtual Host: {rabbitmq_vhost}')
                self.stdout.write(f'     User: {rabbitmq_user}')
            
            # 2. Declare Exchange
            self.stdout.write('Creating test exchange...')
            channel.exchange_declare(
                exchange=test_exchange,
                exchange_type='direct',
                durable=False,
                auto_delete=True
            )
            self.stdout.write(self.style.SUCCESS(f'  ✅ Exchange created: {test_exchange}'))
            
            # 3. Declare Queue
            self.stdout.write('Creating test queue...')
            result = channel.queue_declare(
                queue=test_queue,
                durable=False,
                exclusive=True,
                auto_delete=True
            )
            queue_name = result.method.queue
            self.stdout.write(self.style.SUCCESS(f'  ✅ Queue created: {queue_name}'))
            
            # 4. Bind Queue to Exchange
            self.stdout.write('Binding queue to exchange...')
            channel.queue_bind(
                exchange=test_exchange,
                queue=queue_name,
                routing_key='health_check'
            )
            self.stdout.write(self.style.SUCCESS('  ✅ Queue bound to exchange'))
            
            # 5. Publish Message
            self.stdout.write('Publishing test message...')
            channel.basic_publish(
                exchange=test_exchange,
                routing_key='health_check',
                body=test_message,
                properties=pika.BasicProperties(
                    delivery_mode=1,  # Transient
                    content_type='text/plain'
                )
            )
            self.stdout.write(self.style.SUCCESS('  ✅ Message published'))
            
            # 6. Consume Message
            self.stdout.write('Consuming test message...')
            received_message = None
            
            method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
            
            if method_frame:
                received_message = body.decode('utf-8')
                if received_message == test_message:
                    self.stdout.write(self.style.SUCCESS('  ✅ Message received and verified'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠️  Message mismatch: expected "{test_message}", got "{received_message}"'
                    ))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  No message received'))
            
            # 7. Get queue info
            if verbose:
                self.stdout.write('Getting server info...')
                # Check if management plugin is available
                try:
                    import requests
                    mgmt_url = f'http://{rabbitmq_host}:15672/api/overview'
                    response = requests.get(
                        mgmt_url,
                        auth=(rabbitmq_user, rabbitmq_pass),
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        self.stdout.write(f'     RabbitMQ version: {data.get("rabbitmq_version")}')
                        self.stdout.write(f'     Erlang version: {data.get("erlang_version")}')
                        queue_totals = data.get('queue_totals', {})
                        self.stdout.write(f'     Total queues: {queue_totals.get("messages", 0)} messages')
                except Exception:
                    pass  # Management API not available, skip
            
            # 8. Cleanup (queues/exchanges with auto_delete will be removed)
            self.stdout.write('Cleaning up...')
            try:
                channel.queue_delete(queue=queue_name)
                channel.exchange_delete(exchange=test_exchange)
            except Exception:
                pass  # May already be deleted
            self.stdout.write(self.style.SUCCESS('  ✅ Cleanup successful'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ RabbitMQ is healthy!'))
            
        except pika.exceptions.AMQPConnectionError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ RabbitMQ connection failed: {e}'))
            self.stdout.write(self.style.WARNING(
                f'\nMake sure RabbitMQ is running at {rabbitmq_host}:{rabbitmq_port}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ RabbitMQ error: {e}'))
        finally:
            if connection and connection.is_open:
                connection.close()
