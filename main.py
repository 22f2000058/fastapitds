from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import List
import statistics

app = FastAPI()

# Strict CORS - only allow the specific origin
allowed_origin = "https://dash-u91np4.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Skip custom headers for OPTIONS preflight (let CORS middleware handle)
    if request.method != "OPTIONS":
        # Add X-Request-ID
        request_id = str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id
        
        # Add X-Process-Time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

@app.get("/stats")
async def get_stats(values: str = Query(...)):
    try:
        # Parse comma-separated values
        num_list = [int(x.strip()) for x in values.split(",") if x.strip()]
        
        if not num_list:
            raise ValueError("No valid numbers provided")
        
        count = len(num_list)
        total_sum = sum(num_list)
        min_val = min(num_list)
        max_val = max(num_list)
        mean = statistics.mean(num_list)
        
        # Your email (update if needed)
        email = "22f2000058@ds.study.iitm.ac.in"
        
        return {
            "email": email,
            "count": count,
            "sum": total_sum,
            "min": min_val,
            "max": max_val,
            "mean": round(mean, 6)  # Ensure precision
        }
    except Exception as e:
        return {"error": str(e)}, 400

# Explicit OPTIONS handler as backup for preflight
@app.options("/stats")
async def options_stats():
    return {}
