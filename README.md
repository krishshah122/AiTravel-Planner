# 🌍 FlowTravel – AI-Powered Agentic Trip Planner

An intelligent, conversational travel planning application powered by **LangGraph**, **Groq LLM**, and **Supabase**. Chat with an AI agent to get detailed, personalized travel itineraries with real-time weather, restaurant recommendations, activity suggestions, and expense breakdowns.

---

## 🎯 What It Does

1. **Conversational Interface:** Chat naturally with an AI agent ("Plan a 3-day trip to Tokyo on a budget")
2. **Real-Time Data:** Fetches live weather (Open-Meteo), attractions/restaurants (Tavily search), currency conversion (ExchangeRate API)
3. **Intelligent Agent:** LangGraph-based agent automatically selects and chains the right tools for your query
4. **Secure Authentication:** Supabase-powered user accounts with JWT bearer tokens
5. **Trip History:** Save and revisit your previous trip plans
6. **Calendar Export:** Download your itinerary as `.ics` files for calendar apps

---

## 🏗️ Architecture

### **Frontend (Streamlit)**
- Chat-based UI with message history
- User authentication (Sign up / Login)
- Trip management (Save, load, switch between trips)
- Calendar download functionality

### **Backend (FastAPI)**
- `/query` → Processes travel planning requests via LangGraph agent
- `/generate_calendar` → Converts itinerary to iCalendar format
- Rate limiting and CORS middleware
- JWT token validation with Supabase

### **Agent (LangGraph)**
Orchestrates a multi-tool workflow:
- **Weather Tool** → Current weather + 5-day forecast (Open-Meteo)
- **Place Search Tool** → Attractions, restaurants, activities (Tavily)
- **Calculator Tool** → Cost calculations
- **Currency Converter Tool** → Real-time exchange rates (ExchangeRate API)

LLM automatically decides which tools to call based on user intent.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI + Uvicorn |
| **Agent Framework** | LangGraph + LangChain |
| **LLM** | Groq (Llama 3 model) |
| **Authentication** | Supabase + JWT |
| **Weather API** | Open-Meteo (free, no key required) |
| **Place Search** | Tavily (agentic search) |
| **Currency API** | ExchangeRate API |
| **Database** | Supabase (PostgreSQL) |
| **Environment** | Python-dotenv |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Git
- `.env` file with API keys (see setup below)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd langgraph
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# LLM
GROQ_API_KEY=your-groq-api-key

# APIs (optional, required only if using these services)
EXCHANGE_RATE_API_KEY=your-exchange-rate-api-key
TAVILY_API_KEY=your-tavily-api-key

# Backend URL (for Streamlit to call FastAPI)
Backend_url=http://localhost:8000
```

**Getting API Keys:**
- **Groq:** Sign up at [console.groq.com](https://console.groq.com)
- **Supabase:** Create project at [supabase.com](https://supabase.com)
- **ExchangeRate API:** Get key at [exchangerate-api.com](https://www.exchangerate-api.com)
- **Tavily:** Get key at [tavily.com](https://tavily.com)

---

## 🚀 Running the Application

### Option 1: Local Development

**Terminal 1 – Start FastAPI Backend**
```bash
uvicorn main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`

**Terminal 2 – Start Streamlit Frontend**
```bash
streamlit run streamlitapp.py
```
Frontend will open at `http://localhost:8501`

### Option 2: Docker
```bash
docker build -t flowtravel .
docker run -p 8000:8000 -p 8501:8501 --env-file .env flowtravel
```

---

## 📖 Usage Guide

### 1. **Create an Account**
   - Click "Sign Up" on the login screen
   - Enter email and password
   - You're authenticated via Supabase JWT

### 2. **Start Planning a Trip**
   - Type naturally: _"Plan a 3-day trip to Mumbai with a ₹50,000 budget"_
   - The AI agent will:
     - Identify the destination (Mumbai)
     - Fetch current weather
     - Search for attractions, restaurants, activities
     - Calculate expenses
     - Generate a comprehensive markdown itinerary

### 3. **Save Your Trip**
   - Trips are auto-saved when the AI responds
   - View previous trips in the sidebar under "Your Trips"

