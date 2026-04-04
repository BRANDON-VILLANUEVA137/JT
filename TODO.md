# Cloudinary Fix - Checklist
- [x] **Edit settings.py** (agregar 'cloudinary' app + STATICFILES_STORAGE) ✅
- [ ] `git add . && git commit -m "Fix cloudinary config" && git push`
- [ ] Render Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- [ ] **Re-upload images:** `python manage.py shell` + script
- [ ] Test homepage imágenes
- [ ] Update .gitignore permanent
