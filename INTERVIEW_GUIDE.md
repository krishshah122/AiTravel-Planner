# 👨‍💻 AI Travel Planner: Comprehensive Interview Guide

**Last Updated:** March 2026  
**Project:** AI-Powered Trip Planning Agent with Real-Time Multi-Tool Integration  
**Status:** Production-ready with AWS infrastructure  

This guide breaks down your exact codebase file-by-file so you can explain your engineering decisions flawlessly during your interview.

---

## 📊 Quick Project Summary

**What:** An AI agent that autonomously plans trips by conversing with users and calling multiple real-time APIs (weather, place search, expense calculation, currency conversion) to build comprehensive, cost-detailed travel itineraries.

**Why it's impressive:** Unlike simple chatbots, this system makes **intelligent decisions** about which tools to use and in what sequence. It's a production-grade agentic application with security, rate limiting, and multi-step reasoning.

**One-liner for interviews:** *"A multi-tool AI agent that autonomously reasons about travel planning, using LangGraph to orchestrate sequential API calls and generate detailed, cost-accurate itineraries."*

---

## 1. The Tech Stack: "What & Why" (Deep Dive)

### Frontend Layer
**Technology:** Streamlit  
**Why Streamlit?**
- Rapid prototyping: Full conversational UI in pure Python (no JavaScript needed)
- Native session management: Handles chat history, user state automatically
- Caching system: `@st.cache_data` prevents redundant API calls (major latency win)
- Real-time updates: Perfect for agent response streaming
- Deployment: Single-line deployment on Render/Heroku

**What you built with it:**
- Chat interface with conversation history persistence (via Supabase)
- Interactive map rendering with geolocation
- NLP-based city name extraction (before passing to mapping services)
- Markdown-formatted agent responses with tables and formatting

**Interview insight:** "Streamlit allowed me to ship a production UI in days instead of weeks. I didn't need to build a React frontend separately."

---

