from fastapi import FastAPI

app = FastAPI(title="CRUD App", version="1.0", description="A simple CRUD Task API")

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


@app.get("tasks/{id}")
def check_task_state(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def new_task(payload: RequestBody):
    if not payload.title.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Title cannot be empty"}
        )

        new_id = max((task["id"] for task in tasks), default=0) + 1

        new_task = {
            "id": new_id,
            "title": payload.title,
            "done": False
        }

        tasks.append(new_task)

        return new_task


@app.put("/tasks/{id}")
def update_task(id: int, payload: RequestBody):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})

        for task in tasks:
            if task["id"] == id:
                task["title"] = payload.title
                task["done"] = True
                return task

        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )



@app.delete("tasks/{id}")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return {"message": "Task successfully removed!"}

    
    raise HTTPException(
        status_code=404,
        detail={"error": "Unknown task"}
    )