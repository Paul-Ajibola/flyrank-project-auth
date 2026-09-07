from contextlib import asynccontextmanager
import os
import json
import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from repo import TaskRepository
from database import init_db

import redis.asyncio as aioredis



DB_FILE = "tasks.db"

# connect to Redis via environment variable (defaults to localhost for local testing)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 60    # Cache expires after 60 seconds


repo = TaskRepository()
redis_client: aioredis.Redis | None = None



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


@app.get("/teaser")
def home():
    return "Hello There! Welcome to my task homepage"


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
    await redis_client.setex(cache_key, CACHE_TIL, json.dumps(tasks))
    return tasks


# Fixed: Added leading slash
@app.get("/tasks/{id}")
async def check_task_state(id: int):
    cache_key = f"task:{id}"

    # 1. check redis
    cached = await redis_client.get(cache_key)
    if cached:
        return json.load(cached)

    # 2. cache miss: fetch from DB
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 3. store in redis
    await redis_client.setex(cache_key, CACHE_TIL, json.dumps(task))
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

