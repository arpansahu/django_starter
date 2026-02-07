"""
Management Command: send_notifications

Sends notifications via various channels (email, SMS, webhook).
Demonstrates external service integration patterns.
"""
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from commands_app.models import CommandLog


class Command(BaseCommand):
    help = 'Send notifications via email, SMS, or webhook'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--channel',
            type=str,
            required=True,
            choices=['email', 'sms', 'webhook', 'slack'],
            help='Notification channel',
        )
        parser.add_argument(
            '--recipient',
            type=str,
            required=True,
            help='Recipient (email address, phone number, or webhook URL)',
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Notification',
            help='Notification subject/title',
        )
        parser.add_argument(
            '--message',
            type=str,
            required=True,
            help='Notification message',
        )
        parser.add_argument(
            '--template',
            type=str,
            help='Template file for the message',
        )
        parser.add_argument(
            '--data',
            type=str,
            help='JSON data for template rendering',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show notification without sending',
        )
        parser.add_argument(
            '--urgent',
            action='store_true',
            help='Mark as urgent/high priority',
        )
    
    def handle(self, *args, **options):
        channel = options['channel']
        recipient = options['recipient']
        subject = options['subject']
        message = options['message']
        dry_run = options['dry_run']
        urgent = options['urgent']
        
        self.stdout.write(f'📬 Sending notification:')
        self.stdout.write(f'   - Channel: {channel}')
        self.stdout.write(f'   - Recipient: {recipient}')
        self.stdout.write(f'   - Subject: {subject}')
        self.stdout.write(f'   - Urgent: {urgent}')
        
        # Log command
        log = CommandLog.objects.create(
            command_name='send_notifications',
            arguments={
                'channel': channel,
                'recipient': recipient,
                'subject': subject,
                'urgent': urgent,
            },
        )
        
        try:
            if dry_run:
                self.stdout.write(self.style.WARNING(f'\n⚠️  DRY RUN - Not actually sending'))
                self.stdout.write(f'\nMessage preview:')
                self.stdout.write(f'---')
                self.stdout.write(message)
                self.stdout.write(f'---')
                return
            
            # Send based on channel
            if channel == 'email':
                self._send_email(recipient, subject, message, urgent)
            elif channel == 'sms':
                self._send_sms(recipient, message)
            elif channel == 'webhook':
                self._send_webhook(recipient, subject, message, urgent)
            elif channel == 'slack':
                self._send_slack(recipient, message, urgent)
            
            log.status = 'completed'
            log.completed_at = timezone.now()
            log.exit_code = 0
            log.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Notification sent successfully'))
            
        except Exception as e:
            log.status = 'failed'
            log.completed_at = timezone.now()
            log.error_output = str(e)
            log.exit_code = 1
            log.save()
            raise CommandError(f'Failed to send notification: {e}')
    
    def _send_email(self, recipient: str, subject: str, message: str, urgent: bool):
        """Send email notification"""
        # This is a demo - in production, use Django's email backend
        self.stdout.write(f'\n   📧 Sending email to {recipient}...')
        
        # Simulate email sending
        email_config = getattr(settings, 'EMAIL_HOST', None)
        if not email_config:
            self.stdout.write(self.style.WARNING('   Email not configured - simulating send'))
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = f'{"[URGENT] " if urgent else ""}{subject}'
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = recipient
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Note: In production, use Django's send_mail
        self.stdout.write(f'   Email would be sent via {settings.EMAIL_HOST}')
    
    def _send_sms(self, recipient: str, message: str):
        """Send SMS notification"""
        self.stdout.write(f'\n   📱 Sending SMS to {recipient}...')
        
        # This would integrate with Twilio, AWS SNS, etc.
        self.stdout.write(self.style.WARNING('   SMS not configured - simulating send'))
    
    def _send_webhook(self, url: str, subject: str, message: str, urgent: bool):
        """Send webhook notification"""
        import urllib.request
        
        self.stdout.write(f'\n   🔗 Sending webhook to {url}...')
        
        payload = json.dumps({
            'subject': subject,
            'message': message,
            'urgent': urgent,
            'timestamp': timezone.now().isoformat(),
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                self.stdout.write(f'   Webhook response: {response.status}')
        except Exception as e:
            raise CommandError(f'Webhook failed: {e}')
    
    def _send_slack(self, webhook_url: str, message: str, urgent: bool):
        """Send Slack notification"""
        import urllib.request
        
        self.stdout.write(f'\n   💬 Sending Slack message...')
        
        payload = json.dumps({
            'text': f'{"🚨 URGENT: " if urgent else ""}{message}',
        }).encode('utf-8')
        
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                self.stdout.write(f'   Slack response: {response.status}')
        except Exception as e:
            raise CommandError(f'Slack notification failed: {e}')
