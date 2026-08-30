# PICME Login System Guide

## 🔐 Separate Login Pages

PICME now has **two distinct login pages** for better user experience:

---

## 👤 **USER LOGIN**

### Purpose
For regular users who want to find their photos from events.

### Access URL
```
http://localhost:5000/auth/user-login
```

### Features
- **Blue/Primary themed** interface
- User-friendly login form
- Link to registration page
- Quick access to admin login (if needed)
- Information about user capabilities

### What Users Can Do
✅ Browse event photos  
✅ Use AI face matching  
✅ Find photos instantly  
✅ Download matched photos  

### Visual Design
- **Color**: Primary Blue
- **Icon**: `fa-user` (user icon)
- **Card Border**: Blue

---

## 🛡️ **ADMIN / CREATOR LOGIN**

### Purpose
For event organizers and administrators who manage events and photos.

### Access URL
```
http://localhost:5000/auth/admin-login
```

### Features
- **Red/Danger themed** interface
- Admin-specific login form
- Security-focused messaging
- Link to user login (if logged in by mistake)
- Information about admin capabilities

### What Admins Can Do
✅ Create and manage events  
✅ Upload and process photos  
✅ View analytics and metrics  
✅ Generate QR codes  

### Visual Design
- **Color**: Danger Red
- **Icon**: `fa-user-shield` (admin shield icon)
- **Card Border**: Red

### Security
- ✅ Admin credentials verified
- ✅ Non-admin users denied access
- ✅ Clear error messages
- ✅ Separate authentication flow

---

## 📱 **Navigation Menu**

### Dropdown Login Menu
When not logged in, users see a dropdown with:

```
Login ▼
  ├─ 🛡️ Admin / Creator Login (Red)
  └─ 👤 User Login (Blue)
```

### Homepage Buttons
```
┌──────────────────────┐
│ 🔍 Find My Photos    │ (Green - Primary action)
└──────────────────────┘

┌─────────────┬─────────────┐
│ 🛡️ Admin   │ 👤 User     │
│   Login    │   Login     │
└─────────────┴─────────────┘
```

---

## 🔄 **Login Flow**

### For Regular Users:
```
Homepage → "User Login" → Enter credentials → Events Page
```

### For Admins:
```
Homepage → "Admin Login" → Enter admin credentials → Admin Dashboard
```

### Auto-redirect:
- Users logged in as admin → redirected to Admin Dashboard
- Users logged in as regular user → redirected to Events Page
- Generic `/auth/login` → redirects to User Login

---

## 🎨 **Visual Differences**

| Feature | User Login | Admin Login |
|---------|------------|-------------|
| **Theme Color** | Blue (Primary) | Red (Danger) |
| **Icon** | 👤 User | 🛡️ Shield |
| **Border** | Blue | Red |
| **Button** | Primary Blue | Danger Red |
| **Heading** | "User Login" | "Admin / Creator Login" |

---

## 🧪 **Testing the Login System**

### Test Admin Login:
1. Go to http://localhost:5000
2. Click "Admin Login" button
3. Use credentials:
   - Username: `admin`
   - Password: `admin123`
4. Should redirect to Admin Dashboard

### Test User Login:
1. Go to http://localhost:5000
2. Click "User Login" button
3. Register a new user first (if needed)
4. Login with user credentials
5. Should redirect to Events Page

### Test Security:
1. Try logging into Admin Login with user credentials
2. Should see: "Access denied. Admin credentials required."
3. Regular users cannot access admin panel

---

## 📝 **Registration Page**

The registration page now shows **both login options**:

```
Already have an account?

[👤 User Login]  [🛡️ Admin Login]
```

This makes it easy for new users to find the correct login page after registration.

---

## 🔧 **Technical Details**

### Route Structure:
```python
/auth/login          → Redirects to user login
/auth/user-login     → User login page
/auth/admin-login    → Admin login page (with role verification)
/auth/register       → Registration (creates regular users)
/auth/logout         → Logout for both types
```

### Templates:
```
app/templates/auth/
  ├── user_login.html     → Blue themed user login
  ├── admin_login.html    → Red themed admin login
  └── register.html       → Registration form
```

### Security Features:
1. **Role Verification** - Admin login checks `user.is_admin`
2. **Access Control** - Non-admins denied admin access
3. **Clear Messaging** - Different error messages for clarity
4. **Auto-redirect** - Logged-in users redirected appropriately

---

## 🎯 **Benefits of Separate Logins**

### User Experience:
✅ Clear distinction between user types  
✅ Prevents confusion about credentials  
✅ Professional appearance  
✅ Easier onboarding  

### Security:
✅ Role-based access control  
✅ Separate authentication flows  
✅ Clear permission boundaries  
✅ Better audit trail  

### Design:
✅ Visual differentiation (colors/icons)  
✅ Consistent branding  
✅ Intuitive navigation  
✅ Mobile-friendly  

---

## 🚀 **Quick Reference**

### Default Admin Credentials:
```
URL: http://localhost:5000/auth/admin-login
Username: admin
Password: admin123
```

### Create New User:
```
URL: http://localhost:5000/auth/register
(Then login via User Login)
```

### Access from Homepage:
```
Homepage → Two login buttons visible
         → Dropdown menu in navigation
         → Links in registration page
```

---

## 💡 **Tips**

1. **For Event Organizers:** Use Admin Login
2. **For Event Attendees:** Use User Login
3. **First Time Users:** Register, then use User Login
4. **Admin Setup:** Change default admin password after first login
5. **Testing:** Try both login pages to see the difference

---

## 🔗 **Related Pages**

- `README.md` - Project documentation
- `QUICKSTART.md` - Quick start guide
- `USAGE.md` - Detailed usage instructions
- `INSTALLATION.md` - Setup instructions

---

**✨ Your login system is now ready with separate admin and user portals!**
