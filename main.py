from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import List
import statistics

app = FastAPI(title="TDS Metrics API")

# === STRICT CORS POLICY ===
ALLOWED_ORIGIN = "https://dash-u91np4.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],   # No wildcard *
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # X-Request-ID
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    
    # X-Process-Time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        # Parse values
        num_list = [int(x.strip()) for x in values.split(",") if x.strip().isdigit()]
        
        if not num_list:
            raise ValueError("No valid integers provided")
        
        count = len(num_list)
        total = sum(num_list)
        min_val = min(num_list)
        max_val = max(num_list)
        mean = statistics.mean(num_list)
        
        # ←←← UPDATE WITH YOUR EMAIL ←←←
        YOUR_EMAIL = "your-university-email@domain.com"
        
        return {
            "email": YOUR_EMAIL,
            "count": count,
            "sum": total,
            "min": min_val,
            "max": max_val,
            "mean": round(mean, 6)   # within ±0.01
        }
    except Exception as e:
        return {"error": str(e)}, 400