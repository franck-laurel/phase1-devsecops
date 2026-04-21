# Phase 1 & 2 — DevSecOps Lab

A hands-on DevSecOps lab demonstrating a containerized 2-tier web application deployed on Kubernetes, with a CI/CD pipeline and security hardening controls.

---

## Architecture

```
User (browser)
     │
     ▼
[Frontend :5001]  ──HTTP──►  [Backend :5000]  ──SQLite──►  database.db
```

Both services run as separate containers in a Kubernetes `lab` namespace.

---

## Project Structure

```
.
├── backend/
│   ├── app.py               # Flask REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_app.py      # pytest unit tests
├── frontend/
│   ├── app.py               # Flask web UI
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
├── deny-all.yaml            # NetworkPolicy: default deny all
├── role.yaml                # RBAC Role (least privilege)
├── rolebinding.yaml         # RBAC RoleBinding
├── api-tester.yaml          # curl pod for in-cluster testing
├── dvwa.yaml                # DVWA vulnerable app (attack target)
└── .github/
    └── workflows/
        └── ci.yml           # GitHub Actions CI pipeline
```

---

## Services

### Backend (`backend/app.py`)

A Flask REST API exposing three endpoints:

| Route | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/users` | GET | List all users |
| `/users` | POST | Create a user (`name` + `email` required) |

Uses **SQLite** for persistence. Parameterized queries protect against SQL injection.

Configuration via environment variables:

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `database.db` | Path to the SQLite database |
| `APP_PORT` | `5000` | Listening port |
| `LOG_LEVEL` | `INFO` | Logging level |

### Frontend (`frontend/app.py`)

A Flask web UI that:
- Displays the list of users by calling `GET /users` on the backend
- Provides an HTML form to add a new user via `POST /users` on the backend

Configuration via environment variables:

| Variable | Default | Description |
|---|---|---|
| `API_URL` | `http://127.0.0.1:5000` | Backend base URL |
| `APP_PORT` | `5001` | Listening port |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## CI/CD Pipeline

Triggered on every push or pull request to `main`.

**Job 1 — `test-backend`**
- Sets up Python 3.11
- Installs dependencies
- Runs `pytest`

**Job 2 — `build-and-push`** *(runs only if tests pass)*
- Logs into GitHub Container Registry (GHCR)
- Builds and pushes both Docker images with tags `latest` and `phase2-ci`

Images are published to:
- `ghcr.io/franck-laurel/phase1-devsecops/backend`
- `ghcr.io/franck-laurel/phase1-devsecops/frontend`

---

## Kubernetes Deployment

All resources are deployed in the `lab` namespace.

```bash
# Deploy the application
kubectl apply -f k8s/

# Apply security policies
kubectl apply -f deny-all.yaml
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml
```

---

## Security Controls

### NetworkPolicy — `deny-all.yaml`

Applies a **default-deny-all** policy to the entire `lab` namespace, blocking all ingress and egress traffic unless explicitly permitted. This enforces a zero-trust baseline.

### RBAC — `role.yaml` / `rolebinding.yaml`

- The `app2-role` Role grants **read-only** access to pods (`get`, `list`) — least privilege
- The `app2-binding` RoleBinding assigns this role to the `app2-sa` ServiceAccount

### DVWA — `dvwa.yaml`

Deploys [DVWA (Damn Vulnerable Web App)](https://github.com/digininja/DVWA) as an intentionally vulnerable target for attack simulation and practice. Service account token automounting is disabled (`automountServiceAccountToken: false`).

### API Tester — `api-tester.yaml`

A `curl`-based pod that runs for 1 hour inside the cluster. Used to simulate an attacker or test network policies and API reachability from within the `lab` namespace.

```bash
# Exec into the tester pod
kubectl exec -it api-tester -n lab -- sh
```

---

## Running Tests Locally

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

---

## Learning Objectives

This lab covers:

1. **Containerization** — Dockerizing a Python Flask application
2. **CI/CD with security gates** — Tests must pass before images are built and pushed
3. **Kubernetes hardening** — NetworkPolicy, RBAC least-privilege, disabled token automounting
4. **Offensive/defensive practice** — DVWA as attack target, `api-tester` as in-cluster attacker simulation
