# SmartTask AI

> AI-powered task management application built with React, FastAPI, MongoDB, and OpenRouter.

SmartTask AI is a clean, modern, full-stack productivity web application designed to demonstrate robust full-stack architecture, REST API design, Pydantic data validation, NoSQL persistence with MongoDB, interactive React component architecture with Axios, and a controlled AI prioritization workflow using OpenRouter.

---

## 🏗️ Architecture Overview

```
Frontend (React + Vite)
      │
      ▼  (HTTP / JSON via Axios)
Backend (FastAPI REST API)
      │
      ├── MongoDB (CRUD Persistence)
      │
      └── OpenRouter API (Structured Prioritization & Recommendations)
```

### Application Flow

1. **Task Management (CRUD):**
   - **React Components** (`TaskForm`, `TaskList`, `TaskItem`, `Dashboard`) manage state and dispatch asynchronous requests via `src/services/api.js`.
   - **FastAPI Router** validates incoming payloads against **Pydantic schemas** (`TaskCreate`, `TaskUpdate`).
   - **Database Layer** connects to **MongoDB** via `pymongo` to perform CRUD operations on the `tasks` collection.
   - Responses are serialized into standard `TaskResponse` JSON with MongoDB `_id` converted to clean string `id`.

2. **AI Prioritization Workflow:**
   - The user clicks **"Summarize My Tasks"** in the UI.
   - The frontend sends current active tasks to `POST /api/ai/summarize`.
   - The FastAPI backend forwards the tasks to a dedicated backend **AI Service** (`ai_service.py`).
   - OpenRouter processes the task items and returns structured JSON containing:
     - Executive summary
     - Highest-priority bottleneck items
     - Recommended execution order
     - Actionable strategic productivity recommendation
   - **Security Guarantee:** The OpenRouter API key resides exclusively in `backend/.env` and is **never** exposed to the client browser or in API responses.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.14, FastAPI, Uvicorn, Pydantic v2, PyMongo, HTTPX, python-dotenv |
| **Database** | MongoDB (v7.0+) |
| **Frontend** | React 19, Vite, Axios, Plain CSS (Custom Design System with Glassmorphism & Dark Mode) |

---

## 📂 Project Structure

```
smart-task-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application & CORS setup
│   │   ├── database.py           # MongoDB connection lifecycle & health check
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── task.py           # TaskPriority & TaskStatus Enums
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── task.py           # Pydantic schemas (TaskCreate, TaskUpdate, etc.)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py          # CRUD REST endpoints (/api/tasks)
│   │   │   └── ai.py             # AI prioritization endpoint (/api/ai/summarize)
│   │   └── services/
│   │       ├── __init__.py
│   │       └── ai_service.py     # OpenRouter API integration & prompt engineering
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Template for backend environment variables
│   └── .gitignore                # Backend ignore rules
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskForm.jsx      # Task creation form
│   │   │   ├── TaskList.jsx      # Filterable task list container
│   │   │   └── TaskItem.jsx      # Individual task card with status & edit actions
│   │   ├── pages/
│   │   │   └── Dashboard.jsx     # Main view integrating form, list, and AI section
│   │   ├── services/
│   │   │   └── api.js            # Centralized Axios API client
│   │   ├── App.jsx               # Root React component
│   │   ├── main.jsx              # React DOM entry point
│   │   └── index.css             # Theme, design tokens, and modern styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── README.md                     # Comprehensive project documentation
├── .env.example                  # Root environment variables reference
└── .gitignore                    # Global repository ignore rules
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Set your configuration values inside `backend/.env`:

```ini
# MongoDB Connection String (Local or MongoDB Atlas)
MONGODB_URL=mongodb://localhost:27017/smart_task_ai

# OpenRouter API Key (Required for AI task prioritization)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenRouter Model (Configured for Gemini via OpenRouter)
OPENROUTER_MODEL=google/gemini-2.5-flash

# Backend Port (Defaults to 8000)
PORT=8000
```

> **Security Note:** Never commit `.env` files to source control. The `.gitignore` files are preconfigured to ignore `.env` files.

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10+ (tested on Python 3.14)
- **Node.js**: v18+ (tested on Node.js v22)
- **npm**: v9+
- **MongoDB**: A running MongoDB instance locally (`mongodb://localhost:27017`) or a free cloud cluster from [MongoDB Atlas](https://www.mongodb.com/atlas).
- **OpenRouter API Key**: An API key from [OpenRouter](https://openrouter.ai/).

---

### Step 1: Start MongoDB

Ensure MongoDB is running locally:

```bash
# Verify MongoDB is running on port 27017
nc -zv localhost 27017
```

*Or use your MongoDB Atlas connection string in `backend/.env`.*

---

### Step 2: Set Up and Run the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify your environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URL and OpenRouter API Key
   ```

5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. Open interactive API docs:
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Step 3: Set Up and Run the Frontend

1. In a new terminal tab, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser:
   - **App URL**: [http://localhost:5173](http://localhost:5173)

---

## 📡 REST API Documentation

| Method | Endpoint | Status Codes | Description |
|---|---|---|---|
| `GET` | `/health` | `200 OK` | Check API and MongoDB connection status |
| `POST` | `/api/tasks` | `201 Created`, `422` | Create a new task (validated by Pydantic) |
| `GET` | `/api/tasks` | `200 OK`, `500` | Fetch all tasks ordered by creation date |
| `GET` | `/api/tasks/{task_id}` | `200 OK`, `400`, `404` | Fetch a single task by MongoDB ObjectId |
| `PUT` | `/api/tasks/{task_id}` | `200 OK`, `400`, `404` | Update title, description, priority, or status |
| `DELETE` | `/api/tasks/{task_id}` | `204 No Content`, `400`, `404` | Delete a task by ObjectId |
| `POST` | `/api/ai/summarize` | `200 OK`, `503`, `502`, `429` | Send tasks to OpenRouter for executive analysis |

---

## 🧪 Testing & Verification

### Automated Backend Verification

You can verify the backend endpoints and validation rules using Python:

```bash
backend/.venv/bin/python -c "
import httpx
res = httpx.get('http://localhost:8000/health')
print('Backend Health:', res.json())
"
```

### Manual Verification Workflow

1. **Create Task:** Enter title `"Prepare DBMS presentation"`, select Priority `"HIGH"`, click **Create Task**.
2. **Read Tasks:** Observe the task card render immediately in the task list.
3. **Update Status:** Change status from `"To Do"` to `"In Progress"` using the dropdown; note persistence in MongoDB.
4. **Edit Details:** Click **Edit**, update details, and save.
5. **AI Prioritization:** Click **"Summarize My Tasks"**; view the structured AI executive summary and recommended order.
6. **Delete Task:** Click **Delete**, accept the confirmation prompt, and verify removal from the database.
