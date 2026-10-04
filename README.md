# Auth & Task Management API

A secure RESTful API built with **FastAPI**, **Supabase Auth**, **Redis**, and **PostgreSQL**.

This project demonstrates how to build an authenticated backend API using Supabase as an **Identity Provider (IdP)**, JWT-based authentication, reusable FastAPI authentication dependencies, Redis caching, and automatically generated Swagger/OpenAPI documentation.

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Architecture](#architecture)
* [Project Structure](#project-structure)
* [Environment Variables](#environment-variables)
* [Installation](#installation)
* [Running the Application](#running-the-application)
* [API Reference](#api-reference)
* [Authentication Flow](#authentication-flow)
* [Protected Routes](#protected-routes)
* [Swagger UI](#swagger-ui)
* [Testing](#testing)
* [Security Notes](#security-notes)
* [Project Status](#project-status)

---

## Overview

This project started as a simple CRUD Task API and was extended to include authentication and route protection.

The application uses **Supabase Auth** to manage users and issue authentication tokens. The FastAPI backend verifies the access token before allowing users to access protected endpoints.

The application also uses Redis as a caching layer for task queries and PostgreSQL as the persistent database.

The main objective is to demonstrate how authentication, authorization, caching, and database persistence can work together in a modern backend application.

---

## Features

### Authentication

* User registration with Supabase Auth
* User login with email and password
* JWT access tokens
* Refresh tokens
* User logout
* Bearer token authentication
* Reusable FastAPI authentication dependency

### Authorization

Protected routes require a valid Supabase access token.

The authentication dependency:

1. Extracts the Bearer token from the request.
2. Sends the token to Supabase for verification.
3. Rejects missing, invalid, or expired tokens.
4. Makes the authenticated user available to the protected route.

### Task Management

The API also provides CRUD operations for tasks:

* Create tasks
* Read all tasks
* Read individual tasks
* Update tasks
* Delete tasks

### Redis Caching

Redis is used to cache task data.

The API caches:

* The complete task list
* Individual tasks

The cache expires after 60 seconds, and task mutations invalidate the relevant cache entries.

### API Documentation

FastAPI automatically generates interactive Swagger UI documentation.

The protected routes use a Bearer authentication scheme, allowing JWTs to be entered through Swagger's **Authorize** button.

---

## Tech Stack

| Technology           | Purpose                            |
| -------------------- | ---------------------------------- |
| Python 3.10+         | Programming language               |
| FastAPI              | Web API framework                  |
| Uvicorn              | ASGI server                        |
| Supabase Auth        | Authentication and user management |
| PostgreSQL           | Persistent task storage            |
| psycopg2             | PostgreSQL database driver         |
| Redis                | Caching                            |
| Pydantic             | Request validation                 |
| python-dotenv        | Environment variable management    |
| Swagger UI / OpenAPI | Interactive API documentation      |

---

## Architecture

The application follows this general flow:

```text
                    ┌─────────────────────┐
                    │       Client        │
                    │ Browser / Swagger   │
                    │ PowerShell / curl   │
                    └──────────┬──────────┘
                               │
                               │
                    Login credentials
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Supabase Auth    │
                    │                     │
                    │ User authentication │
                    │ JWT generation      │
                    └──────────┬──────────┘
                               │
                         Access Token
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI API      │
                    │                     │
                    │ Auth Dependency     │
                    │ Route Handlers      │
                    └──────┬────────┬─────┘
                           │        │
                           │        │
                           ▼        ▼
                    ┌──────────┐  ┌──────────────┐
                    │  Redis   │  │ PostgreSQL   │
                    │  Cache   │  │  Database    │
                    └──────────┘  └──────────────┘
```

### Authentication Flow

```text
Client
  │
  │ email + password
  ▼
Supabase Auth
  │
  │ access_token (JWT)
  ▼
Client
  │
  │ Authorization: Bearer <token>
  ▼
FastAPI
  │
  │ get_current_user()
  ▼
Supabase
  │
  │ token verification
  ▼
Protected Route
  │
  ▼
Response
```

---

## Project Structure

```text
project/
│
├── main.py              # FastAPI application and API routes
├── auth_client.py       # Supabase client configuration
├── database.py          # PostgreSQL connection and database setup
├── repo.py              # Task repository and CRUD operations
│
├── .env                 # Environment variables (DO NOT COMMIT)
├── .gitignore           # Files excluded from Git
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

DATABASE_URL=postgresql://username:password@localhost:5432/database_name

REDIS_URL=redis://localhost:6379/0

PORT=3000
```

### Variable Description

| Variable       | Description                              |
| -------------- | ---------------------------------------- |
| `SUPABASE_URL` | URL of your Supabase project             |
| `SUPABASE_KEY` | Supabase API key used by the application |
| `DATABASE_URL` | PostgreSQL connection string             |
| `REDIS_URL`    | Redis connection URL                     |
| `PORT`         | Port used by the API                     |

### Important

Never commit `.env` to GitHub.

Your `.gitignore` should contain:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

## Installation

### Prerequisites

Make sure the following are installed:

* Python 3.10 or newer
* PostgreSQL
* Redis
* Git
* A Supabase account and project

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise:

```bash
pip install fastapi uvicorn supabase redis psycopg2-binary python-dotenv "pydantic[email]"
```

### 4. Configure environment variables

Create `.env` and provide your Supabase, PostgreSQL, and Redis configuration.

---

## Running the Application

Start the API with:

```bash
uvicorn main:app --reload --port 3000
```

The API should be available at:

```text
http://localhost:3000
```

Interactive Swagger documentation:

```text
http://localhost:3000/docs
```

---

# API Reference

## Public Endpoints

| Method | Endpoint       | Authentication | Description                 |
| ------ | -------------- | -------------- | --------------------------- |
| `GET`  | `/`            | No             | Returns API information     |
| `GET`  | `/health`      | No             | Checks API and Redis health |
| `GET`  | `/public/info` | No             | Returns public information  |

---

## Authentication Endpoints

| Method | Endpoint       | Authentication | Success          |
| ------ | -------------- | -------------- | ---------------- |
| `POST` | `/auth/signup` | No             | `201 Created`    |
| `POST` | `/auth/login`  | No             | `200 OK`         |
| `POST` | `/auth/logout` | Yes            | `204 No Content` |

---

## Protected Endpoints

| Method | Endpoint               | Authentication | Success  |
| ------ | ---------------------- | -------------- | -------- |
| `GET`  | `/protected/profile`   | Bearer JWT     | `200 OK` |
| `GET`  | `/protected/dashboard` | Bearer JWT     | `200 OK` |

---

## Task Endpoints

| Method   | Endpoint      | Authentication | Description      |
| -------- | ------------- | -------------- | ---------------- |
| `GET`    | `/tasks`      | No             | Get all tasks    |
| `GET`    | `/tasks/{id}` | No             | Get a task by ID |
| `POST`   | `/tasks`      | No             | Create a task    |
| `PUT`    | `/tasks/{id}` | No             | Update a task    |
| `DELETE` | `/tasks/{id}` | No             | Delete a task    |

Task reads use Redis caching to reduce repeated database queries.

---

# Authentication Flow

## 1. Sign Up

Send a request to:

```http
POST /auth/signup
```

Request body:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

Supabase creates the user account.

Successful registration returns:

```text
201 Created
```

---

## 2. Login

Send:

```http
POST /auth/login
```

with:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

On successful authentication, Supabase returns an access token and refresh token.

Example response:

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {}
}
```

The `access_token` is the JWT used to access protected endpoints.

---

# Protected Routes

Protected routes require an HTTP Authorization header:

```http
Authorization: Bearer <access_token>
```

The FastAPI authentication dependency is responsible for verifying this token.

Conceptually:

```python
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    user_response = supabase.auth.get_user(token)

    if not user_response or not user_response.user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user_response.user
```

A protected endpoint can then reuse the dependency:

```python
@app.get("/protected/profile")
async def get_protected_profile(
    user=Depends(get_current_user)
):
    return {
        "id": user.id,
        "email": user.email
    }
```

This prevents authentication logic from being duplicated across every protected route.

---

# Logout

The logout endpoint is itself protected:

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

The backend verifies the token and then asks Supabase to terminate the user's session.

Successful logout returns:

```text
204 No Content
```

---

# Swagger UI

FastAPI automatically generates interactive API documentation.

Open:

```text
http://localhost:3000/docs
```

### Using authentication in Swagger

1. Register a user using `/auth/signup`.
2. Log in using `/auth/login`.
3. Copy the returned `access_token`.
4. Click **Authorize** in Swagger UI.
5. Enter the Bearer token.
6. Click **Authorize**.
7. Test the protected endpoints.

The protected routes should display a lock icon.

You can then test:

```text
GET /protected/profile
GET /protected/dashboard
POST /auth/logout
```

directly from Swagger UI.

---

# Testing

## Test 1 — Public Endpoint

```bash
curl.exe -i http://localhost:3000/public/info
```

Expected:

```text
200 OK
```

---

## Test 2 — Protected Endpoint Without Token

```bash
curl.exe -i http://localhost:3000/protected/profile
```

Expected:

```text
401 Unauthorized
```

---

## Test 3 — Register

PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/auth/signup" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"test@example.com","password":"password123"}'
```

Expected:

```text
201 Created
```

---

## Test 4 — Login

```powershell
$response = Invoke-RestMethod `
  -Uri "http://localhost:3000/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"test@example.com","password":"password123"}'

$token = $response.access_token

Write-Output $token
```

Save the returned access token.

---

## Test 5 — Access Protected Profile

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/protected/profile" `
  -Method Get `
  -Headers @{ Authorization = "Bearer $token" }
```

A valid token should return the authenticated user's information.

---

## Test 6 — Access Protected Dashboard

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/protected/dashboard" `
  -Method Get `
  -Headers @{ Authorization = "Bearer $token" }
```

A valid token should allow access.

---

## Test 7 — Invalid Token

Change one character of the token and send the request again:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/protected/profile" `
  -Method Get `
  -Headers @{ Authorization = "Bearer INVALID_TOKEN" }
```

Expected:

```text
401 Unauthorized
```

---

## Test 8 — Logout

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/auth/logout" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" }
```

Expected:

```text
204 No Content
```

---

# Redis Caching

Task retrieval uses Redis to reduce unnecessary database queries.

For the task list, the cache key is:

```text
tasks:all
```

For an individual task:

```text
task:{id}
```

Cached values expire after 60 seconds.

When a task is created, updated, or deleted, the relevant cache entries are invalidated so that subsequent requests retrieve current data from PostgreSQL.

---

# Security Notes

This project demonstrates several important backend security practices:

### 1. Authentication is delegated to Supabase

The application does not implement password hashing or cryptographic token generation itself.

Supabase acts as the Identity Provider responsible for user authentication and token issuance.

### 2. Protected routes verify tokens

Simply checking whether an Authorization header exists is not sufficient.

The backend sends the token to Supabase for verification before granting access.

### 3. Secrets are stored in environment variables

Supabase credentials and database configuration are loaded from `.env` rather than being hard-coded into the source code.

### 4. `.env` must not be committed

Before pushing to GitHub, verify that `.env` is included in `.gitignore`.

---




