# 🔗 INTEGRATION GUIDE: Combining Backend + Frontend

## Step 1: Prepare Backend

Extract kizuna-platform.zip and set up:
```bash
cd kizuna-platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Extract Frontend

Extract kizuna-frontend.zip:
```bash
cd kizuna-frontend
```

## Step 3: Merge Files

Copy frontend to backend:
```bash
cp -r templates/* ../kizuna-platform/templates/
cp -r static/* ../kizuna-platform/static/
```

## Step 4: Add Logo

Your logo files (main-3x.jpg, small-3x.jpg) need to be:
1. Converted to PNG format (or keep as JPG)
2. Placed in: kizuna-platform/static/images/kizuna-logo.png

Bash command:
```bash
cp main-3x.jpg ../kizuna-platform/static/images/kizuna-logo.jpg
```

Then update templates if using JPG instead of PNG.

## Step 5: Initialize Database

```bash
cd ../kizuna-platform
python app.py
```

The database will auto-create with tables.

## Step 6: Run Development Server

```bash
flask run
# Visit http://localhost:5000
```

## Directory Structure After Merge

```
kizuna-platform/
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── routes/          ✅ From backend ZIP
├── templates/       ✅ Merged from frontend ZIP
│   ├── base.html
│   ├── home.html
│   ├── auth/
│   ├── clubs/
│   ├── events/
│   └── admin/
├── static/          ✅ Merged from frontend ZIP
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/      ✅ Add your logo here!
└── instance/
    └── kizuna.db
```

## 🎯 Complete Checklist

- [ ] Backend extracted and setup
- [ ] Frontend extracted
- [ ] Templates copied to backend
- [ ] Static files copied to backend
- [ ] Logo placed in static/images/
- [ ] Database initialized
- [ ] Flask dev server running
- [ ] Visit localhost:5000 - see your site!

## ✨ You're Live!

Navigate to http://localhost:5000 and explore:
- Home page with hero
- Browse clubs
- View events
- Register for events
- Login/create account
- Admin dashboard

All fully integrated with your Kizuna branding!

## 🚀 Ready for Deployment?

See DEPLOYMENT.md in the backend package for Render.com setup.

---

**Questions?** Refer to:
- Backend: COMPLETE_SETUP.md in kizuna-platform/
- Frontend: README.md in kizuna-frontend/
- Integration: This file!
