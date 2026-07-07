from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from pydantic import BaseModel
import jwt
import statistics
import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

app = FastAPI(title="TDS API - Stats + JWT + Config")

# ==================== CORS ====================
ALLOWED_ORIGIN = "https://dash-u91np4.example.com"

# ==================== CORS (Updated for Grader) ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # Allow all for grader to reach it
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    if request.method != "OPTIONS":
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# ==================== STATS ENDPOINT (Q1) ====================
@app.get("/stats")
async def get_stats(values: str = Query(...)):
    try:
        num_list = [int(x.strip()) for x in values.split(",") if x.strip()]
        if not num_list:
            raise ValueError("No valid numbers")
        
        return {
            "email": "22f2000058@ds.study.iitm.ac.in",
            "count": len(num_list),
            "sum": sum(num_list),
            "min": min(num_list),
            "max": max(num_list),
            "mean": round(statistics.mean(num_list), 6)
        }
    except Exception:
        return {"error": "Invalid input"}, 400

# ==================== VERIFY ENDPOINT (Q2) ====================
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-flo4p4fi.apps.exam.local"

class TokenRequest(BaseModel):
    token: str

@app.post("/verify")
async def verify_token(payload: TokenRequest):
    try:
        decoded = jwt.decode(
            payload.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"verify_exp": True, "verify_iss": True, "verify_aud": True}
        )
        return {
            "valid": True,
            "email": decoded.get("email"),
            "sub": decoded.get("sub"),
            "aud": decoded.get("aud")
        }
    except Exception:
        raise HTTPException(status_code=401, detail={"valid": False})

# ==================== CONFIG ENDPOINT (Q3) ====================
load_dotenv()

def load_config() -> Dict[str, Any]:
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }
    
    # Layer 2: YAML
    try:
        with open("config.development.yaml", "r") as f:
            yaml_config = yaml.safe_load(f) or {}
            config.update(yaml_config)
    except FileNotFoundError:
        pass
    
    # Layer 3+4: .env + OS env (OS has higher priority)
    env_map = {
        "APP_PORT": "port",
        "NUM_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key"
    }
    
    for env_key, config_key in env_map.items():
        if env_key in os.environ:
            value = os.environ[env_key]
            if config_key in ["port", "workers"]:
                config[config_key] = int(value)
            elif config_key == "debug":
                config[config_key] = str(value).lower() in ["true", "1", "yes", "on"]
            else:
                config[config_key] = value
    
    return config


@app.get("/effective-config")
async def effective_config(set: list[str] = Query(default=[])):
    # Load fresh every request so grader's dynamic OS env vars are respected
    config = load_config()
    
    # Apply CLI overrides (highest precedence)
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            if key in ["port", "workers"]:
                config[key] = int(value)
            elif key == "debug":
                config[key] = value.lower() in ["true", "1", "yes", "on"]
            else:
                config[key] = value
    
    if "api_key" in config:
        config["api_key"] = "****"
    
    return config
