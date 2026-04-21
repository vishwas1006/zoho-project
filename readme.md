# Zoho Project Assistant

A conversational AI chatbot that lets you manage your Zoho Projects using plain English. Built with FastAPI, LangGraph, and Next.js.

You can ask things like "What projects do I have?", "Show me all open tasks", or "Create a task called Fix Login Bug" — and the bot handles it. Write operations like creating, updating, or deleting tasks always pause and ask you to confirm before doing anything.

---

## What it does

- Connects to your Zoho Projects account via OAuth 2.0 — no shared tokens, every user logs in with their own account
- Routes your message to the right agent — a query agent for reading data, an action agent for making changes
- Remembers context within a session (so you can say "show tasks for the first one" after asking about projects)
- Remembers past sessions too — preferences and conversation history are stored in a local database
- Pauses before any write operation and shows you exactly what it's about to do, then waits for your confirmation

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (async) |
| AI Agents | LangGraph + Groq (llama-3.3-70b-versatile) |
| Frontend | Next.js + Tailwind CSS |
| Database | SQLite (via SQLAlchemy async) |
| Auth | Zoho OAuth 2.0 Authorization Code Grant |

---

## Project structure

```
zoho-chatbot/
├── backend/
│   ├── main.py                  # FastAPI routes
│   ├── config.py                # Environment config
│   ├── database.py              # SQLite setup
│   ├── auth/
│   │   └── zoho_oauth.py        # OAuth URL builder and token exchange
│   ├── zoho/
│   │   └── client.py            # Zoho API client with auto token refresh
│   ├── agents/
│   │   ├── graph.py             # LangGraph graph wiring
│   │   ├── router.py            # Routes messages to query or action agent
│   │   ├── query_agent.py       # Read-only agent
│   │   └── action_agent.py      # Write agent with HIL pause
│   ├── tools/
│   │   ├── list_projects.py
│   │   ├── list_tasks.py
│   │   ├── get_task_details.py
│   │   ├── create_task.py
│   │   ├── update_task.py
│   │   ├── delete_task.py
│   │   ├── list_project_members.py
│   │   └── get_task_utilisation.py
│   └── memory/
│       ├── short_term.py        # LangGraph MemorySaver (within session)
│       ├── long_term.py         # DB-backed memory (across sessions)
│       └── pending_actions.py   # Stores HIL actions waiting for confirmation
└── frontend/
    └── pages/
        ├── index.tsx            # Login page
        └── chat.tsx             # Chat interface
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Zoho account with access to Zoho Projects
- A Groq API key (free at console.groq.com)
- A Zoho OAuth client (instructions below)

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/zoho-chatbot.git
cd zoho-chatbot
```

---

### 2. Set up Zoho OAuth

You need to register an OAuth client with Zoho to get a `CLIENT_ID` and `CLIENT_SECRET`.

1. Go to [api-console.zoho.in](https://api-console.zoho.in)
2. Click **Add Client** → choose **Server-based Applications**
3. Fill in:
   - **Client Name**: anything (e.g. Zoho Chatbot)
   - **Homepage URL**: `http://localhost:3000`
   - **Authorized Redirect URIs**: `http://localhost:8000/auth/callback`
4. Click **Create**
5. Copy the **Client ID** and **Client Secret**

---

### 3. Get a Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign in and click **API Keys** in the sidebar
3. Click **Create API Key**, name it anything, copy the key

---

### 4. Configure environment variables

```bash
cd backend
cp .env.example .env
```

Open `.env` and fill in your values:

```
ZOHO_CLIENT_ID=your_client_id_here
ZOHO_CLIENT_SECRET=your_client_secret_here
ZOHO_REDIRECT_URI=http://localhost:8000/auth/callback
GROQ_API_KEY=your_groq_key_here
```

---

### 5. Start the backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

---

### 6. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

---

### 7. Log in and start chatting

1. Open `http://localhost:3000`
2. Click **Login with Zoho**
3. Authenticate with your Zoho account
4. You'll be redirected to the chat page automatically

---

## How it works

### Authentication

Every user logs in with their own Zoho account via the Authorization Code Grant flow. After login, the access token and refresh token are stored in a local SQLite database tied to a session cookie. The token refreshes automatically before any Zoho API call if it has expired.

### Agents

When you send a message, a router reads it and decides which agent should handle it:

- **Query agent** — handles read operations like listing projects, fetching tasks, checking members. It never modifies anything.
- **Action agent** — handles write operations like creating, updating, or deleting tasks. Before executing anything, it pauses and tells you exactly what it's about to do. The operation only proceeds if you click Confirm.

### Memory

- **Short-term**: LangGraph's MemorySaver keeps context within a session. If you ask "what projects do I have?" and then "show tasks for the first one", the bot remembers which project you meant.
- **Long-term**: Every message is saved to the SQLite database. When you log in for a new session, the bot loads a summary of your past conversations so it can reference earlier context.

### Human-in-the-loop

Any write operation — create, update, delete — triggers a confirmation step. The bot shows you exactly what it's about to do and presents Confirm and Cancel buttons. If you cancel, nothing happens and no changes are made to your Zoho account.

---

## Available tools

| Tool | What it does |
|---|---|
| `list_projects` | Fetch all projects for the logged-in user |
| `list_tasks` | List tasks for a project, with filters for status, assignee, and due date |
| `get_task_details` | Fetch full details of a single task by ID |
| `create_task` | Create a new task in a project (requires confirmation) |
| `update_task` | Update task status, assignee, due date, or priority (requires confirmation) |
| `delete_task` | Delete a task (requires confirmation) |
| `list_project_members` | Get all members of a project with their roles |
| `get_task_utilisation` | Summarise task load per member across a project |

---

## Example conversations

```
You: What projects do I have?
Bot: You have one project — Website Redesign (active)

You: Show tasks for that project
Bot: Here are the tasks for Website Redesign:
     1. Design Homepage — Open
     2. Setup Database — Open
     3. API Integration — Open

You: Create a task called Fix Login Bug
Bot: I am about to create a new task called "Fix Login Bug" in Website Redesign.
     Do you confirm?
     [ Confirm ]  [ Cancel ]

You: (clicks Confirm)
Bot: Task 'Fix Login Bug' created successfully.

You: Delete the Design Homepage task
Bot: I am about to delete the task "Design Homepage" from Website Redesign.
     Do you confirm?
     [ Confirm ]  [ Cancel ]

You: (clicks Cancel)
Bot: Action cancelled. Nothing was changed.
```

---

## API endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/auth/login` | Redirects to Zoho login page |
| GET | `/auth/callback` | Handles OAuth callback, saves tokens, redirects to chat |
| GET | `/auth/check` | Validates current session |
| POST | `/chat` | Send a message, get a response |
| POST | `/chat/confirm` | Confirm or cancel a pending action |
| GET | `/` | Health check |

---

## Notes

- This project is built for local development. For production, you would need HTTPS, a proper secret store, and rate limiting.
- The SQLite database (`chatbot.db`) is created automatically on first startup.
- Zoho access tokens expire after 1 hour. The client handles refresh automatically.