# check_service_health/management/commands/test_email.py

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test if email service (MailJet) is configured and working properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed output'
        )
        parser.add_argument(
            '--send-test',
            type=str,
            metavar='EMAIL',
            help='Send a test email to this address'
        )

    def handle(self, *args, **options):
        verbose = options.get('detailed', False)
        test_email = options.get('send_test')
        
        self.stdout.write(self.style.WARNING('Testing MailJet Email configuration...'))
        
        # 1. Check MailJet API settings
        self.stdout.write('Checking MailJet API settings...')
        
        # Check for MailJet specific settings (your project uses these)
        mailjet_api_key = getattr(settings, 'MAIL_JET_API_KEY', None)
        mailjet_secret_key = getattr(settings, 'MAIL_JET_API_SECRET', None)
        
        if verbose:
            self.stdout.write(f'     API Key: {mailjet_api_key[:10]}***' if mailjet_api_key else '     API Key: Not set')
            self.stdout.write(f'     Secret Key: {mailjet_secret_key[:5]}***' if mailjet_secret_key else '     Secret Key: Not set')
        
        # Validate settings
        issues = []
        
        if not mailjet_api_key:
            issues.append('MAIL_JET_API_KEY is not configured')
        
        if not mailjet_secret_key:
            issues.append('MAIL_JET_API_SECRET is not configured')
        
        if issues:
            self.stdout.write(self.style.ERROR('  ❌ MailJet configuration issues:'))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f'     - {issue}'))
            return
        
        self.stdout.write(self.style.SUCCESS('  ✅ MailJet API credentials configured'))
        
        # 2. Test MailJet API connection
        self.stdout.write('Testing MailJet API connection...')
        
        try:
            from mailjet_rest import Client
            
            mailjet = Client(
                auth=(mailjet_api_key, mailjet_secret_key),
                version='v3'
            )
            
            # Get account info / sender list
            result = mailjet.sender.get()
            
            if result.status_code == 200:
                self.stdout.write(self.style.SUCCESS('  ✅ MailJet API connection successful'))
                
                senders = result.json().get('Data', [])
                if verbose and senders:
                    self.stdout.write(f'     Found {len(senders)} verified sender(s):')
                    for sender in senders[:5]:
                        status = '✅' if sender.get('Status') == 'Active' else '⚠️'
                        self.stdout.write(f'       {status} {sender.get("Email")}')
                elif senders:
                    active_senders = [s for s in senders if s.get('Status') == 'Active']
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Found {len(active_senders)} active sender(s)'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  No verified senders found'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ❌ MailJet API returned status {result.status_code}'
                ))
                if verbose:
                    self.stdout.write(f'     Response: {result.json()}')
                return
                
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '  ❌ mailjet-rest package not installed. Run: pip install mailjet-rest'
            ))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ MailJet API error: {e}'))
            return
        
        # 3. Check API statistics (optional)
        if verbose:
            self.stdout.write('Checking API statistics...')
            try:
                stats = mailjet.statcounters.get()
                if stats.status_code == 200:
                    data = stats.json().get('Data', [{}])[0] if stats.json().get('Data') else {}
                    self.stdout.write(f'     Messages sent: {data.get("MessageSentCount", "N/A")}')
                    self.stdout.write(f'     Messages opened: {data.get("MessageOpenedCount", "N/A")}')
            except Exception:
                pass  # Stats not critical
        
        # 4. Send test email if requested
        if test_email:
            self.stdout.write(f'Sending test email to {test_email}...')
            try:
                mailjet_v31 = Client(
                    auth=(mailjet_api_key, mailjet_secret_key),
                    version='v3.1'
                )
                
                # Get first active sender
                active_sender = None
                for sender in senders:
                    if sender.get('Status') == 'Active':
                        active_sender = sender.get('Email')
                        break
                
                if not active_sender:
                    active_sender = 'noreply@example.com'
                
                data = {
                    'Messages': [
                        {
                            'From': {
                                'Email': active_sender,
                                'Name': 'Django Starter Health Check'
                            },
                            'To': [
                                {
                                    'Email': test_email,
                                    'Name': 'Test Recipient'
                                }
                            ],
                            'Subject': 'Django Starter - Health Check Test Email',
                            'TextPart': 'This is a test email from Django Starter health check.\n\n'
                                       'If you received this email, your MailJet configuration is working!',
                            'HTMLPart': '<h3>Django Starter Health Check</h3>'
                                       '<p>This is a test email from Django Starter health check.</p>'
                                       '<p>If you received this email, your MailJet configuration is working!</p>'
                        }
                    ]
                }
                
                result = mailjet_v31.send.create(data=data)
                
                if result.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Test email sent to {test_email}'))
                else:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ Failed to send email: {result.status_code}'
                    ))
                    if verbose:
                        self.stdout.write(f'     Response: {result.json()}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Failed to send test email: {e}'))
                return
        
        self.stdout.write(self.style.SUCCESS('\n✅ MailJet email service is healthy!'))
        
        if not test_email:
            self.stdout.write(self.style.WARNING(
                '\nTip: Run with --send-test your@email.com to send a test email'
            ))