### Backend Layer
**Technology:** FastAPI  
**Why FastAPI?**
- Asynchronous by default: Can handle 100+ concurrent requests without blocking
- Auto-generated docs: Swagger/OpenAPI built-in (shows you're production-ready)
- Dynamic type validation: Pydantic integration catches malformed requests instantly
- Speed: 2-3x faster than Django/Flask on the same hardware
- Built for AI: Industry standard for ML model serving and agentic systems

**What you implemented:**
- Rate limiting (10 req/min per IP): Prevents bot attacks
- JWT authentication: Custom `get_current_user()` dependency that validates Supabase tokens
- CORS security: Locked to `localhost:8501` only
- Health checks: API availability monitoring
- Single global graph instance: Initialized once at startup, reused for all requests (efficiency hack)

**Code highlight:** Show this in interview:
```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase: Client = create_client(supabase_url, supabase_key)
    try:
        userResponse = supabase.auth.get_user(token)
        if not userResponse.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return userResponse.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
```
This shows you understand production security patterns.

---

### Agent Orchestration
**Technology:** LangGraph (by LangChain)  
**Why LangGraph over LangChain chains?**
- **Loops matter:** LangChain chains are linear (Tool A → Tool B → Tool C → End). Travel planning needs loops:
  - Agent: "I need weather for Paris"
  - Tool Node executes weather API
  - Agent: "I need restaurants too"
  - Tool Node executes place search
  - Agent: "I have enough info, here's your itinerary"
- **Conditional routing:** The agent **decides** which tools to call, not a pre-defined sequence
- **State management:** `MessagesState` keeps full conversation history between loops
- **Better visualization:** Generates graph diagrams showing agent decision flow

**What you built:**
- **StateGraph with two nodes:**
  1. `agent_function`: Calls Groq LLM with available tools
  2. `ToolNode`: Executes whatever tool the agent selected
- **Edges:**
  - START → agent
  - agent → [conditional] → tools OR end
  - tools → agent (loops back)
- **Tool binding:** `llm.bind_tools(tools=self.tools)` tells Groq which tools exist

**Interview explanation:**
"I used LangGraph because it enforces a clear control flow. The agent decides when to stop calling tools and provide a final answer. With traditional chains, you'd hardcode the sequence upfront—no intelligence in tool selection."

---

### LLM Choice
**Technology:** Groq (Running Llama 2/3)  
**Why Groq?**
- **Speed:** LPU (Language Process Unit) architecture: 300+ tokens/second vs OpenAI's ~60 tokens/sec
- **Cost:** ~10x cheaper than GPT-4
- **Multi-tool bottleneck:** My agent calls 4-5 tools in sequence. A slow LLM would:
  - Get weather (15 sec)
  - Get places (15 sec)
  - Get expenses (10 sec)
  - **Total: 40 seconds with slow LLM**
  - **Groq: 12 seconds** (still bottlenecked by APIs, not LLM)
- **Open source model:** Llama 2/3 has no IP restrictions (good for commercial apps)

**Fallback strategy you could mention:**
"If Groq had downtime, I could swap to OpenAI's GPT-4 with one environment variable change. The `ModelLoader` class handles that abstraction."

---

### Authentication
**Technology:** Supabase (PostgreSQL + Auth)  
**Why Supabase?**
- Don't build databases: Supabase provides hosted PostgreSQL
- Don't build auth: Supabase OAuth + JWT + MFA out-of-the-box
- Row Level Security (RLS): Each user only sees their own chat history
- Realtime subscriptions: Can push chat updates instantly (future feature)
- Developer experience: Dashboard UI for managing users/data

**What you use it for:**
- User authentication (JWT tokens)
- Storing chat history in `chat_history` table
- Retrieving user's past trips from `Your Trips` sidebar

**Interview angle:** "I chose Supabase because user data is sensitive. Rather than building SQLAlchemy models and bcrypt hashing myself, I delegated to a battle-tested platform."

---

### Data APIs (Tools)
**Weather:** OpenWeatherMap API  
- Provides current weather + 5-day forecast  
- Called by agent when user asks about climate

**Places/Activities:** Tavily Search API  
- High-quality structured search results (better than Google Places for this use case)
- Covers attractions, restaurants, activities, transportation
- Called 4 times per trip (one for each category)

**Expense Calculation:** Custom Python calculator  
- Handles cost breakdowns (hotel × nights, meals × days, etc.)
- Formats numbers (strips `$`, handles commas: `$1,200` → 1200.0)

**Currency Conversion:** Custom logic (can integrate Fixer.io or XE.com later)  
- Allows trip costs in different currencies

---

## 2. Architecture & Data Flow (Visual)

---

## 2. Architecture & Data Flow (Visual)

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (BROWSER)                          │
│                    Streamlit Chat Interface (Port 8501)              │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │  Chat History    │  │  Map Widget  │  │ User Sidebar   │        │
│  │  (from Supabase) │  │  (Folium)    │  │ (Your Trips)   │        │
│  └────────┬─────────┘  └──────────────┘  └────────────────┘        │
└───────────┼────────────────────────────────────────────────────────┘
            │ HTTP POST                      JWT Auth Header
            │ /query                         Access Token
            │
┌───────────▼────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI, Port 8000)                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  MIDDLEWARE LAYER                                             │   │
│  │  ├─ CORS Validation (localhost:8501 only)                    │   │
│  │  ├─ Rate Limiting (10 req/min per IP)                        │   │
│  │  └─ JWT Authentication via Supabase                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  QUERY ENDPOINT: POST /query                                  │   │
│  │  ├─ Validates user token                                     │   │
│  │  ├─ Extracts message history from request                    │   │
│  │  └─ Feeds to Global Graph Instance                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└───────────┬──────────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────────┐
│           AI ORCHESTRATION LAYER (LangGraph)                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  NODE 1: agent_function                                    │  │
│  │  ├─ Takes MessagesState (conversation history)             │  │
│  │  ├─ Adds system prompt (from prompt.py)                    │  │
│  │  ├─ Calls Groq Llama3 API with bound tools                 │  │
│  │  └─ Returns agent_response with tool selections            │  │
│  └────────┬─────────────────────────────────────────────────┘   │
│           │                                                      │
│           ├─ CONDITIONAL LOGIC (tools_condition)                │
│           │  ├─ If agent selected tools → go to ToolNode       │
│           │  └─ If agent said "Final answer" → return response │
│           │                                                      │
│  ┌────────▼─────────────────────────────────────────────────┐   │
│  │  NODE 2: tools (ToolNode)                                 │   │
│  │  ├─ Parses agent's tool selection                         │   │
│  │  ├─ Executes: get_current_weather,                        │   │
│  │  │           search_attractions,                          │   │
│  │  │           estimate_total_hotel_cost, etc.              │   │
│  │  └─ Appends tool_result to message state                  │   │
│  │  └─ Loops back to agent_function                          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────┬───────────────────────────────────────────────────┘
            │ (loops until agent says "Final answer")
            │
