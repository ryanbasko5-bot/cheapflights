# 🚀 TWILIO SETUP GUIDE (5 Minutes)

## Step 1: Sign Up (2 minutes)

1. **Go to**: https://www.twilio.com/try-twilio
2. **Fill in**: Email, Name, Password
3. **Verify**: Phone number (they'll send you a code)
4. **Skip**: The survey questions (just click through)

## Step 2: Get a Phone Number (1 minute)

1. After signup, you'll see: **"Get a Twilio phone number"**
2. Click: **"Get your first Twilio phone number"**
3. Twilio will suggest a number
4. Click: **"Choose this number"**
5. **Copy** the number (e.g., `+61234567890`)

## Step 3: Get API Credentials (1 minute)

1. **Go to**: https://console.twilio.com
2. Look for **"Account Info"** section (right side of dashboard)
3. You'll see:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click "Show" to reveal it

4. **Copy both**

## Step 4: Update .env File (1 minute)

Open `.env` file and replace:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+61234567890
```

With your actual credentials.

## Step 5: Test It! (30 seconds)

```bash
python quick_test.py
```

You should receive SMS in **10-30 seconds**!

---

## 💰 Twilio Free Trial

- **$15 free credit** (enough for ~1000 SMS)
- Sends to **any country** (including Australia)
- **Trial limitation**: Can only send to **verified phone numbers**
  - Your phone is auto-verified during signup
  - To test with other numbers: Console → Phone Numbers → Verified Caller IDs

---

## 🆘 Common Issues

### Issue 1: "Unverified number"
**Solution**: Console → Phone Numbers → Verified Caller IDs → Add your test number

### Issue 2: "Insufficient funds"
**Solution**: You've used up $15 credit. Upgrade account or add payment method.

### Issue 3: "Invalid phone number format"
**Solution**: Must include country code (e.g., `+61411246861` not `0411246861`)

---

## 🎯 What to Tell Me

Once you have the credentials, send me:
1. ✅ Account SID (starts with `AC`)
2. ✅ Auth Token
3. ✅ Your Twilio phone number (the one you got in Step 2)

I'll update the `.env` file and we'll test!
