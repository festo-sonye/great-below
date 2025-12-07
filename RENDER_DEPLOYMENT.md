# Great Below - Render.com Deployment Guide

## Step 1: Create a .env file

Copy `.env.example` to `.env` and update with your values:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-generate-a-strong-one
ALLOWED_HOSTS=your-app-name.onrender.com,localhost

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# M-PESA (Add when you have active credentials)
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
```

## Step 2: Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Great Below e-commerce platform"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/great-below.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render.com

### 3a. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### 3b. Create Web Service
1. Click "New +" → "Web Service"
2. Select your `great-below` repository
3. Fill in the details:
   - **Name**: great-below (or your preferred name)
   - **Environment**: Python 3
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn crochet_shop.wsgi:application`

### 3c. Add Environment Variables
In the Render dashboard, go to "Environment" and add:

```
DEBUG=False
SECRET_KEY=<generate-a-strong-secret-key>
ALLOWED_HOSTS=<your-render-url>.onrender.com
DATABASE_URL=<your-postgresql-url>
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
```

### 3d. Add PostgreSQL Database
1. In Render, create a new PostgreSQL database
2. Copy the connection string (DATABASE_URL)
3. Add it to your environment variables

### 3e. Deploy
Click "Deploy" and watch the logs. Your app should be live in 2-5 minutes!

## Step 4: After Deployment

### Create Superuser
Once deployed, you need to create an admin user:

1. In Render dashboard, go to your service
2. Click "Shell" tab
3. Run:
```bash
python manage.py createsuperuser
```

4. Follow prompts to create admin account

### Access Your App
- **Main Site**: https://your-app-name.onrender.com
- **Admin Panel**: https://your-app-name.onrender.com/admin

## Step 5: Configure Media Files (Optional)

For better media handling, you can:
1. Use AWS S3 for storing product images
2. Or use Render's built-in volume storage

Ask if you need help with S3 setup!

## Troubleshooting

### 500 Error
- Check logs in Render dashboard
- Ensure DATABASE_URL is correct
- Check SECRET_KEY is set

### Static files not loading
- Run `python manage.py collectstatic --noinput`
- Ensure STATIC_URL is correct

### Database connection error
- Verify DATABASE_URL format
- Check PostgreSQL instance is running
- Ensure IP whitelist includes Render servers

## Environment Variables Reference

| Variable | Required | Example |
|----------|----------|---------|
| DEBUG | Yes | False |
| SECRET_KEY | Yes | django-insecure-xxxxx |
| ALLOWED_HOSTS | Yes | your-app.onrender.com |
| DATABASE_URL | Yes | postgresql://user:pass@host:5432/db |
| EMAIL_HOST_USER | No | your-email@gmail.com |
| EMAIL_HOST_PASSWORD | No | app-specific-password |

## Important Notes

⚠️ **Never commit `.env` file to GitHub!**
- It's in `.gitignore` by default
- Only commit `.env.example`

✅ **Use strong SECRET_KEY**
- Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

✅ **Enable SSL/HTTPS**
- Render does this automatically

## Getting Help

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
- Contact Render support for issues

---

**Happy Deploying! 🚀**