┌───────────▼───────────────────────────────────────────────────┐
│              API CALLS (External Services)                     │
│                                                                │
│  ┌──────────────────┐ ┌──────────────────┐                    │
│  │ OpenWeatherMap   │ │ Tavily Search    │                    │
│  │ get_current...   │ │ search_...       │                    │
│  │ get_forecast...  │ │ attractions,etc. │                    │
│  └──────────────────┘ └──────────────────┘                    │
│                                                                │
│  ┌──────────────────┐ ┌──────────────────┐                    │
│  │ Local Calcs      │ │ Currency Conv    │                    │
│  │ (Python math)    │ │ (can integrate)  │                    │
│  └──────────────────┘ └──────────────────┘                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘

PERSISTENCE LAYER:
┌────────────────────────────────────────────────────────────────┐
│ Supabase PostgreSQL                                            │
│ ├─ chat_history table: { id, user_id, title, messages }       │
│ ├─ users table: (managed by Supabase Auth)                    │
│ └─ Row Level Security: Each user only sees own data           │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow: User Message to Itinerary

```
1. USER ACTION
   User types: "Plan a 3-day trip to Paris"
   │
2. FRONTEND PROCESSING
   ├─ Streamlit extracts city name (NLP call to Groq)
   ├─ Caches this extraction (@st.cache_data)
   ├─ Fetches map coordinates via geopy
   ├─ Renders folium map
   └─ Sends HTTP POST /query with:
      {
        "messages": ["User: Plan a 3-day trip to Paris"],
        "Authorization": "Bearer <JWT_TOKEN>"
      }
   │
3. BACKEND AUTHENTICATION
   ├─ FastAPI intercepts request
   ├─ Extracts JWT token from header
   ├─ Calls Supabase: "Is this token valid?"
   ├─ If invalid → 401 Unauthorized (STOP)
   └─ If valid → Continue to agent
   │
4. AGENT DECISION LOOP (LangGraph)
   
   ITERATION 1:
   ├─ Agent sees: "Plan a 3-day trip to Paris"
   ├─ Agent thinks: "I need weather, places, expenses"
   ├─ Agent decides to call: get_weather_forecast("Paris")
   └─ ToolNode executes → Returns "Forecast: Sunny 18°C, Rain 16°C..."
   
   ITERATION 2:
   ├─ Agent sees: Previous message + weather result
   ├─ Agent decides to call: search_attractions("Paris")
   └─ ToolNode executes → Returns "Eiffel Tower, Louvre, Arc de Triomphe..."
   
   ITERATION 3:
   ├─ Agent sees: All previous data
   ├─ Agent decides to call: estimate_total_hotel_cost(150, 3)
   └─ ToolNode executes → Returns 450.0
   
   ITERATION 4:
   ├─ Agent sees: All data gathered
   ├─ Agent decides: "I have enough info!"
   ├─ Agent stops calling tools
   └─ Agent composes final Markdown response
   │
5. RESPONSE FORMATTING
   ├─ Agent creates Markdown with:
   │  ├─ # Adventure in Paris!
   │  ├─ ## Day-by-Day Itinerary
   │  ├─ ## Budget Breakdown (table format)
   │  ├─ ## Weather Forecast
   │  └─ ## Recommended Hotels, Restaurants, etc.
   └─ FastAPI returns this as JSON
   │
6. FRONTEND DISPLAY
   ├─ Streamlit receives response
   ├─ Renders Markdown beautifully
   ├─ Saves chat to Supabase chat_history
   └─ Message appears in chat window with formatting
```

---

