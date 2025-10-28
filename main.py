from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from agent.agent import GraphBuilder
from utils.doc import save_document
from starlette.responses import JSONResponse
import os
import datetime
import time
from collections import defaultdict
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

app = FastAPI(title="AI Travel Planner API", version="1.0.0")
request_counts = defaultdict(list)
RATE_LIMIT = 10  
RATE_LIMIT_WINDOW = 60  

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

class QueryRequest(BaseModel):
    messages: list[str]

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

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        print(f"Received query: {query}")
        
        # Add timeout and better error handling
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        # Generate graph visualization
        try:
            png_graph = react_app.get_graph().draw_mermaid_png()
            with open("my_graph.png", "wb") as f:
                f.write(png_graph)
            print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        except Exception as graph_error:
            print(f"Graph generation failed: {graph_error}")
            # Continue without graph if it fails

        # Process the query
        messages = {"messages": query.messages}
        output = react_app.invoke(messages)

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