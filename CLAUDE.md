# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Software Guard is an internal company software download station with a monorepo structure containing a FastAPI backend and Vue 3 frontend. The application manages software distribution, download tracking, vulnerability notifications, and user access control.

## Development Commands

### Backend (FastAPI)
Located in `backend/` directory. Uses `uv` as the Python package manager.

```bash
cd backend
uv sync                      # Install dependencies
uv run python main.py        # Start development server (http://localhost:8000)
```

### Frontend (Vue 3 + Vite)
Located in `frontend/` directory. Uses `pnpm` as the Node.js package manager.

```bash
cd frontend
pnpm install                 # Install dependencies
pnpm dev                     # Start development server (http://localhost:5173)
pnpm build                   # Build for production
```

## Architecture

### Backend Structure (`backend/app/`)

- **`api/`** - FastAPI route handlers organized by feature:
  - `auth.py` - Authentication endpoints (login, register, token verification)
  - `software.py` - Software CRUD operations and version management
  - `request.py` - Software request workflow (users request software, ops review)
  - `download.py` - Download tracking and statistics
  - `vulnerability.py` - Security vulnerability records for software versions
  - `user.py` - User management
  - `stats.py` - Dashboard statistics

- **`core/`** - Core infrastructure:
  - `config.py` - Pydantic settings with environment variable support (reads from `.env`)
  - `database.py` - SQLAlchemy session management and engine configuration
  - `security.py` - JWT token creation/password hashing (bcrypt)
  - `deps.py` - FastAPI dependency injection for auth/permissions (`require_admin`, `require_ops`)

- **`models/`** - SQLAlchemy ORM models:
  - `user.py` - User with roles (ADMIN, OPS, USER)
  - `software.py` - Software and SoftwareVersion (one-to-many)
  - `request.py` - SoftwareRequest workflow model
  - `download.py` - DownloadLog tracking
  - `vulnerability.py` - Vulnerability records linked to software versions
  - `audit.py` - AuditLog for compliance

- **`schemas/`** - Pydantic models for request/response validation

### Frontend Structure (`frontend/src/`)

- **`api/`** - Axios-based API clients, one per backend route module
- **`stores/`** - Pinia stores for state management (user.js for auth state)
- **`router/`** - Vue Router configuration with auth guards
- **`views/`** - Page components organized by feature:
  - `Login.vue` - Authentication
  - `Layout.vue` - Main app shell with navigation
  - `Software/` - Software browsing and details
  - `Admin/` - Ops/admin dashboard, requests, vulnerabilities, users

### Key Architectural Patterns

**Authentication Flow:**
- Backend uses JWT with `OAuth2PasswordBearer` scheme
- Frontend stores token in Pinia store (`useUserStore`)
- Axios interceptor automatically includes `Authorization: Bearer <token>` header
- Route guards check `userStore.token` and `userStore.isOps()` for admin access

**Permission System:**
- Three roles: USER (default), OPS, ADMIN
- Backend uses `require_ops` dependency for protected endpoints
- Frontend checks `userStore.isOps()` (returns true for both OPS and ADMIN roles)

**Database Setup:**
- Tables auto-created on startup via `Base.metadata.create_all()` in `main.py` lifespan
- Default admin account created on first run (username: `admin`, password: `admin123`)
- Uses PostgreSQL with connection pooling

**File Storage:**
- Software files stored in `backend/storage/` directory
- Configured via `STORAGE_PATH` in settings

## Configuration

### Backend Environment Variables (`backend/.env`)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `STORAGE_PATH` - File storage location

### Frontend Proxy
The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000` (see `vite.config.js`).

## Important Notes

- The project uses Chinese comments and UI text throughout
- CORS is configured for `http://localhost:5173` and `http://localhost:3000`
- File uploads are limited to 1GB with specific allowed extensions (`.exe`, `.msi`, `.zip`, etc.)
- Alembic is installed but migrations are not currently configured (tables use auto-create)
