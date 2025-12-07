# 🚀 Great Below - Quick Deployment to Render.com

## What You Need Before Starting

- ✅ GitHub account
- ✅ Render.com account (free)
- ✅ This project pushed to GitHub

---

## 5-Minute Quick Start

### Step 1: Generate SECRET_KEY (1 min)

Run this in your project directory:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output - you'll need it.

### Step 2: Create .env File (1 min)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Update `.env` with:
```
DEBUG=False
SECRET_KEY=<paste-the-key-from-step-1>
ALLOWED_HOSTS=your-app-name.onrender.com
```

### Step 3: Push to GitHub (1 min)

```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### Step 4: Deploy on Render (2 mins)

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select your GitHub repository
4. Fill in:
   - **Name**: great-below
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn crochet_shop.wsgi:application`
5. Click "Create Web Service"

### Step 5: Add Database (Optional but Recommended)

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Create database (free tier available)
3. Copy connection string
4. Add to Web Service environment variables as `DATABASE_URL`

### Step 6: Add Environment Variables

In your Web Service settings → Environment:
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-app-name.onrender.com
```

---

## After Deployment ✅

Once the deployment finishes (you'll see "Live" status):

### Create Admin User

1. In Render dashboard, click "Shell"
2. Run:
```bash
python manage.py createsuperuser
```
3. Follow prompts

### Access Your Site

- **Main Site**: https://great-below.onrender.com (or your app name)
- **Admin**: https://great-below.onrender.com/admin

---

## Features Ready to Use 🎉

✅ Product listings and categories
✅ Seller profiles with ratings
✅ Shopping cart
✅ Order checkout with multiple payment methods
✅ Order tracking
✅ User reviews and ratings
✅ Messaging between buyers and sellers
✅ Geolocation on checkout
✅ Seller product management (add, edit, delete)
✅ Customer order history
✅ Cross-role support (buyers can be sellers too!)

---

## Environment Variables Explained

| Variable | What It Is | Example |
|----------|-----------|---------|
| `DEBUG` | Development mode | False (for production) |
| `SECRET_KEY` | Django encryption key | django-insecure-xxxxx |
| `ALLOWED_HOSTS` | Allowed domain names | your-app.onrender.com |
| `DATABASE_URL` | Database connection | postgresql://user:pass@host/db |

---

## Troubleshooting

**Getting a 500 error?**
- Check Render logs (click "Logs" in dashboard)
- Make sure all environment variables are set
- Ensure DATABASE_URL is correct

**Static files not loading?**
- This is handled automatically by WhiteNoise
- If issues persist, run: `python manage.py collectstatic --noinput`

**Need to update code?**
- Just push to GitHub
- Render will automatically redeploy!

---

## File Structure for Deployment

```
Great-Below/
├── .env                    # Your secret config (don't commit!)
├── .env.example            # Example config (commit this)
├── .gitignore              # Files to ignore
├── Procfile                # Render deployment config ✓
├── runtime.txt             # Python version ✓
├── requirements.txt        # Dependencies ✓
├── manage.py
├── setup_deployment.py     # Helper script
├── RENDER_DEPLOYMENT.md    # Detailed guide
├── DEPLOYMENT.md           # General deployment info
└── crochet_shop/
    ├── settings.py         # Django settings (already configured!) ✓
    ├── urls.py
    └── wsgi.py
```

All the hard work is done! ✨

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com/
- **This Project**: Check RENDER_DEPLOYMENT.md for detailed instructions

---

**You're ready to deploy! Let's go! 🚀**
