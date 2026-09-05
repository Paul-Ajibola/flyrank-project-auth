# Task API

A simple CRUD (Create, Read, Update, Delete) REST API for managing tasks, built with **FastAPI**.

## Features

- ✅ List all tasks
- ✅ Retrieve a single task by ID
- ✅ Create a new task
- ✅ Update an existing task
- ✅ Delete a task
- ✅ Health check endpoint

## Tech Stack

- [Python 3.9+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/) (ASGI server)

## Getting Started

### Prerequisites

Make sure you have Python 3.9 or higher installed.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

### Running the App

Start the development server with:

```bash
uvicorn main:app --reload
```

> Replace `main` with the name of your Python file if it's different.

The API will be available at `http://127.0.0.1:8000`.

Interactive API docs (Swagger UI) are automatically available at:
`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint      | Description                     |
|--------|---------------|----------------------------------|
| GET    | `/`           | Describes the API and lists endpoints |
| GET    | `/tester`     | Simple welcome message           |
| GET    | `/health`     | Health check                     |
| GET    | `/tasks`      | List all tasks                   |
| GET    | `/tasks/{id}` | Get a single task by ID           |
| POST   | `/tasks`      | Create a new task                |
| PUT    | `/tasks/{id}` | Update a task by ID              |
| DELETE | `/tasks/{id}` | Delete a task by ID              |

### Example Request Bodies

**Create a task** — `POST /tasks`
```json
{
  "title": "walk the dog"
}
```

**Update a task** — `PUT /tasks/{id}?title=new+title`

> Note: the current implementation of `update_task` expects `title` as a **query parameter**, not a JSON body.

## Example Task Object

```json
{
  "id": 1,
  "title": "throw out the trash",
  "done": false
}
```

## Notes

- Data is currently stored **in memory** (a Python list), so all tasks will reset whenever the server restarts. This project is intended for learning/demo purposes.
- For persistent storage, consider integrating a database such as SQLite, PostgreSQL, or MongoDB.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or issue.