# Facebook Data Deletion Callback Setup

## Overview
Facebook requires all apps using Facebook Login to provide a **Data Deletion Callback URL**. This is a mandatory requirement for app review and compliance with Facebook Platform Policy.

## Data Deletion Callback URL

### Local Development
```
http://127.0.0.1:8016/data-deletion-callback/
```

### Production
```
https://yourdomain.com/data-deletion-callback/
```

## How to Configure in Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your app
3. Navigate to **App Settings** → **Basic**
4. Scroll down to **Data Deletion Instructions URL**
5. Enter your Data Deletion Callback URL:
   - Production: `https://yourdomain.com/data-deletion-callback/`
6. Click **Save Changes**

## What This Page Does

The data deletion callback page (`/data-deletion-callback/`):

✅ **Public Access** - No login required (Facebook users may not have accounts on your site)

✅ **Information Display**:
- What data is collected via Facebook Login
- How data is deleted (step-by-step timeline)
- Automatic deletion process when app is removed from Facebook

✅ **Manual Deletion Request Form**:
- Users can submit deletion requests via form
- Requires email and optional reason
- Shows confirmation message after submission

✅ **Alternative Methods**:
- Link to account settings for logged-in users
- Email contact information
- Direct support contact

✅ **Compliance**:
- Meets Facebook Platform Policy requirements
- Shows clear timeline (immediate, 7 days, 30 days, 90 days)
- Provides multiple ways to request deletion

## Data Deletion Timeline

When a user removes the Facebook app or requests deletion:

| Timeline | Action |
|----------|--------|
| **Immediate** | Account deactivated |
| **Within 7 Days** | Personal data anonymized |
| **Within 30 Days** | All data permanently deleted |
| **Within 90 Days** | Removed from backups |

## Automatic Deletion

When users remove your app from Facebook:
- Facebook sends a deauthorization callback
- Your app receives notification (via webhook if configured)
- Deletion process begins automatically within 48 hours

## Testing the Implementation

### Manual Test
1. Visit: `http://127.0.0.1:8016/data-deletion-callback/`
2. Verify all information sections are displayed
3. Test the deletion request form
4. Check that success message appears after submission

### Automated Tests
```bash
python manage.py test account.tests.DataDeletionCallbackViewTest
```

All 6 tests should pass:
- ✅ Page loads without authentication
- ✅ No login required (public access)
- ✅ Displays required information
- ✅ Form submission works
- ✅ Optional fields are optional
- ✅ Timeline information is displayed

## Production Considerations

### 1. Email Notifications
When a deletion request is submitted, you may want to:
```python
# In DataDeletionCallbackView.post()
from django.core.mail import send_mail

send_mail(
    subject='Data Deletion Request',
    message=f'Deletion request from: {email}\nReason: {reason}',
    from_email='admin@yourdomain.com',
    recipient_list=['admin@yourdomain.com'],
)
```

### 2. Database Logging
Store deletion requests for compliance:
```python
# Create a model to track requests
class DataDeletionRequest(models.Model):
    email = models.EmailField()
    reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
```

### 3. Facebook Deauthorization Webhook
To handle automatic deletion when users remove your app:

Add to `urls.py`:
```python
path('facebook/deauthorize/', FacebookDeauthorizeView.as_view(), name='facebook_deauthorize'),
```

Create view to handle Facebook's deauthorization callback:
```python
class FacebookDeauthorizeView(View):
    def post(self, request):
        # Parse signed_request from Facebook
        # Extract user_id
        # Queue deletion task
        pass
```

### 4. Celery Task for Deletion
Create an async task to handle the actual deletion:
```python
@shared_task
def process_data_deletion(email):
    try:
        user = Account.objects.get(email=email)
        user.delete()
        # Log completion
        return f"Deleted user: {email}"
    except Account.DoesNotExist:
        return f"User not found: {email}"
```

## Facebook App Review

During Facebook App Review, reviewers will:
1. Visit your Data Deletion Callback URL
2. Verify it's publicly accessible
3. Check that it explains the deletion process
4. Confirm timeline is reasonable (usually 30-90 days)
5. Test the deletion request mechanism

## Important URLs

- **Data Deletion Callback**: `/data-deletion-callback/` (Public)
- **Account Deletion**: `/account/delete/` (Login required)
- **Privacy Policy**: `/privacy-policy/` (Public)
- **Terms of Service**: `/terms-of-service/` (Public)

## Facebook Requirements Checklist

- [x] Public URL (no login required)
- [x] Explains what data is collected
- [x] Shows how data is deleted
- [x] Provides deletion timeline
- [x] Offers way to submit requests
- [x] Shows contact information
- [x] Links to Privacy Policy and Terms
- [x] Professional and clear presentation

## Support

If users have questions about data deletion:
- Email: admin@arpansahu.space
- Data Deletion Page: Your domain + `/data-deletion-callback/`
- Account Settings: Your domain + `/account/` (for logged-in users)

## References

- [Facebook Platform Policy - Data Deletion](https://developers.facebook.com/docs/development/create-an-app/app-dashboard/data-deletion-callback)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [GDPR Compliance](https://developers.facebook.com/docs/workplace/reference/graph-api/gdpr)
