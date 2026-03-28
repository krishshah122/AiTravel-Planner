# 🗺️ AI Travel Planner: Workflow & Technical Roadmap

**Last Updated:** March 2026

---

## 📊 Current Workflow Architecture

### Phase 1: User Request Entry
```
User Action:
├─ Opens Streamlit app (localhost:8501)
├─ Authenticates via Supabase OAuth
│  └─ Available: Google, GitHub, etc.
├─ Session created with JWT token stored in st.session_state
└─ Chat interface becomes interactive
```

### Phase 2: Query Submission
```
User types: "Plan a 3-day trip to Paris with $1500 budget"
│
Streamlit Processing:
├─ Extract city via NLP (Groq API call)
│  └─ "Plan a 3-day trip to Paris with $1500 budget" → "Paris"
│  └─ Cache result to prevent redundant calls
├─ Geocode city (geopy/OpenStreetMap)
│  └─ Get coordinates: 48.8566°N, 2.3522°E
├─ Render interactive map (Folium)
└─ Package HTTP request:
   POST /query
   Headers: Authorization: Bearer <JWT_TOKEN>
   Body: {
     "messages": [
       "User: Plan a 3-day trip to Paris with $1500 budget"
     ]
   }
```

### Phase 3: Backend Authentication & Validation
```
FastAPI (/query endpoint):
│
├─ Middleware Layer
│  ├─ CORS check: Is origin "localhost:8501"?
│  ├─ Rate limit check: IP made < 10 requests/minute?
│  └─ Extract JWT token from Authorization header
│
├─ get_current_user() dependency
│  ├─ Calls Supabase: "Verify this JWT?"
│  ├─ If valid: Return user object
│  └─ If invalid: 401 Unauthorized (STOP)
│
└─ Request validation
   ├─ Parse QueryRequest body
   └─ Check message non-empty
```

### Phase 4: Agent Decision Loop (LangGraph)
```
LangGraph State: MessagesState = {
  "messages": [
    SystemMessage("You are a travel agent..."),
    HumanMessage("Plan a 3-day trip to Paris with $1500 budget")
  ]
}

ITERATION 1: Agent Decision
├─ Input: [system_prompt, user_message]
├─ Groq Llama3 processes: "What info do I need?"
├─ Decision: "Call get_weather_forecast('Paris')"
├─ Return: AIMessage with tool_calls=[get_weather_forecast]
└─ tools_condition evaluates: "Agent called tools? YES"

ITERATION 2: Tool Execution
├─ ToolNode receives: get_weather_forecast('Paris')
├─ Calls OpenWeatherMap API
├─ Returns: ToolMessage("Paris weather: 18°C, Sunny...")
├─ Appends to messages state
└─ tools_condition evaluates: "Loop back to agent? YES"

ITERATION 3: Agent Decision (with context)
├─ Input: [system_prompt, user_message, weather_result]
├─ Agent thinks: "I have weather. Need places next."
├─ Decision: "Call search_attractions('Paris')"
└─ ToolNode executes → Returns attractions list

ITERATION 4: Agent Decision (continued)
├─ Decision: "Call search_restaurants('Paris')"
└─ Returns: Restaurants with prices

ITERATION 5: Agent Decision (continued)
├─ Decision: "Calculate hotel cost: 150/night × 3 nights"
├─ ToolNode executes: estimate_total_hotel_cost(150, 3)
└─ Returns: 450.0

ITERATION 6: Agent Decision (continued)
├─ Decision: "Calculate daily budget"
├─ ToolNode executes: calculate_daily_expense_budget(1500, 3)
└─ Returns: 500/day

ITERATION 7: Agent Final Response
├─ Agent sees all gathered data
├─ Decision: "I have enough info. Final answer time."
├─ Composes Markdown response:
│  ├─ # Adventure in Paris!
│  ├─ ## Day 1-3 Itinerary
│  ├─ ## Attractions & Activities
│  ├─ ## Budget Breakdown (Markdown table)
│  ├─ ## Weather Summary
│  └─ ## Accommodation & Dining
└─ tools_condition evaluates: "Final answer detected? YES → EXIT LOOP"
```