## 3. Codebase Deep Dive (File by File)
This is the entry point of the application.
1. **The Auth Guard:** When a user lands, the app halts rendering (`st.stop()`) unless `st.session_state.user` exists. If they log in, Supabase issues a cryptographically secure `access_token`. 
2. **The Chat Interface:** The user types a query ("Plan a 3-day trip to Paris"). 
3. **The Map Fix (NLP Extraction):** *Highlight this feature!* Explain that mapping libraries (`geopy`) crash when given a full sentence. Before drawing the map, you make a 0.2-second call to Groq to extract just the city name ("Paris"). You then heavily cache this using `@st.cache_data` to prevent geocoding rate-limits.
4. **The Handoff:** The Streamlit app packages the chat history and the Supabase JWT token and makes an HTTP POST request to the backend.

### Step 2: The Backend Server (`main.py`)
This file protects the AI from abuse and serves the responses.
1. **CORS & Rate Limiting:** You've implemented a custom middleware that tracks IP addresses and blocks traffic if someone spams your server (MAX 10 requests per minute). You also locked CORS so other websites cannot hijack your frontend.
2. **JWT Authentication:** *Highlight this security feature!* You wrote a custom `Depends(get_current_user)` function. Before FastAPI even runs the AI, it intercepts the `Authorization: Bearer <token>` header, pings Supabase, and rejects fake tokens with a `401 Unauthorized`. 
3. **Calendar Generator:** A separate endpoint uses a strict System Prompt to convert JSON agent outputs into clean `.ics` calendar files.

### Step 3: The AI Brain (`agent/agent.py`)
This is where the LangGraph logic lives. 
1. **GraphBuilder:** It initializes the LLM and gives it a list of tools (the "Swiss Army Knife"). 
2. **Nodes and Edges:** You defined a `StateGraph`. 
   - Node 1: `agent_function` (The brain thinking).
   - Node 2: `tools` (The APIs executing).
   - Edges: The agent loops conditionally. If the agent decides it needs to use a tool, it goes to `tools`. `tools` sends data back to the `agent_function`. When it's finally satisfied, it terminates formatting a response.

### Step 4: The Tools (`tools/` folder)
Explain that you explicitly broke your tools into separate files rather than one massive script to follow the **Single Responsibility Principle**.
- **`placesearch.py`:** Uses the `TavilySearch` API. *Tell the interviewer you specifically removed OpenStreetMap (Nominatim) from the agent sequence because Nominatim's strict 1-req/sec rate-limits were bottlenecking the agent and causing 15-second cascade delays.*
- **`expense.py`:** Defines explicit typing (like `list[float]`) so the LLM knows exactly how to format its JSON arguments.
- **`prompt.py`:** *Highlight your Security Defenses.* Explain that you added explicit anti-injection guardrails to the bottom of the System Prompt to prevent malicious users from hacking the LLM into printing out its API keys.

---

## 3. Top 3 Interview Questions & Answers

**Q: Why did you use a Single Agent architecture instead of a Multi-Agent system?**
*Answer:* "For this scope, a single 'ReAct' agent with a suite of 4-5 well-defined tools is vastly superior for Latency. A Multi-Agent system (e.g., a Manager delegating to a Finance Agent and a Weather Agent) requires sending full message histories back and forth between different LLMs. That network overhead would push load times up to 45+ seconds. The Single Agent hits the sweet spot of high intelligence and sub-15s latency."

**Q: How do you handle security in your application?**
*Answer:* "Security is implemented in three layers. First, Environment Variables protect my API keys. Second, the Network Layer is protected: Frontend hits are checked with Supabase Auth, and Backend hits are verified with a custom JWT Dependency middleware and IP Rate Limiting. Third, the AI Layer is protected with explicit prompt injection guardrails prohibiting it from revealing systemic instructions."

**Q: How did you solve Latency issues?**
*Answer:* "I profiled the application and realized LangGraph tools run sequentially. Furthermore, free tools like OpenStreetMap forcibly delayed the agent with timeouts. I optimized this by strictly substituting slow APIs for premium high-concurrency APIs like Tavily, and implementing `@st.cache_data` in my frontend to permanently memoize heavy map renderings."

---

## ✅ Pre-Interview Checklist
- [ ] Read through this document exactly.
- [ ] Pull up `streamlitapp.py` line 191 to physically show them the clever NLP Map Extraction technique.
- [ ] Pull up `main.py` line 56 to show them the custom JWT validation dependency you wrote.
