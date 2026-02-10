# OAuth Authentication Setup

This project supports social authentication with Google, GitHub, Facebook, Twitter/X, and LinkedIn.

## Important: HTTPS Requirement

**All OAuth providers require HTTPS connections in production.** Facebook is particularly strict about this requirement. The application now includes automatic HTTPS security configuration that activates when:

- `DEBUG=False` in your environment
- Or `PROTOCOL` starts with `https`

This ensures:
- Session and CSRF cookies are marked as secure
- X-Forwarded-Proto headers are trusted (for reverse proxy setups)
- HSTS (HTTP Strict Transport Security) is enabled
- Secure content type headers are set

## Automatic Domain Configuration

The application automatically configures the OAuth callback URLs based on your environment variables (`DOMAIN` and `PROTOCOL`). You don't need to manually update the Site domain in the database.

## Environment Setup

### Local Development

In your `.env` file, set:
```env
DEBUG=True
DOMAIN=localhost:8016
PROTOCOL=http
```

**Note:** With `DEBUG=True`, HTTPS security settings are relaxed for local development convenience.

### Production

In your `.env` file, set:
```env
DEBUG=False
DOMAIN=yourdomain.com
PROTOCOL=https://
```

**Important:** With `DEBUG=False` and/or `PROTOCOL=https://`, the following security features are automatically enabled:
- SECURE_PROXY_SSL_HEADER - trusts X-Forwarded-Proto from reverse proxy
- SESSION_COOKIE_SECURE & CSRF_COOKIE_SECURE - cookies only sent over HTTPS  
- HSTS (HTTP Strict Transport Security) headers
- Additional security headers for XSS and content type protection

## Provider Configuration

For each OAuth provider you want to use, you need to:

1. **Create an OAuth application** in the provider's developer console
2. **Add the callback URLs** to your OAuth app settings
3. **Add the credentials** to your `.env` file

### View Your Callback URLs

Run this command to see all callback URLs for your current environment:

```bash
python show_oauth_urls.py
```

Or start the Django server and the URLs will be displayed automatically.

### Required Callback URLs by Provider

The callback URLs follow this pattern: `{PROTOCOL}://{DOMAIN}/accounts/{provider}/login/callback/`

**For local development (localhost:8016):**
- Google: `http://localhost:8016/accounts/google/login/callback/`
- GitHub: `http://localhost:8016/accounts/github/login/callback/`
- Facebook: `http://localhost:8016/accounts/facebook/login/callback/`
- Twitter: `http://localhost:8016/accounts/twitter/login/callback/`
- LinkedIn: `http://localhost:8016/accounts/linkedin_oauth2/login/callback/`

**Also add the 127.0.0.1 variant for local development:**
- `http://127.0.0.1:8016/accounts/{provider}/login/callback/`

**For production:**
- `https://yourdomain.com/accounts/{provider}/login/callback/`

## Step-by-Step Provider Setup

### 1. Google OAuth

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Add to **Authorized JavaScript origins**:
   - Local: `http://localhost:8016` and `http://127.0.0.1:8016`
   - Prod: `https://yourdomain.com`
6. Add to **Authorized redirect URIs**: (callback URLs from above)
7. Copy Client ID and Client Secret to `.env`:
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### 2. GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Set **Homepage URL**: `http://localhost:8016` (or your production URL)
4. Set **Authorization callback URL**: `http://localhost:8016/accounts/github/login/callback/`
5. Copy Client ID and Client Secret to `.env`:
   ```env
   GITHUB_CLIENT_ID=your-client-id
   GITHUB_CLIENT_SECRET=your-client-secret
   ```

### 3. Facebook OAuth

1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Create a new app
3. Add **Facebook Login** product
4. In **Facebook Login Settings**, add **Valid OAuth Redirect URIs**
5. **Important:** Add **Data Deletion Callback URL** (required by Facebook):
   - Local: `http://localhost:8016/data-deletion-callback/`
   - Prod: `https://yourdomain.com/data-deletion-callback/`
   - This URL must be publicly accessible (no login required)
   - See [Facebook Data Deletion Setup](FACEBOOK_DATA_DELETION.md) for details
6. Copy App ID and App Secret to `.env`:
   ```env
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   ```

**Note:** Facebook requires all apps to provide a Data Deletion Callback URL. This page explains how user data is deleted when they remove your app from their Facebook account. For detailed setup instructions and compliance requirements, see [FACEBOOK_DATA_DELETION.md](FACEBOOK_DATA_DELETION.md).

### 4. Twitter/X OAuth

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app
3. In **Authentication settings**, add callback URL
4. Copy API Key and API Secret to `.env`:
   ```env
   TWITTER_API_KEY=your-api-key
   TWITTER_API_SECRET=your-api-secret
   ```

### 5. LinkedIn OAuth

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Create a new app
3. In **Auth** tab, add **Authorized redirect URLs**
4. Copy Client ID and Client Secret to `.env`:
   ```env
   LINKEDIN_CLIENT_ID=your-client-id
   LINKEDIN_CLIENT_SECRET=your-client-secret
   ```

## Testing

1. Start your Django server
2. Go to the login page
3. Click on any social login button
4. You should be redirected to the provider's login page
5. After authentication, you'll be redirected back to your application

## Troubleshooting

### Error 400: redirect_uri_mismatch

This means the callback URL in your OAuth app settings doesn't match what Django is sending. 

**Solution:**
1. Run `python show_oauth_urls.py` to see your current callback URLs
2. Add these exact URLs to your OAuth provider's allowed callback URLs
3. Make sure you added both `localhost` and `127.0.0.1` variants for local development
4. Restart your Django server

### Facebook: "Isn't using a secure connection"

**Error message:** "Facebook has detected that [App Name] isn't using a secure connection to transfer information."

**Cause:** Facebook requires HTTPS for OAuth in production. This error appears when:
- Your `PROTOCOL` is set to `http` instead of `https://`
- `DEBUG=True` in production (disables security features)
- Missing HTTPS security headers
- Reverse proxy not forwarding HTTPS correctly

**Solution:**

1. **Check your `.env` file** (production):
   ```env
   DEBUG=False
   PROTOCOL=https://
   DOMAIN=yourdomain.com
   ```

2. **Verify Facebook App Settings:**
   - Go to Facebook Developer Console → Settings → Basic
   - **App Domains:** Add your domain (e.g., `yourdomain.com`)
   - **Valid OAuth Redirect URIs:** Must use `https://` 
     ```
     https://yourdomain.com/accounts/facebook/login/callback/
     ```

3. **Ensure your reverse proxy (nginx/load balancer) forwards HTTPS:**
   ```nginx
   proxy_set_header X-Forwarded-Proto $scheme;
   proxy_set_header X-Forwarded-Host $host;
   ```

4. **Restart Django** to apply security settings

5. **Test locally with ngrok** (optional):
   - `ngrok http 8016`
   - Update `.env`: `DOMAIN=your-ngrok-url.ngrok.io` and `PROTOCOL=https://`
   - Add ngrok URL to Facebook app settings

### Site domain not updating automatically

If the Site domain doesn't update automatically:
1. Check that `DOMAIN` and `PROTOCOL` are set in your `.env` file
2. Restart the Django server
3. Or manually update via Django shell:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'localhost:8016'  # or your domain
   site.save()
   ```

## Switching Between Environments

When switching between local and production:

1. Update `DOMAIN` and `PROTOCOL` in `.env`
2. Restart the Django server
3. The Site domain will automatically update
4. Make sure you've added the callback URLs for both environments in each OAuth provider console