### Phase 5: Response & Persistence
```
FastAPI returns to Streamlit:
{
  "response": "# Adventure in Paris!\n\n## Day 1: Arrival & Exploration..."
}

Streamlit Processing:
├─ Receives Markdown response
├─ Renders formatted text (bold, tables, bullets)
├─ Saves to chat history via Supabase:
│  ├─ Table: chat_history
│  ├─ Row: {
│  │    id: uuid(),
│  │    user_id: current_user_id,
│  │    title: "Plan a 3-day trip to Paris...",
│  │    messages: [...full conversation...],
│  │    created_at: now(),
│  │    updated_at: now()
│  │  }
│  └─ RLS ensures user can only see own history
└─ Display in chat window
```

### Phase 6: User Access to History
```
Sidebar "Your Trips":
├─ User clicks sidebar
├─ Streamlit fetches from Supabase:
│  SELECT id, title, messages 
│  FROM chat_history 
│  WHERE user_id = current_user_id
│  ORDER BY updated_at DESC
├─ Displays list of past trips
└─ User clicks trip → Loads conversation history
```

---

## 🔄 Current System Constraints

| Constraint | Impact | Workaround |
|---|---|---|
| Single FastAPI instance | Max ~100 concurrent requests | Deploy multiple instances behind load balancer |
| Sequential tool calls | Tools don't run in parallel | Rewrite with async tool execution |
| @st.cache_data | Streamlit reruns entire script | Use sessions + caching strategically |
| Groq rate limits | ~90 requests per minute | Queue requests if needed |
| Tavily API quota | 1000 requests/month (free tier) | Upgrade plan or cache results |
| OpenWeatherMap quota | 60 calls/minute (free tier) | Uses per-city caching |

---

## 🚀 Technical Roadmap (6-12 Months)

### Phase 1: Optimization (Weeks 1-4)
**Goal:** Reduce latency from 12s to 6s

**Tasks:**
- [ ] Implement async tool execution (run weather + places in parallel)
  ```python
  # Currently sequential:
  weather = await agent.call_tool("weather", "Paris")  # 5s
  places = await agent.call_tool("places", "Paris")    # 5s
  # Total: 10s
  
  # After async:
  weather, places = await asyncio.gather(
      agent.call_tool("weather", "Paris"),
      agent.call_tool("places", "Paris")
  )  # Total: 5s (concurrent)
  ```