### 4. **Export to Calendar**
   - After getting an itinerary, click **"📅 Generate Calendar (.ics)"**
   - Download the `.ics` file to import into Google Calendar, Outlook, etc.

---

## 📁 Project Structure

```
langgraph/
├── streamlitapp.py              # Streamlit UI
├── main.py                      # FastAPI backend
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker config
├── setup.py                     # Package metadata
│
├── agent/
│   ├── __init__.py
│   └── agent.py                 # LangGraph agent builder & tool orchestration
│
├── tools/
│   ├── weather.py               # Weather tool (Open-Meteo wrapper)
│   ├── placesearch.py           # Place search tool (Tavily)
│   ├── expense.py               # Expense calculator
│   ├── convtcurr.py             # Currency converter
│   └── operat.py                # Other operations
│
├── utils/
│   ├── weatherinfo.py           # Open-Meteo API client
│   ├── placesearch.py           # Tavily API client
│   ├── currconvt.py             # ExchangeRate API client
│   ├── expensecal.py            # Expense logic
│   ├── model_loader.py          # LLM initialization (Groq)
│   └── config_loader.py         # Config parsing
│
├── prompt/
│   └── prompt.py                # System prompt for agent
│
└── config/
    └── config.yaml              # Configuration file
```

---

## 🔄 How the Agent Works

```
User Query: "Plan a 3-day trip to Tokyo"
    ↓
[LangGraph Agent cycles]
    ↓
TURN 1: LLM reads query + system prompt
    • Decides: "Need weather, places, restaurants, activities"
    • Selects tools: get_current_weather, search_places, etc.
    ↓
TURN 2: All selected tools execute in PARALLEL
    • Weather tool → 28°C, clear, wind 5km/h
    • Place search tool → Senso-ji Temple, Tokyo Tower, ...
    • Restaurant tool → Michelin-starred options, ...
    ↓
TURN 3: LLM reads all results
    • Decides: "I have enough data, now write final itinerary"
    • Returns: Comprehensive markdown with tables, breakdown, maps, etc.
    ↓
[Graph ends, response sent to Streamlit]
    ↓
User sees: Full itinerary in chat
```

---

## 🔐 Authentication Flow

```
1. User signs up/logs in via Streamlit
2. Supabase validates credentials, returns JWT token
3. Token stored in browser cookie (survives page refresh)
4. Each API request includes: Authorization: Bearer <JWT>
5. FastAPI validates token with Supabase
6. Request processed only if token is valid
```

---

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/query` | Send chat message, get itinerary |
| `POST` | `/generate_calendar` | Convert itinerary to .ics |
| `GET` | `/health` | Check backend health |
| `GET` | `/` | API status |

**Example Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"messages": ["Plan a trip to Paris"]}'
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Supabase auth fails | Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env` |
| LLM not responding | Verify `GROQ_API_KEY` is valid and has quota |
| Weather data missing | Open-Meteo is free, no key needed; check internet |
| Rate limit errors | Tavily/ExchangeRate APIs may have rate limits; wait and retry |
| Frontend can't reach backend | Ensure `Backend_url` in `.env` matches your FastAPI port |

---

## 🚀 Deployment

### Deploy Backend (Render.com)
1. Push code to GitHub
2. Connect repo to Render.com
3. Set environment variables in Render dashboard
4. Deploy as Python service on port 8000

### Deploy Frontend (Streamlit Cloud)
1. Push code to GitHub
2. Connect repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set environment variables in app settings
4. Deploy

---

## 📝 Environment Variables Checklist

- [ ] `SUPABASE_URL` – Your Supabase project URL
- [ ] `SUPABASE_KEY` – Your Supabase anon key
- [ ] `GROQ_API_KEY` – Groq API key for LLM
- [ ] `EXCHANGE_RATE_API_KEY` – (Optional) For currency conversion
- [ ] `TAVILY_API_KEY` – (Optional) For place/attraction search
- [ ] `Backend_url` – FastAPI backend URL (localhost:8000 for dev)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear descriptions

---

## 📄 License

Educational and demonstration purposes only. Always verify travel information before booking.

---

## 👤 Author

**Krish Shah** – [shahkrish551@gmail.com](mailto:shahkrish551@gmail.com)

Built with ❤️ using LangChain, LangGraph, Streamlit, and FastAPI.
