from contextlib import asynccontextmanager
import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from repo import TaskRepository
from database import init_db


DB_FILE = "tasks.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CRUD App",
    version="1.0",
    description="A simple CRUD Task API",
    lifespan=lifespan,
)

repo = TaskRepository()

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
def get_health():
    return {"status": "ok"}


@app.get("/tasks")
def check_task():
    repo.get_all()


# Fixed: Added leading slash
@app.get("/tasks/{id}")
def check_task_state(id: int):
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def new_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return repo.create(payload.title)


# Fixed: Swapped RequestBody for TaskCreate (or TaskUpdate if supporting partial updates)
@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    updated = repo.update(task_id, payload.title, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated
    

@app.delete("/tasks/{id}")
def delete_task(id: int):
    success = repo.delete(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

