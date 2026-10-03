"""
Basic CRUD Task API
--------------------
A minimal FastAPI app backed by an in-memory list. No database, no auth —
just enough to practice REST semantics with curl.

Run it:
    pip install fastapi uvicorn --break-system-packages
    uvicorn main:app --reload

Then hit it with curl (see examples at the bottom of this file).
"""


from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

app = FastAPI(title="Task API", version="1.0.0")

# ---------------------------------------------------------------------------
# "Database": just a list of dicts living in memory. Restarting the server
# wipes it. next_id tracks the next free id so we never reuse one, even
# after deletes.
# ---------------------------------------------------------------------------
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write CRUD API", "done": True},
]
next_id = 3


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_blank_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def api_info():
    """Describes the API: name, version, and available endpoints."""
    return {
        "name": "Task API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This description",
            "GET /tasks": "List all tasks",
            "GET /tasks/{id}": "Get a single task by id",
            "POST /tasks": "Create a new task (body: { title })",
            "PUT /tasks/{id}": "Update a task's title and/or done state",
            "DELETE /tasks/{id}": "Delete a task",
        },
    }


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id
    task = {"id": next_id, "title": payload.title.strip(), "done": False}
    tasks.append(task)
    next_id += 1
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of 'title' or 'done' to update",
        )

    if payload.title is not None:
        task["title"] = payload.title.strip()
    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Custom validation error handler so bad request bodies come back as
# clean 400s with a readable message, instead of FastAPI's default 422.
# ---------------------------------------------------------------------------
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
def validation_error_handler(request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    field = ".".join(str(p) for p in first_error["loc"] if p != "body")
    message = first_error["msg"]
    return JSONResponse(
        status_code=400,
        content={"error": f"{field}: {message}" if field else message},
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request, exc: HTTPException):
    # Normalize FastAPI's default {"detail": ...} into {"error": ...}
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# ---------------------------------------------------------------------------
# curl cheat sheet
# ---------------------------------------------------------------------------
# API info:
#   curl http://127.0.0.1:8000/
#
# List tasks:
#   curl http://127.0.0.1:8000/tasks
#
# Get one task:
#   curl http://127.0.0.1:8000/tasks/1
#   curl http://127.0.0.1:8000/tasks/99          # -> 404
#
# Create a task:
#   curl -X POST http://127.0.0.1:8000/tasks \
#        -H "Content-Type: application/json" \
#        -d '{"title": "Buy milk"}'
#
#   curl -X POST http://127.0.0.1:8000/tasks \
#        -H "Content-Type: application/json" \
#        -d '{"title": ""}'                      # -> 400
#
# Update a task:
#   curl -X PUT http://127.0.0.1:8000/tasks/1 \
#        -H "Content-Type: application/json" \
#        -d '{"done": true}'
#
# Delete a task:
#   curl -i -X DELETE http://127.0.0.1:8000/tasks/1   # -> 204, no body