# HTTPS Security Configuration

## Overview

This application now includes automatic HTTPS security configuration that activates for production environments. This is **required** for OAuth providers like Facebook, Google, and others that mandate secure connections.

## When Security Settings Activate

HTTPS security features are automatically enabled when **either** of these conditions is met:

1. `DEBUG=False` in your `.env` file
2. `PROTOCOL` starts with `https` 

## Security Features Enabled

When activated, the following Django security settings are configured:

### Core HTTPS Settings

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

- **SECURE_PROXY_SSL_HEADER**: Tells Django to trust the `X-Forwarded-Proto` header from your reverse proxy (nginx, load balancer, etc.)
- **SESSION_COOKIE_SECURE**: Ensures session cookies are only sent over HTTPS connections
- **CSRF_COOKIE_SECURE**: Ensures CSRF tokens are only sent over HTTPS connections

### HSTS (HTTP Strict Transport Security)

```python
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

- **HSTS**: Tells browsers to only access your site via HTTPS for the specified duration
- **Include Subdomains**: Applies HSTS to all subdomains
- **Preload**: Allows your site to be included in browsers' HSTS preload lists

### Additional Security Headers

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

- **Content Type NoSniff**: Prevents browsers from MIME-sniffing responses
- **XSS Filter**: Enables browser's XSS filtering
- **X-Frame-Options**: Prevents clickjacking by restricting iframe embedding

## Environment Configuration

### Production Environment

```env
# .env file for production
DEBUG=False
PROTOCOL=https://
DOMAIN=yourdomain.com
```

With these settings:
- ✅ All security features are ENABLED
- ✅ OAuth providers (Facebook, Google, etc.) will work correctly
- ✅ Cookies are secure
- ✅ HSTS headers are sent

### Local Development

```env
# .env file for local development
DEBUG=True
PROTOCOL=http
DOMAIN=localhost:8016
```

With these settings:
- ❌ Security features are DISABLED (for development convenience)
- ⚠️ OAuth may not work with some providers (Facebook requires HTTPS)
- ✓ You can test without SSL certificates

## Reverse Proxy Configuration

For production deployments behind nginx or a load balancer, ensure your proxy forwards the HTTPS protocol information:

### Nginx Configuration Example

```nginx
location / {
    proxy_pass http://django_app;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;  # ← Important for HTTPS detection
    proxy_set_header X-Forwarded-Host $host;
}
```

### Testing HTTPS Locally with ngrok

If you need to test OAuth with HTTPS locally:

```bash
# Start ngrok
ngrok http 8016

# Update .env
DOMAIN=your-random-id.ngrok.io
PROTOCOL=https://
DEBUG=False  # or True, security will still activate due to PROTOCOL=https

# Restart Django
python manage.py runserver 8016
```

Add the ngrok URL to your OAuth provider's allowed callback URLs:
```
https://your-random-id.ngrok.io/accounts/facebook/login/callback/
```

## Verifying Security Configuration

### Check if Security is Active

1. Start your Django server
2. Look for the Site domain output showing your configuration
3. Check if `DEBUG=False` or `PROTOCOL=https://`

### Test HTTPS Headers

Visit your production site and check response headers (using browser dev tools):

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
```

### Test OAuth Callback

1. Try logging in with Facebook (or any OAuth provider)
2. If successful, security is properly configured
3. If you see "Not using secure connection" error, check:
   - Is `DEBUG=False`?
   - Is `PROTOCOL=https://`?
   - Is your reverse proxy forwarding `X-Forwarded-Proto`?
   - Are you actually accessing via HTTPS?

## Common Issues

### "Mixed Content" Warnings

If you see mixed content warnings after enabling HTTPS:
- Check that all static files URLs use HTTPS
- Verify `AWS_S3_USE_SSL = True` (if using S3)
- Check that external resources (CDNs, APIs) use HTTPS

### OAuth Still Failing After Configuration

1. **Clear browser cache and cookies**
2. **Restart Django server** to apply new settings
3. **Verify environment variables** are loaded:
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> settings.DEBUG
   False
   >>> settings.SECURE_PROXY_SSL_HEADER
   ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

### Local Development Can't Test OAuth

Use one of these approaches:
1. **ngrok** (recommended for testing)
2. **Create separate OAuth apps** for local development (some providers allow `http://localhost`)
3. **Use production OAuth apps** only for production testing

## Security Best Practices

1. **Always use `DEBUG=False` in production**
2. **Always use `PROTOCOL=https://` in production**
3. **Never commit `.env` files** to version control
4. **Rotate secrets regularly** (SECRET_KEY, OAuth secrets)
5. **Keep dependencies updated** to patch security vulnerabilities
6. **Use environment-specific OAuth credentials** (separate apps for dev/prod)
7. **Monitor security headers** using tools like [Security Headers](https://securityheaders.com/)

## References

- [Django Security Settings](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)
- [HSTS Preload List](https://hstspreload.org/)
- [Facebook OAuth Documentation](https://developers.facebook.com/docs/facebook-login/web)
