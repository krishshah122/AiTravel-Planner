# ⚡ Quick Reference - AI Travel Planner

## 🎯 What It Does
An **AI agent** that plans trips by:
- Chatting with users about destination/duration
- Using tools to fetch real-time data
- Calculating costs automatically
- Generating detailed itineraries with day-by-day breakdowns

---

## 📐 Architecture (Simple)
```
User → Streamlit UI → FastAPI Backend → LangGraph Agent → Tools → Response
                                                    ↓
                                [Weather | Places | Calculator | Currency]
```

---

## 🔑 Key Components

### 1. **Agent** (`agent/agent.py`)
- LangGraph workflow
- Decides which tools to use
- Maintains conversation state

### 2. **Tools** (4 main tools in `/tools/`)
- `weather.py` - Current weather & forecast
- `placesearch.py` - Attractions, restaurants, activities
- `expense.py` - Cost calculations
- `convtcurr.py` - Currency conversion

### 3. **Backend** (`main.py`)
- FastAPI with rate limiting
- `/query` endpoint
- Health checks

### 4. **Frontend** (`streamlitapp.py`)
- Chat interface
- Session history
- Markdown formatting

---

## 🛠 Tech Stack
- **AI:** LangGraph + LangChain
- **LLM:** Groq (fast & cost-effective)
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Deploy:** AWS (ECS, S3, CloudFront)

---

## 💬 Elevator Pitch (30 sec)
*"I built an AI Travel Planner using LangGraph that acts as a smart travel agent. Instead of just giving generic advice, it uses real-time tools to fetch weather, search for restaurants, calculate costs, and build comprehensive itineraries. The agent decides which tools to use and can make multiple tool calls in sequence to provide complete trip plans."*

---

## 🎤 Demo Script
1. Open app: `streamlit run streamlitapp.py`
2. Query: "Plan a 5-day trip to Bali"
3. Show response (weather, hotels, attractions, costs)
4. Show graph: `my_graph.png` (agent's decision flow)

---

## 🏆 Impressive Features
✅ Autonomous tool usage (not just chat)  
✅ Real-time data integration  
✅ Cost estimation intelligence  
✅ Production-ready (rate limiting, health checks)  
✅ AWS deployment ready  
✅ Graph visualization of agent reasoning  

---

## 📝 Key Interview Answers

**Q: Why LangGraph?**  
A: "Better control over agent workflow. The graph structure enables conditional routing - the agent decides when to use tools vs respond. This creates intelligent multi-step reasoning."

**Q: Biggest Challenge?**  
A: "Coordinating multiple API calls with fallback mechanisms and maintaining conversation context across tool calls."

**Q: What would you improve?**  
A: "Add persistent memory for user history, PDF export functionality, and booking API integration."

---

**One-liner:** *AI agent that autonomously plans trips using real-time data tools*

