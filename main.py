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
# tasks = [
#     {"id": 1, "title": "remove trash", "done": False},
#     {"id": 2, "title": "wash cloth", "done": False},
#     {"id": 3, "title": "polish shoes", "done": False}
# ]


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
def check_task():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    return [
        {"id": row["id"], "title": row["title"], "done": bool[row["done"]]}
        for row in rows
    ]



@app.get("tasks/{id}")
def check_task_state(id: int):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()

    if row in None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {id} not found"}
        )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}



@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def new_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (payload.title, False)
    )
    conn.commit()

    new_id = cur.lastrowid    # the id SQLite just assigned via AUTOINCREMENT

    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    conn.close()

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}



@app.put("/tasks/{id}")
def update_task(id: int, payload: RequestBody):
    if not payload.title.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    existing = cur.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )

    cur.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (payload.title, True, id)
    )
    conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}



# Note the leading '/' added to the path
@app.delete("/tasks/{id}")
def delete_task(id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    existing = cur.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail={"error": "Unknown task"}
        )

    cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {"message": "Task successfully removed!"}


