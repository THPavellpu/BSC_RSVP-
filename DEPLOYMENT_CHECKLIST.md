# Render Deployment Checklist - LPU BSC RSVP

## Pre-Deployment (Local Setup) ✅

- [x] Code is in GitHub repository
- [x] All changes committed (`git status` shows clean)
- [x] `requirements.txt` has all dependencies
- [x] Django settings configured for Render
- [x] Secret key is NOT the default hardcoded one
- [x] DEBUG = False in settings
- [x] ALLOWED_HOSTS includes Render domain
- [x] Cloudinary packages installed and configured
- [x] PostgreSQL driver (psycopg2-binary) in requirements

## Render Setup (Dashboard) ✅

### PostgreSQL Database Service

- [ ] Create PostgreSQL service on Render
  - Name: `lpu-bsc-db`
  - Region: Same as web service
- [ ] Copy **Internal Database URL**
- [ ] Render auto-sets `DATABASE_URL` env variable
- [ ] Database ready to use

### Web Service Configuration

- [ ] Create Web Service from GitHub repo
  - Name: `bsc-rsvp`
  - Region: Select appropriate region
  - Runtime: Python
  - Build Command: (from RENDER_DEPLOYMENT.md or render.yaml)
  - Start Command: (from RENDER_DEPLOYMENT.md or render.yaml)

- [ ] Set Environment Variables (Settings → Environment):

```
SECRET_KEY = [Generate random key - must change from hardcoded default]
DEBUG = False
DATABASE_URL = [Auto-set from PostgreSQL service]
CLOUDINARY_CLOUD_NAME = [Your Cloudinary cloud name]
CLOUDINARY_API_KEY = [Your Cloudinary API key]
CLOUDINARY_API_SECRET = [Your Cloudinary API secret]
EMAIL_HOST = smtp.gmail.com (optional)
EMAIL_PORT = 587 (optional)
EMAIL_HOST_USER = [your-email@gmail.com] (optional)
EMAIL_HOST_PASSWORD = [app-specific password] (optional)
DEFAULT_FROM_EMAIL = noreply@lpubsc.com (optional)
```

- [ ] Connect PostgreSQL database to Web Service
  - If separate service: Link in Environment
  - DATABASE_URL should auto-appear

- [ ] Set Health Check Path: `/` (default)

## Deployment 🚀

- [ ] Push latest code to GitHub main branch

  ```bash
  git add .
  git commit -m "Deploy to Render with PostgreSQL & Cloudinary"
  git push origin main
  ```

- [ ] Render auto-starts build and deploy
  - Watch progress in Render Dashboard
  - View logs for any errors

- [ ] Wait for build to complete
  - Green checkmark = Success
  - Red X = Check logs for errors

## Post-Deployment Verification ✅

### 1. Basic Health Check
- [ ] Website loads: `https://bsc-rsvp.onrender.com/`
- [ ] Homepage displays correctly
- [ ] No 500 or 502 errors

### 2. Admin Interface
- [ ] Admin loads: `https://bsc-rsvp.onrender.com/admin/`
- [ ] Can login with superuser credentials
- [ ] Ticket list shows in admin

### 3. Database & Storage
- [ ] Check existing data appears (users, events, tickets)
- [ ] Cloudinary status shows in admin (QR ✓, PDF ✓)
- [ ] File uploads work

### 4. Ticket System
- [ ] View existing ticket: Check QR code displays
- [ ] Download PDF: Should work without 404
- [ ] Create new RSVP: Ticket auto-generates

### 5. Logs Check
- [ ] Go to Render Dashboard → Web Service → Logs
- [ ] Check for errors
- [ ] Look for ticket generation logs (should see ✓)

## Troubleshooting 🔍

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Build fails | Missing package | Add to requirements.txt, push update |
| 500 error | Env variable missing | Check all 6 required vars are set |
| DB error | DATABASE_URL missing | Verify PostgreSQL service linked |
| Static files 404 | collectstatic failed | Check build logs |
| QR/PDF 404 | Cloudinary vars missing | Set CLOUDINARY_* env vars |
| Login doesn't work | Secret key issue | Regenerate and redeploy |

## Commands on Render (via Shell)

If needed, you can run commands via Render Shell:

```bash
# Create admin user
python manage.py createsuperuser

# Regenerate all tickets
python manage.py regenerate_tickets

# Run Django shell
python manage.py shell

# Check database
python manage.py dbshell
```

## Environment Variables Checklist

**REQUIRED (must have):**
- [ ] SECRET_KEY = Generated random key (not default)
- [ ] DEBUG = False
- [ ] DATABASE_URL = Set by PostgreSQL service
- [ ] CLOUDINARY_CLOUD_NAME = From Cloudinary dashboard
- [ ] CLOUDINARY_API_KEY = From Cloudinary dashboard
- [ ] CLOUDINARY_API_SECRET = From Cloudinary dashboard

**OPTIONAL (for email):**
- [ ] EMAIL_HOST = smtp.gmail.com
- [ ] EMAIL_PORT = 587
- [ ] EMAIL_HOST_USER = your-email@gmail.com
- [ ] EMAIL_HOST_PASSWORD = Google App Password
- [ ] DEFAULT_FROM_EMAIL = noreply@lpubsc.com

## Security Verification

- [ ] No secrets in code or git history
- [ ] All sensitive data in environment variables
- [ ] HTTPS enabled (Render default - https://)
- [ ] SECRET_KEY is strong and random
- [ ] DEBUG is False
- [ ] ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS configured

## Monitoring (Post-Deploy)

- [ ] Check Render dashboard daily for errors
- [ ] Monitor logs in Render dashboard
- [ ] Test periodic RSVP creation
- [ ] Verify email notifications (if enabled)
- [ ] Backup database periodically (Render feature)

## Go Live! 🎉

Once all items checked:
- App is live at `https://bsc-rsvp.onrender.com/`
- PostgreSQL database connected
- Cloudinary storing media files
- Tickets working with QR & PDF
- Ready for users!

---

## Quick Links

- **Render Dashboard**: https://dashboard.render.com/
- **Cloudinary Console**: https://cloudinary.com/console
- **Your App**: https://bsc-rsvp.onrender.com/
- **Admin Panel**: https://bsc-rsvp.onrender.com/admin/
- **Docs**: See RENDER_DEPLOYMENT.md

---

## Emergency Contacts / Useful Resources

- **Render Support**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Cloudinary Docs**: https://cloudinary.com/documentation
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

Created: March 2026 | Updated: As needed
