from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import sqlite3


DB_FILE = "tasks.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()


    # create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # insert sample tasks only if table is empty
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]

    if count == 0:
        sample_tasks = [
            ("remove trash", False),
            ("wash cloth", False),
            ("polish shoes", False),
        ]
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            sample_tasks
        )
        conn.commit()

    conn.close()

    yield     # app runs; doesn't shutdown



app = FastAPI(
    title="CRUD App",
    version="1.0",
    description="A simple CRUD Task API",
    lifespan=lifespan
)



# 1. Pydantic request body schema
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be blank")

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# 2. In-memory data store
tasks = [
    {"id": 1, "title": "remove trash", "done": False},
    {"id": 2, "title": "wash cloth", "done": False},
    {"id": 3, "title": "polish shoes", "done": False}
]


@app.get("/teaser")
def home():
    return "Hello There! Welcome to my task homepage"


@app.get("/")
def describe_api():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/tasks")
def get_all_tasks():
    return tasks


# Note the leading '/' added to the path
@app.get("/tasks/{id}")
def check_task_state(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {id} not found")


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def new_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    # Dedented outside the if block so this code actually runs
    new_id = max((task["id"] for task in tasks), default=0) + 1
    created_task = {
        "id": new_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks.append(created_task)
    return created_task


@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    target_task = next((task for task in tasks if task["id"] == id), None)
    if not target_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        target_task["title"] = payload.title.strip()

    if payload.done is not None:
        target_task["done"] = payload.done

    return target_task


# Note the leading '/' added to the path
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    target_task = next((task for task in tasks if task["id"] == id), None)
    if not target_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
    tasks.remove(target_task)
    return None

