# 👨‍💻 AI Travel Planner: Step-by-Step Interview Guide

This guide breaks down your exact codebase file-by-file so you can explain your engineering decisions flawlessly during your interview. 

---

## 1. The Tech Stack: "What & Why"

During your interview, they will ask you why you chose certain technologies. Use these answers:

* **Frontend (Streamlit):** "I used Streamlit because it allows me to rapidly prototype a Python-native conversational UI. It handles state management (like chat history) natively, letting me focus on the AI engineering rather than writing React/JavaScript."
* **Backend (FastAPI):** "I chose FastAPI because it is asynchronous by default, incredibly fast, and auto-generates Swagger documentation. It's the industry standard for serving machine learning models and AI agents."
* **Agent Framework (LangGraph):** "I chose LangGraph over standard LangChain because it lets me build a cyclical state machine. Traditional chains are linear (A -> B -> C). LangGraph allows the agent to loop (Agent -> Tool -> Agent -> Tool) until it gathers enough information to answer the user."
* **LLM (Groq - Llama3):** "I used Groq because its LPU architecture processes tokens at breakneck speeds (~300+ tokens/sec). Since my agent does multi-hop reasoning (pinging weather, then places, then calculating), a slow LLM would compound latency to unacceptable levels."
* **Authentication (Supabase):** "I needed secure, cryptographic JWT verification without building a custom database. Supabase provides enterprise-grade OAuth and Row Level Security instantly."

---

## 2. Codebase Walkthrough (File by File)

If they ask you to walk through your code or explain how data flows from the user to the AI, explain this exact path:

### Step 1: The User Interface (`streamlitapp.py`)
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
