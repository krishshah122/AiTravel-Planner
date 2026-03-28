from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from agent.agent import GraphBuilder
from starlette.responses import JSONResponse
import os
import datetime
import time
from collections import defaultdict
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv(override=True)

app = FastAPI(title="AI Travel Planner", version="1.0.0")
request_counts = defaultdict(list)
RATE_LIMIT = 10  
RATE_LIMIT_WINDOW = 60

# Global graph instance to avoid reinitializing on every request
_global_graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the graph once on startup"""
    global _global_graph
    try:
        print("Initializing graph on startup...")
        graph_builder = GraphBuilder(model_provider="groq")
        _global_graph = graph_builder.build_graph()
        print("Graph initialized successfully!")
        
        # Generate graph visualization exactly once on boot
        try:
            png_graph = _global_graph.get_graph().draw_mermaid_png()
            with open("my_graph.png", "wb") as f:
                f.write(png_graph)
            print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        except Exception as graph_error:
            print(f"Graph generation failed: {graph_error}")
            
    except Exception as e:
        print(f"Failed to initialize graph: {e}")
        _global_graph = None  

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Secured origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth dependency
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=500, detail="Missing Supabase config")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    try:
        userResponse = supabase.auth.get_user(token)
        if not userResponse.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return userResponse.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

class QueryRequest(BaseModel):
    messages: list[str]

class CalendarRequest(BaseModel):
    itinerary: str

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if current_time - req_time < RATE_LIMIT_WINDOW]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests. Please try again later."}
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "AI Travel Planner API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/test")
async def test():
    """Test basic imports and model loading"""
    try:
        from agent.agent import GraphBuilder
        return {"message": "Imports successful"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Import failed: {str(e)}"}
        )

@app.post("/query")
async def query_travel_agent(query: QueryRequest, current_user = Depends(get_current_user)):
    try:
        pass # Keep console clean during runtime
        
        # Use global graph or create new one if not initialized
        if _global_graph is None:
            print("Graph not initialized, creating new instance...")
            graph_builder = GraphBuilder(model_provider="groq")
            react_app = graph_builder.build_graph()
        else:
            react_app = _global_graph

        # Process the query
        messages = {"messages": query.messages}
        output = await react_app.invoke(messages)

        # Handle different output formats
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)
        
        return {"answer": final_output, "status": "success"}
        
    except Exception as e:
        print(f"Error in query_travel_agent: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Internal server error: {str(e)}", "status": "error"}
        )

@app.post("/generate_calendar")
async def generate_calendar(request: CalendarRequest, current_user = Depends(get_current_user)):
    try:
        from utils.model_loader import ModelLoader
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Load the LLM dynamically
        loader = ModelLoader(model_provider="groq")
        llm = loader.load_llm()
        
        # Strict prompting to prevent conversational text wrapping the ICS format
        sys_msg = SystemMessage(content="You are a strict data converter script. Convert the user's travel itinerary into a valid .ics (iCalendar) formatting string. Exclude code fences or markdown blocks. Start exactly with BEGIN:VCALENDAR and end with END:VCALENDAR.")
        user_msg = HumanMessage(content=f"Convert this itinerary to .ics:\n{request.itinerary}")
        
        response = llm.invoke([sys_msg, user_msg])
        
        # Clean potential markdown markdown code fences from the LLM response
        ics_text = response.content.replace('```ics', '').replace('```', '').strip()
        
        return {"ics": ics_text, "status": "success"}
    except Exception as e:
        print(f"Error in generate_calendar: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Internal server error: {str(e)}", "status": "error"}
        )