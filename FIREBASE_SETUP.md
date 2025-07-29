# 🚀 Firebase Setup Guide for WanderWhiz

## Quick Firebase Setup for Hackathon

### Step 1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Name it "wanderwhiz-hackathon" (or similar)
4. Disable Analytics for faster setup
5. Click "Create project"

### Step 2: Enable Firestore Database
1. In your Firebase console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for hackathon - allows read/write)
4. Select a location closest to you
5. Click "Done"

### Step 3: Generate Service Account Key
1. Go to Project Settings (gear icon) > Service accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase-key.json`
5. Place it in your project root (same folder as app.py)

### Step 4: Update Requirements
Your requirements.txt already includes:
```
firebase-admin>=6.0.0
```

### Step 5: Environment Variables (Optional)
For production, set:
```bash
export FIREBASE_KEY_PATH=/path/to/firebase-key.json
```

## 🎯 Hackathon Features Enabled

✅ **Cloud Storage**: All itineraries saved to Firestore
✅ **Demo Trips**: Pre-loaded impressive examples  
✅ **Platform Stats**: Real-time usage statistics
✅ **User Analytics**: Trip history and preferences
✅ **Scalability**: Ready for thousands of users

## 🔥 Demo Data Included

- **Paris Adventure**: 8 locations, €180 budget
- **Tokyo Explorer**: 10 locations, ¥25,000 budget  
- **NYC Highlights**: 12 locations, $220 budget

## 🎨 Enhanced UI Features

- **Statistics Dashboard**: Live platform metrics
- **Demo Trip Cards**: Interactive examples
- **Loading Animations**: Professional feel
- **Responsive Design**: Works on all devices

## ⚡ Local Development

If Firebase isn't set up yet, the app gracefully falls back to:
- Local storage for itineraries
- Demo statistics  
- Sample trips

Perfect for hackathon demos! 🏆

## 🚨 Security Note

For hackathons, test mode is fine. For production:
1. Set proper Firestore security rules
2. Enable authentication
3. Use environment variables for keys
