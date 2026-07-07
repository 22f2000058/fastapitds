from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from pydantic import BaseModel
import jwt
from jwt import PyJWTError

app = FastAPI(title="TDS JWT Verifier")

# CORS (same as before)
ALLOWED_ORIGIN = "https://dash-u91np4.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
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

# === ASSIGNED VALUES ===
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
            options={
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            }
        )
        
        return {
            "valid": True,
            "email": decoded.get("email"),
            "sub": decoded.get("sub"),
            "aud": decoded.get("aud")
        }
        
    except Exception:
        raise HTTPException(status_code=401, detail={"valid": False})
