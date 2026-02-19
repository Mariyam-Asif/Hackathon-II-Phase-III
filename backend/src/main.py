import logging
import os
import sys
import time
from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Path Configuration ---
# Add the 'src' directory to sys.path to allow absolute imports
# This is crucial for Hugging Face Spaces and other deployment environments
current_file_path = os.path.abspath(__file__)
src_dir = os.path.dirname(current_file_path)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# --- Imports ---
# Use absolute imports from the 'src' directory
try:
    from api.task_routes import router as task_router
    from api.auth_routes import router as auth_router
    from api.chat_routes import router as chat_router
    from api.v1.agents import router as agents_router
    from api.health_routes import router as health_router
    from middleware.auth_middleware import AuthMiddleware, RateLimitMiddleware
    from auth.error_handlers import register_auth_error_handlers
except ImportError as e:
    # Log the error for debugging
    print(f"Import Error: {e}")
    # Fallback to relative imports if absolute fails (unlikely given sys.path change)
    from .api.task_routes import router as task_router
    from .api.auth_routes import router as auth_router
    from .api.chat_routes import router as chat_router
    from .api.v1.agents import router as agents_router
    from .api.health_routes import router as health_router
    from .middleware.auth_middleware import AuthMiddleware, RateLimitMiddleware
    from .auth.error_handlers import register_auth_error_handlers

# Set up logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Todo App API",
    description="Todo App Backend with Better Auth Integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Middleware ---

# 1️⃣ CORS middleware: must be FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackathon-ii-phase-iii-giaic.vercel.app",
        "https://giaic-hackathon-ii-phase-ii.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ GZip for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3️⃣ Authentication & rate limit
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)

# --- Security headers ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# --- Request logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {response.status_code} in {time.time() - start_time:.2f}s")
    return response

# --- Routers ---
app.include_router(auth_router, prefix="", tags=["authentication"])
app.include_router(task_router, prefix="/api/{user_id}", tags=["tasks"])
app.include_router(chat_router, prefix="", tags=["chat"])
app.include_router(agents_router, prefix="", tags=["agents"])
app.include_router(health_router, prefix="", tags=["health"])

# Register error handlers
register_auth_error_handlers(app)

# --- Root and health endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo App API with Better Auth Integration"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Global error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )
