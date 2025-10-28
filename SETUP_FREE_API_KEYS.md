# 🔑 Free API Keys Setup Guide

## ✅ Your App is Now Configured for FREE APIs!

Your configuration in `config/config.yaml` uses:
- **Model:** `llama-3.1-8b-instant` (FREE on Groq)
- **Provider:** Groq (FREE tier available)

---

## 📝 Step-by-Step: Get FREE API Keys

### 1️⃣ Get Groq API Key (FREE)
1. Go to: https://console.groq.com/
2. Sign up (free account)
3. Navigate to: https://console.groq.com/keys
4. Click "Generate API Key"
5. Copy the key

### 2️⃣ Get Tavily API Key (FREE)
1. Go to: https://tavily.com/
2. Sign up for free account
3. Get your API key from dashboard
4. Copy the key

### 3️⃣ Get OpenWeatherMap API Key (FREE)
1. Go to: https://openweathermap.org/api
2. Sign up for free account (1000 calls/day)
3. Go to API Keys
4. Copy the key

### 4️⃣ Get Exchange Rate API Key (FREE)
1. Go to: https://www.exchangerate-api.com/
2. Sign up for free account (1500 calls/month)
3. Get your API key from dashboard
4. Copy the key

---

## 💻 Local Setup (.env file)

Create a file named `.env` in your project root:

```env
# Groq API (FREE)
GROQ_API_KEY=your_groq_api_key_here

# Tavily API (FREE)
TAVILY_API_KEY=your_tavily_api_key_here

# OpenWeatherMap API (FREE - 1000 calls/day)
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# Exchange Rate API (FREE - 1500 calls/month)
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here
```

---

## 🌐 Update Render Deployment

### Step 1: Push Changes to GitHub
```bash
git add config/config.yaml
git commit -m "Update to free Groq model"
git push
```

### Step 2: Update Environment Variables on Render
1. Go to: https://render.com/
2. Sign in to your account
3. Find your service: **aitravel-planner**
4. Click on it → Go to **"Environment"** tab
5. Add/Update these variables:

```
GROQ_API_KEY=your_actual_groq_key
TAVILY_API_KEY=your_actual_tavily_key
OPENWEATHERMAP_API_KEY=your_actual_openweathermap_key
EXCHANGE_RATE_API_KEY=your_actual_exchange_rate_key
```

6. Click **"Save Changes"**

### Step 3: Manual Deploy (Optional)
- Render should auto-deploy when you push to GitHub
- If not, go to **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🧪 Test Locally

After creating `.env` file:

```bash
# Start backend
uvicorn main:app --reload --port 8000

# In another terminal, start frontend
streamlit run streamlitapp.py
```

Visit: http://localhost:8501

---

## ✅ Current Configuration Status

**config/config.yaml** (Already updated ✓):
```yaml
llm:
  groq:
    model_name: "llama-3.1-8b-instant"  # FREE model
```

**utils/model_loader.py** (Already fixed ✓):
- Uses correct parameter: `model=` instead of `model_name=`

---

## 🎯 Quick Summary

1. ✓ Code updated for free Groq model
2. ✓ Model changed from decommissioned to active
3. ⏳ Need to add API keys to `.env` file
4. ⏳ Need to update Render environment variables
5. ⏳ Push changes to GitHub

---

## 💡 Need Help?

After adding API keys:
- Local testing: Runs on `localhost:8000` (backend) and `localhost:8501` (frontend)
- Render deployment: https://aitravel-planner-gy4l.onrender.com/

All APIs are **FREE** and have generous limits! 🎉

