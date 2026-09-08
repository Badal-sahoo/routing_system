# Fleet Dispatch System

A graph-based fleet dispatch system: agents move around a graph of nodes/edges,
tasks get created between an origin and destination, and a Celery worker runs
Dijkstra's algorithm to assign each task to the nearest available agent. Agent
GPS pings land in Redis (not the relational DB) and get pushed to connected
clients live over WebSocket.

## Architecture

```
React (Vite)  <--REST-->  Django + DRF  <--select_for_update-->  PostgreSQL
     |                         |
     |<--WebSocket (Channels)--+--> Redis (GPS cache, Celery broker, channel layer)
                                |
                          Celery worker --runs--> Dijkstra --assigns--> Agent
```

- **Django + DRF** — REST API for nodes/edges/agents/tasks, plus a dedicated
  high-frequency GPS ingestion endpoint. JWT-protected (see Authentication).
- **Redis** — three separate concerns on three DB indices: GPS cache (`db 1`),
  Celery broker/result backend (`db 0`), Channels layer (`db 2`).
- **Celery** — runs the Dijkstra dispatch job asynchronously off the request path.
- **Channels (ASGI, served by Uvicorn)** — pushes live GPS, rider and task
  updates to WebSocket clients. Each message carries a `kind` (`gps` / `agent` / `task`).
- **React** — renders the graph (via `reagraph`), agent list, and task list, live,
  behind a login screen.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Django 6, Django REST Framework, Celery, Django Channels, django-redis |
| Config | django-environ (`.env` files, one per side) |
| Auth | djangorestframework-simplejwt (JWT access/refresh tokens) |
| Async server | Uvicorn (ASGI) |
| Database | PostgreSQL (SQLite fallback if `DB_NAME` is unset) |
| Cache / broker / channel layer | Redis |
| Frontend | React (Vite), reagraph, Zustand, Axios |

## Project structure

```
backend/
  config/
    settings/{base,development}.py
    celery.py          # Celery app instance
    asgi.py            # ProtocolTypeRouter: HTTP + WebSocket
    urls.py
  apps/                # one app per concern; each owns its own
                       # models / services / serializers / views / urls
    graph/              # Node, Edge          + build_adjacency()
    agents/             # Agent               + GPS ingestion, Redis live state
    tasks/              # Task                + assign_task_to_agent() (the locking write)
    routing/            # no models           + Dijkstra, dispatch job, dispatch endpoint
  consumers/
    location_consumer.py  # WebSocket consumer, broadcasts to "fleet_updates"
frontend/
  src/
    App.jsx                  # logged in? Dashboard : LoginPage
    Dashboard.jsx            # layout; the one place that decides when data loads
    lib/
      config.js              # every value that comes from VITE_* env vars
      tokenStorage.js        # JWT tokens in localStorage + change notifications
      apiClient.js           # THE axios instance: attaches JWT, refreshes on 401
      apiError.js            # DRF error -> one readable line
    features/                # one folder per feature, three files each:
      auth/     auth.api.js     auth.hooks.js     LoginPage.jsx
      graph/    graph.api.js    graph.hooks.js    GraphView.jsx
      agents/   agents.api.js   agents.hooks.js   AgentPanel.jsx
      tasks/    tasks.api.js    tasks.hooks.js    TaskPanel.jsx
      fleet/    fleet.socket.js fleet.hooks.js    (no JSX: it's a connection)
```

`*.api.js` holds every HTTP call a feature makes, `*.hooks.js` holds its store
and hooks, and the `.jsx` file is presentation only. Auth is handled once, in
`lib/apiClient.js` — no feature file mentions a token.

## Prerequisites

- Python 3.13, Node 18+, Redis (`brew install redis` on macOS)
- No Docker required — everything runs as local processes.

## Setup

```bash
# Backend
cd backend
cp .env.example .env          # then set DJANGO_SECRET_KEY
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate

# Create a user to log in with (the frontend requires a login)
./venv/bin/python manage.py createsuperuser

# Frontend
cd ../frontend
cp .env.example .env          # points at localhost:8000 by default
npm install
```

