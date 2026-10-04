from contextlib import asynccontextmanager
import os
import json
import sqlite3
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from pydantic import BaseModel, Field, EmailStr
from repo import TaskRepository
from database import init_db
from auth_client import supabase
from typing import Optional

import redis.asyncio as aioredis

DB_FILE = "tasks.db"

# connect to Redis via environment variable (defaults to localhost for local testing)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 60    # Cache expires after 60 seconds


repo = TaskRepository()
redis_client: aioredis.Redis | None = None


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup check
#     print("Server runnning and connected to Supabase")
#     yield


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # initialize asynchronous Redis connection pool
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    yield
    # clean up connection on shutdown
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="CRUD App",
    version="1.0",
    description="A simple CRUD Task API",
    lifespan=lifespan,
)



class TaskCreate(BaseModel):
    title: str = Field(
        ..., min_length=1, description="Task title cannot be blank"
    )


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


class AuthPayload(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")




@app.get("/")
def describe_api():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def get_health():
    # verify both API and redis are responding
    redis_ok = await redis_client.ping() if redis_client else False
    return {"status": "ok", "redis": redis_ok}


@app.get("/tasks")
async def check_task():
    cache_key = "tasks:all"
    
    # 1. check redis
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. cache miss: fetch from DB
    tasks = repo.get_all()

    # 3. store in redis
    await redis_client.setex(cache_key, CACHE_TTL, json.dumps(tasks))
    return tasks


# Fixed: Added leading slash
@app.get("/tasks/{id}")
async def check_task_state(id: int):
    cache_key = f"task:{id}"

    # 1. check redis
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. cache miss: fetch from DB
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 3. store in redis
    await redis_client.setex(cache_key, CACHE_TTL, json.dumps(task))
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def new_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    created = repo.create(payload.title)
    
    # invalidate list cache so new tasks show up immediately
    await redis_client.delete("tasks.all")
    return created


# Fixed: Swapped RequestBody for TaskCreate (or TaskUpdate if supporting partial updates)
@app.put("/tasks/{id}")
async def update_task(id: int, payload: TaskUpdate):
    updated = repo.update(task_id, payload.title, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await redis_client.delete(f"task:{id}", "tasks:all")
    return updated
    

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    success = repo.delete(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    # invalidate both the individual task cache and the list cache
    await redis_client.delete(f"task:{id}", "tasks:all")
    return None



# --- Auth Routes ----
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: AuthPayload):
    # input validation
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    try:
        # call Supabase Auth sign_up
        response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed"
            )

        return {
            "message": "User created successfully",
            "user": response.user
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/auth/login", status_code=status.HTTP_200_OK)
async def login(payload: AuthPayload):
    # input validation
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and passwords are required"
        )

    try:
        # call supbase Auth sign_in_with_password
        response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": response.user
        }
    except Exception:
        # catch authentication errors and map to 401 unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )



# the public endpoint
@app.get("/public/info", status_code=status.HTTP_200_OK)
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}


# protected endpoint
@app.get("/protected/profile", status_code=status.HTTP_401_UNAUTHORIZED)
def get_protected_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"}
        )

    token = authorization.split("Bearer ")[1].strip()
    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"}
        )

    return {"message": "Access granted to profile"}




# ====================================================================
#               Protected endpoints using Dependency Injection
# =====================================================================


# create HTTPBearer instance and get_current_user function
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Intercept requests, extracts the JWT, verifies it with Supabase
    via supabase.auth.get_user(token) and returns user metadata.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )

    try:
        # verify token with Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_AUTHORIZED,
                detail="Invalide or expired token"
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@app.get("/protected/profile", status_code=status.HTTP_200_OK)
async def get_protected_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }


@app.get("/protected/dashboard", status_code=status.HTTP_200_OK)
async def get_protected_profile(current_user=Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {current_user.email}!"}


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # terminate session with Supabase
        supabase.auth.sing_out(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"logout failed: {str(e)}"
        )
    return None

