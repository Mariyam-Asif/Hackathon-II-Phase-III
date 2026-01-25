import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import Response
from .api.task_routes import router as task_router
from .api.auth_routes import router as auth_router
from .middleware.auth_middleware import AuthMiddleware, RateLimitMiddleware
from .auth.error_handlers import register_auth_error_handlers
from dotenv import load_dotenv
import time
from typing import Callable
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

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
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://localhost:3001",  # Next.js dev server (alternative port)
        "http://127.0.0.1:3001",  # Alternative localhost format
        "http://localhost:8000",  # Allow same origin for direct API access
        "http://127.0.0.1:8000",  # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# 2️⃣ GZip for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3️⃣ Authentication & rate limit
# AuthMiddleware will now skip public routes and OPTIONS
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

# --- Root and health endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo App API with Better Auth Integration"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- Startup event ---
@app.on_event("startup")
def on_startup():
    logger.info("Application starting up...")
    from .database.database import create_db_and_tables
    create_db_and_tables()

# --- Register auth error handlers ---
app = register_auth_error_handlers(app)


# --- Global exception handlers to ensure CORS headers on error responses ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # For OPTIONS requests, return a minimal response without body to comply with CORS spec
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": exc.errors(),
                "message": "Invalid input data provided"
            }
        )

    # Add CORS headers to ensure browser accepts the error response
    origin = request.headers.get("origin", "http://localhost:3000")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*, Authorization"

    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # For OPTIONS requests, return a minimal response without body to comply with CORS spec
    if request.method == "OPTIONS":
        response = Response(status_code=exc.status_code)
    else:
        response = JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP error",
                "detail": exc.detail,
                "status_code": exc.status_code
            }
        )

    # Add CORS headers to ensure browser accepts the error response
    origin = request.headers.get("origin", "http://localhost:3000")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*, Authorization"

    return response
