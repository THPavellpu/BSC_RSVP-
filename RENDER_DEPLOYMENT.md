# Render Deployment Guide - LPU BSC RSVP System

## ✅ Environment Variables to Set in Render Dashboard

Go to **Settings** → **Environment** in your Render service and add all these variables:

### Database (PostgreSQL)
```
DATABASE_URL = postgresql://username:password@host:port/database
```
*(Render auto-provides this when you create a PostgreSQL service)*

### Cloudinary Media Storage
```
CLOUDINARY_CLOUD_NAME = your_cloud_name
CLOUDINARY_API_KEY = your_api_key
CLOUDINARY_API_SECRET = your_api_secret
```

### Django Security
```
SECRET_KEY = generate-a-random-secret-key-here
DEBUG = False
```

### Email (Optional - for notifications)
```
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = your-app-password
DEFAULT_FROM_EMAIL = noreply@lpubsc.com
```

---

## 📋 Step-by-Step Deployment Checklist

### 1. Create PostgreSQL Database on Render
- [ ] Go to Render Dashboard
- [ ] Click "New +" → "PostgreSQL"
- [ ] Name: `lpu-bsc-db`
- [ ] Create and copy the **Internal Database URL**
- [ ] Note: Render automatically sets `DATABASE_URL` env variable

### 2. Create Web Service on Render
- [ ] Click "New +" → "Web Service"
- [ ] Connect your GitHub repository
- [ ] Select branch (main/master)
- [ ] Name: `bsc-rsvp`
- [ ] Runtime: Python
- [ ] Build Command: (see "Build & Start Commands" below)
- [ ] Start Command: (see "Build & Start Commands" below)

### 3. Add Environment Variables
- [ ] In Web Service settings, go to "Environment"
- [ ] Add all variables from the list above
- [ ] Save

### 4. Connect PostgreSQL to Web Service
- [ ] In Web Service, go to "Environment"
- [ ] DATABASE_URL should be auto-set from PostgreSQL service
- [ ] Verify in the list

### 5. Deploy
- [ ] Push your code to GitHub
- [ ] Render auto-deploys on every push
- [ ] Monitor logs in Render Dashboard

---

## 🔧 Build & Start Commands

### Build Command
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### Start Command
```bash
gunicorn lpu_bsc.wsgi:application
```

Gunicorn is already in your `requirements.txt` ✓

---

## 📁 Required Files

### 1. `render.yaml` - Build Configuration (Optional but Recommended)

Create this file in your project root:

```yaml
# render.yaml
services:
  - type: web
    name: bsc-rsvp
    env: python
    plan: free  # or standard/pro
    buildCommand: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
    startCommand: gunicorn lpu_bsc.wsgi:application
    envVars:
      - key: SECRET_KEY
        scope: build,connect
      - key: DEBUG
        value: "False"
      - key: DATABASE_URL
        scope: build
      - key: CLOUDINARY_CLOUD_NAME
        scope: build,connect
      - key: CLOUDINARY_API_KEY
        scope: build,connect
      - key: CLOUDINARY_API_SECRET
        scope: build,connect
```

### 2. `.gitignore` - Make sure to exclude

```
*.pyc
__pycache__/
*.sqlite3
.env
.DS_Store
/venv/
/media/
/staticfiles/
*.log
```

### 3. `Procfile` (Alternative, if not using render.yaml)

Create in project root:

```
web: gunicorn lpu_bsc.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
```

---

## 🚀 Deployment Process

### First Deployment
1. Push code to GitHub (with updated settings.py)
2. Go to Render Dashboard
3. Create new Web Service from GitHub repo
4. Set environment variables
5. Deploy
6. Watch logs for any errors

### After First Deployment Run
```bash
# SSH into Render container (if needed)
# Or use Render Shell to run commands

# Regenerate tickets (if you have existing tickets)
python manage.py regenerate_tickets

# Check admin
# Visit https://bsc-rsvp.onrender.com/admin/
```

---

## ✅ Post-Deployment Verification

### 1. Check Health
```
https://bsc-rsvp.onrender.com/ → Should load homepage
```

### 2. Check Admin
```
https://bsc-rsvp.onrender.com/admin/ → Should load with login
```

### 3. Check Ticket System
```
# If you have existing tickets, they should now display correctly
# QR codes and PDFs should work via Cloudinary
```

### 4. Check Logs
- Go to Render Dashboard
- Select your web service
- View "Logs" to see errors/info

---

## 🔍 Debugging on Render

### View Real-time Logs
```
Render Dashboard → Web Service → Logs (Real-time tab)
```

### Check Environment Variables
```
Render Dashboard → Settings → Environment
```

### Test Database Connection
From Render Shell (if available):
```bash
python manage.py dbshell
```

### Run Management Commands
From Render Shell:
```bash
python manage.py regenerate_tickets
python manage.py createsuperuser
python manage.py shell
```

---

## 📊 Render Service Limits (Free Plan)

- Deployed but inactive after 15 minutes → takes time to spin up again
- Upgrade to "Standard" for always-on

---

## ⚠️ Important Notes Before Deploying

### 1. Database Migrations
- ✅ Always run migrations in build command
- ✅ `manage.py migrate` is in build command

### 2. Static Files
- ✅ Must run `collectstatic` before serving
- ✅ Uses WhiteNoise (already in settings)

### 3. Cloudinary Setup
- ✅ Must set 3 environment variables
- ✅ Files will upload automatically to Cloudinary

### 4. Secret Key
- ⚠️ **Must change SECRET_KEY in Render**
- Generate a strong key:
  ```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())
  ```

### 5. DEBUG = False
- ✅ Already set in settings
- HTTPS enforced in production

### 6. ALLOWED_HOSTS
- ✅ Updated to include `*.onrender.com`
- Adjust domain if you use custom domain

---

## 🔒 Security Checklist

- [ ] SECRET_KEY changed (not the hardcoded default)
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS includes your domain
- [ ] CSRF_TRUSTED_ORIGINS set
- [ ] SSL/HTTPS enabled (Render default)
- [ ] Database credentials secure (Render handles this)
- [ ] Cloudinary API keys in env variables (not in code)

---

## 💡 Quick Render Commands

```bash
# View logs
curl https://api.render.com/v1/services/{service-id}/logs

# Deploy from CLI (if configured)
render deploy --service=bsc-rsvp

# Check status
render ps
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Deploy fails - "package not found"** | Check `requirements.txt` has all packages. Run `pip freeze > requirements.txt` locally |
| **500 error on page** | Check Render logs. Usually migration or environment variable missing |
| **Database connection error** | Verify `DATABASE_URL` is set. Check PostgreSQL service is running |
| **QR/PDF not showing** | Check Cloudinary env vars are set. Run `python manage.py regenerate_tickets` |
| **Static files not loading** | Check `python manage.py collectstatic` runs. WhiteNoise is configured |
| **"Bad Request" 400 error** | Check ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS include your domain |

---

## 📝 Environment Variables Summary

```
# Copy this template to Render Settings → Environment

# Production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database (Auto-provided by Render PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key  
CLOUDINARY_API_SECRET=your_api_secret

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
DEFAULT_FROM_EMAIL=noreply@lpubsc.com
```

---

## 🎯 Final Deployment Command Flow

1. **Local Development**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Render Auto-Deploys**
   - Runs build command (migrations, collectstatic)
   - Starts web service with Gunicorn
   - Your app is live!

3. **Verify**
   - Check `https://bsc-rsvp.onrender.com/`
   - Check admin at `/admin/`
   - Check logs if issues

That's it! Your RSVP system is now deployed! 🚀