- [ ] Add Redis caching layer for API responses
  - Cache weather for 1 hour (doesn't change frequently)
  - Cache place search for 24 hours
  - Reduce API calls by ~60%
- [ ] Optimize prompt engineering
  - Reduce system prompt verbosity
  - Fewer tool calls per query
- [ ] Profile agent loop iterations
  - Remove redundant tool calls
  - Set max iterations limit

**Success Metric:** Average latency < 6 seconds

---

### Phase 2: Features (Weeks 5-12)
**Goal:** Expand capabilities beyond basic itineraries

**Feature 1: PDF Export**
- [ ] Create ICS calendar files (already have `doc.py`)
- [ ] Generate PDF with images
- [ ] Email itinerary

```python
# Example: Generate PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

pdf = canvas.Canvas("itinerary.pdf", pagesize=letter)
pdf.drawString(100, 750, "# Adventure in Paris!")
# ... add itinerary, budget table, images ...
pdf.save()
```

**Feature 2: Image Integration**
- [ ] Use Tavily image search or Unsplash API
- [ ] Show pictures of attractions
- [ ] Embed in itinerary output

```python
@tool
def search_attraction_images(place: str) -> str:
    """Search images of tourist attractions"""
    # Use Unsplash API: free, high-quality
    # Return markdown: ![Eiffel Tower](image_url)
```

**Feature 3: User Preferences**
- [ ] Store user profile: "I like off-beat locations, vegetarian food"
- [ ] Embed in system prompt: "Remember, this user prefers..."
- [ ] Personalize recommendations

```python
# Save once:
user_preferences = {
  "travel_style": "adventure",
  "budget_level": "mid-range",
  "dietary_restrictions": ["vegetarian"],
  "pace": "slow"
}
supabase.table("users").update(user_preferences).eq("id", user_id).execute()

# Use in every query:
system_prompt += f"""
User Profile:
- Travel Style: {user_prefs['travel_style']}
- Budget: {user_prefs['budget_level']}
- Dietary: {user_prefs['dietary_restrictions']}

Personalize recommendations based on this profile.
"""
```

**Feature 4: Booking Integration (Optional)**
- [ ] Partner with Booking.com API
- [ ] Agent can suggest + link to bookings
- [ ] Commission opportunity (monetization)

```python
@tool
def search_hotel_availability(city: str, checkin: str, checkout: str) -> str:
    """Search hotels via Booking.com API"""
    # Link directly to booking.com affiliate link
    # Return: [{name, rating, price, booking_url}, ...]
```

**Success Metric:** 2-3 features shipped, user engagement +50%

---

### Phase 3: Scaling (Months 4-6)
**Goal:** Support 1000+ concurrent users

**Infrastructure Upgrades:**
- [ ] Deploy on AWS ECS (Elastic Container Service)
  - Auto-scaling: 1-10 instances based on load
  - Each instance runs FastAPI + LangGraph
  - Load balancer (ALB) distributes traffic
  
```yaml
# ECS Task Definition
{
  "containerDefinitions": [
    {
      "name": "fastapi-agent",
      "image": "my-registry/travel-agent:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "GROQ_API_KEY", "value": "${GROQ_API_KEY}"},
        {"name": "SUPABASE_URL", "value": "${SUPABASE_URL}"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/travel-agent",
          "awslogs-region": "us-east-1"
        }
      }
    }
  ]
}
```

- [ ] Use Redis (ElastiCache) for distributed rate limiting
  ```python
  import redis
  
  redis_client = redis.Redis(host='elasticache-endpoint', port=6379)
  
  def check_rate_limit(ip: str) -> bool:
      key = f"rate_limit:{ip}"
      count = redis_client.incr(key)
      if count == 1:
          redis_client.expire(key, 60)  # Reset every 60s
      return count <= 10
  ```

- [ ] Add CloudFront CDN for static assets
- [ ] Use RDS (Managed PostgreSQL) for Supabase
- [ ] Add S3 for storing PDFs, images
- [ ] CloudWatch + Alarms for monitoring

**Success Metric:** Handle 1000 concurrent users with <10s latency

---

### Phase 4: Production Hardening (Months 7-9)
**Goal:** Enterprise-grade reliability

**Tasks:**
- [ ] Add comprehensive logging (CloudWatch Logs)
  ```python
  import logging
  logger = logging.getLogger("travel_agent")
  logger.info(f"User {user_id} requested {destination}")
  logger.error(f"Tavily API failed: {error}")
  ```

- [ ] Error tracking (Sentry)
  ```python
  import sentry_sdk
  sentry_sdk.init("https://key@sentry.io/project")
  
  try:
      response = tavily_api.search(query)
  except Exception as e:
      sentry_sdk.capture_exception(e)
  ```

- [ ] Database backups (RDS automated snapshots)
- [ ] Disaster recovery plan (multi-region failover)
- [ ] PII compliance (GDPR, CCPA)
  - Allow users to download/delete data
  - Right to be forgotten
- [ ] API versioning (/v1/query, /v2/query)
- [ ] API documentation (Swagger UI auto-generated by FastAPI)

**Success Metric:** Zero unplanned downtime, 99.9% uptime SLA

---

### Phase 5: Monetization (Months 10-12)
**Goal:** Generate revenue

**Options:**
1. **Freemium Model**
   - Free: 5 queries/month
   - Pro: 100 queries/month ($5/month)
   - Enterprise: Unlimited ($100/month)

2. **Booking Affiliate**
   - Embed Booking.com links in itineraries
   - Earn 3-5% commission on bookings

3. **B2B (Travel Agencies)**
   - White-label API for agencies
   - $500/month per agency

```python
# Create pricing tiers
TIERS = {
    "free": {"queries_per_month": 5, "price": 0},
    "pro": {"queries_per_month": 100, "price": 5},
    "enterprise": {"queries_per_month": None, "price": 100}
}

# Check tier on query
user_tier = supabase.table("users").select("tier").eq("id", user_id)
remaining = TIER[user_tier]["queries_per_month"] - user_queries_this_month

if remaining <= 0:
    raise HTTPException(402, "Monthly quota exceeded. Upgrade to Pro.")
```

**Success Metric:** $5k MRR (Monthly Recurring Revenue)

---

## 📈 Metrics to Track

### User Metrics
```
Total Users: Count of registered accounts
Active Users: Users who queried in last 30 days
Retention: % of users returning after 7 days
Churn: % of users who leave
```

### Performance Metrics
```
Latency (p50, p95, p99):
- p50: 8 seconds (median)
- p95: 15 seconds (95th percentile)
- p99: 20 seconds (99th percentile)

Error Rate: % of requests that fail
Token Usage: Avg tokens per query (for cost tracking)
Cache Hit Rate: % of queries served from cache
```

### Business Metrics
```
Cost per Query: API costs / total queries
Revenue per User: MRR / active users
Conversion Rate: Free users → Paid users
```

---

## 🎯 Success Criteria by Phase

| Phase | Timeline | Goal | Status |
|---|---|---|---|
| Optimization | Week 4 | 6s latency | 🚀 Ready |
| Features | Week 12 | PDF + Images | 📋 Planned |
| Scaling | Month 6 | 1k users | 📋 Planned |
| Hardening | Month 9 | 99.9% uptime | 📋 Planned |
| Monetization | Month 12 | $5k MRR | 📋 Planned |

---

## 💰 Estimated Costs

| Service | Free Tier | Monthly Cost @ Scale |
|---|---|---|
| **Groq API** | 7k tokens/day | $50 (1M tokens/month) |
| **OpenWeatherMap** | 60 calls/min | $50 (Pro plan) |
| **Tavily API** | 1k searches/month | $30 (upgraded) |
| **AWS ECS** | ❌ | $150 (10 instances) |
| **AWS RDS PostgreSQL** | ❌ | $50 |
| **AWS S3** | 5GB free | $10 |
| **CloudFront CDN** | Varies | $20 |
| **Supabase** | 500MB | $25 (PostgreSQL) |
| **Redis ElastiCache** | ❌ | $20 |
| **Monitoring (CloudWatch)** | Varies | $30 |
| **Domain + SSL** | ❌ | $15 |
| **Misc (CI/CD, backups)** | ❌ | $30 |
| | | **Total: ~$380/month** |

**Pricing Model to Cover Costs:**
- 1000 Pro users × $5 = $5,000 revenue
- Booking commissions: +$2,000
- **Total: $7,000 >> $380 costs** ✅ Profitable at scale

---

## 🎓 Key Learnings

1. **LangGraph is worth it:** Loops enable genuine intelligence vs. linear chains
2. **Groq wins:** Speed matters; slow LLM kills UX
3. **Caching is magic:** @st.cache_data reduces latency ~40%
4. **API choice matters:** Tavily >> Nominatim (rate limits are real)
5. **Prompt engineering is underrated:** Good System Prompt prevents half the issues

---

**Next Action:** Run Phase 1 optimization tasks to reduce latency to 6 seconds.
