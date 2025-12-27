# Firebase Authentication Setup for GYMMANDO

This guide explains how Firebase authentication is integrated into the GYMMANDO system to make everything user-specific.

## Overview

The system now uses Firebase Authentication to:
1. Verify user identity in the API
2. Pass user_id to the LiveKit agent
3. Filter all database queries by user_id
4. Make workouts and data user-specific

## Architecture

```
UI App (Firebase Auth) 
    ↓ (sends Firebase ID token)
API Service (verifies token, extracts user_id)
    ↓ (generates LiveKit token with user_id as identity)
LiveKit Agent (extracts user_id from participant)
    ↓ (uses user_id for all database queries)
Supabase Database (filters by user_id)
```

## Setup Steps

### 1. Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download the JSON file

### 2. Configure API Service

**For Local Development:**
- Save the Firebase service account JSON file
- Set environment variable:
  ```bash
  export FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json
  ```

**For GCP Deployment:**
- Upload the service account JSON to GCP Secret Manager
- Or use the default credentials if running on GCP (the API will auto-detect)

### 3. Update Database Schema

Run the updated SQL script to add `user_id` column:

```sql
-- Add user_id column if it doesn't exist
ALTER TABLE public.workouts 
ADD COLUMN IF NOT EXISTS user_id text;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON public.workouts(user_id);

-- Make user_id required (after migrating existing data)
-- ALTER TABLE public.workouts ALTER COLUMN user_id SET NOT NULL;
```

### 4. Update UI (Already Done)

The UI has been updated to:
- Get Firebase ID token from authenticated user
- Send it in `Authorization: Bearer <token>` header when requesting LiveKit token

## How It Works

### 1. User Authentication (UI)
- User signs in via Firebase Auth (email/password or Google)
- UI stores the authenticated user session

### 2. Token Request (UI → API)
```swift
let firebaseToken = try await user.getIDToken()
request.setValue("Bearer \(firebaseToken)", forHTTPHeaderField: "Authorization")
```

### 3. Token Verification (API)
```python
decoded_token = auth.verify_id_token(id_token)
user_id = decoded_token.get("uid")  # Firebase UID
```

### 4. LiveKit Token Generation (API)
```python
token.with_identity(user_id)  # Sets participant.identity = Firebase UID
```

### 5. Agent Extraction (Agent)
```python
user_id = participant.identity  # Gets Firebase UID from LiveKit participant
```

### 6. Database Queries (Agent)
```python
response = supabase.table("workouts").select("*").eq("user_id", self.user_id).execute()
```

## Testing

### Test with Console Mode

```bash
cd repos/gymmando-api/agent
python main.py console
```

Note: Console mode will use "default_user" since there's no Firebase token. For full testing, use the UI app.

### Test API Endpoint

```bash
# Get Firebase token from your app or Firebase console
curl -X GET "https://gymmando-api-cjpxcek7oa-uc.a.run.app/token" \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```

## Security Notes

- Firebase ID tokens expire after 1 hour
- The UI should refresh tokens automatically
- All database queries are filtered by user_id
- No user can access another user's data

## Troubleshooting

### "Firebase Admin SDK not initialized"
- Check that `FIREBASE_CREDENTIALS_PATH` points to valid JSON file
- For GCP, ensure service account has Firebase Admin SDK permissions

### "Invalid or expired Firebase token"
- Token may have expired (refresh in UI)
- Check Firebase project configuration

### "user_id is None"
- Verify Firebase token contains `uid` claim
- Check token verification is working

### Database queries return empty
- Ensure `user_id` column exists in workouts table
- Check that workouts are being saved with `user_id` field