Both `.env` files are gitignored; the `.env.example` templates next to them
list every variable with a comment. `DJANGO_SECRET_KEY` is required — Django
will refuse to start without it, on purpose.

## Running locally

Four processes, four terminals, all from the project root unless noted:

```bash
# 1. Redis
redis-server

# 2. Celery worker (from backend/)
cd backend && ./venv/bin/celery -A config worker -l info

# 3. Django (from backend/) -- served by Uvicorn (ASGI), HTTP + WebSocket on one port
cd backend && ./venv/bin/uvicorn config.asgi:application --reload

# 4. Frontend (from frontend/)
cd frontend && npm run dev
```

Then open **http://localhost:5173**.

## API

| Endpoint | Auth | Notes |
|---|---|---|
| `POST /api/token/` | — | Login: `{username, password}` &rarr; `{access, refresh}` |
| `POST /api/token/refresh/` | — | `{refresh}` &rarr; new `{access}` |
| `GET /api/nodes/`, `/api/edges/` | JWT, read-only | Graph structure — created via `seed_city` or the admin |
| `GET /api/agents/` | JWT, read-only | Includes `live_location` (merged from Redis) |
| `GET/POST /api/tasks/` | JWT | Create with `origin_node_fk` / `destination_node_fk` |
| `POST /api/tasks/{id}/dispatch/` | JWT | Queues the Celery dispatch job, returns `202` |
| `POST /api/agents/{id}/location/` | open | GPS ping, writes to Redis, 30s TTL, rate-limited (10/10s) |
| `ws://127.0.0.1:8000/ws/fleet/` | open | Live GPS broadcast |

Nodes, edges and agents are read-only over the API: they're built once
(`seed_city`, or by hand in `/admin/`), not written by a logged-in client.
Tasks are the one resource created and dispatched live, so that endpoint
stays full CRUD.

## Authentication

JWT via `djangorestframework-simplejwt`. Every endpoint requires a valid
access token **except** the GPS ping and the WebSocket — those are
device/agent-facing, not a logged-in dispatcher, so "log in" doesn't apply
the same way (see `AgentLocationView`'s docstring for the reasoning).

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "..."}'
# -> {"access": "...", "refresh": "..."}

curl http://127.0.0.1:8000/api/nodes/ -H "Authorization: Bearer <access>"
```

- Access tokens last 30 minutes, refresh tokens last 1 day (`SIMPLE_JWT` in
  `config/settings/base.py`).
- The frontend stores both in `localStorage`, attaches the access token to
  every request via an Axios interceptor, and — if a request comes back
  `401` — transparently calls `/api/token/refresh/`, retries the original
  request once, and only drops back to the login screen if the refresh
  itself fails.

## How dispatch works

1. `POST /api/tasks/` creates a task (`status: pending`).
2. `POST /api/tasks/{id}/dispatch/` enqueues `apps.routing.tasks.dispatch_task`
   and returns immediately (`202`) with a Celery task id.
3. The worker builds an adjacency list from the `Edge` table, runs Dijkstra
   from the task's origin node, and finds the *available* Agent with the
   shortest graph distance to it.
4. The actual assignment goes through `assign_task_to_agent()`
   (`apps/tasks/services.py`), which locks the Agent *and* Task rows with
   `select_for_update()` inside a transaction — safe even if two dispatch
   attempts race for the same agent, and re-dispatching an already-assigned
   task can't claim a second agent.
5. A few seconds later the rider sets off (`pending` → `assigned` →
   `in_progress`). The worker drives them along the route — collect, then
   deliver — reporting a GPS position every tick, and on arrival marks the
   task `completed`, frees the rider, and moves them to the destination node
   so the next dispatch routes from there.

Every step above is pushed to connected dashboards over WebSocket, so a
delivery can be watched start to finish without refreshing.

## Known limitations

- **GPS ingestion has no auth and doesn't verify the agent exists** in the
  DB — both deliberate for now. Closing this properly means per-device
  credentials (an API key per Agent), which is a separate design decision
  from user login; see `AgentLocationView`'s docstring.
- **No registration flow.** Users are created via `createsuperuser` /
  Django admin, not self-service signup — not in scope for this project.

