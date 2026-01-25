# Implementation Plan: Frontend UI and API Integration for Todo Web Application

## Technical Context

**Feature**: Frontend UI and API Integration for Todo Web Application
**Branch**: 1-frontend-todo-integration
**Framework**: Next.js 16+ with App Router
**Authentication**: Better Auth with JWT tokens
**Backend**: FastAPI with SQLModel ORM
**Database**: Neon Serverless PostgreSQL

**Unknowns needing clarification**:
- Page and component structure for task workflows: NEEDS CLARIFICATION
- Strategy for handling loading, error, and empty states: NEEDS CLARIFICATION
- JWT storage method on frontend (e.g., Better Auth session access): NEEDS CLARIFICATION
- Redirect behavior for unauthenticated users accessing protected routes: NEEDS CLARIFICATION

## Constitution Check

Based on `.specify/memory/constitution.md`, this plan must align with:

- **Progressive Enhancement**: Start with basic functionality and enhance with advanced features
- **Simplicity First**: Implement the simplest solution that works, then add complexity only when needed
- **Separation of Concerns**: Keep UI, authentication, and data concerns separate
- **Production Mindset**: Build with production requirements in mind from the start
- **Extensibility**: Design to accommodate future features

**Gates**:
- [ ] All architectural decisions support progressive enhancement
- [ ] Minimal viable solution designed first
- [ ] Clear separation between UI, auth, and data layers
- [ ] Production readiness considerations included
- [ ] Extensibility patterns implemented

## Phase 0: Outline & Research

### Research Tasks

1. **Page and component structure research**
2. **State management strategy research**
3. **JWT storage mechanism research**
4. **Authentication flow and redirect patterns research**

### Research Findings

#### Decision: Page and Component Structure
- **Rationale**: Next.js App Router convention with protected routes pattern
- **Structure**:
  - `/` - Landing page (public)
  - `/auth/login` - Login page (public)
  - `/auth/register` - Registration page (public)
  - `/dashboard` - Protected dashboard (requires auth)
  - `/tasks` - Protected task list (requires auth)
  - `/tasks/[id]` - Protected task detail (requires auth)

#### Decision: State Management Strategy
- **Rationale**: Leverage Better Auth's built-in session management with React Context for additional app state
- **Strategy**:
  - Use Better Auth hooks for authentication state
  - Implement React Context for task state management
  - Handle loading, error, and empty states with dedicated components

#### Decision: JWT Storage Method
- **Rationale**: Better Auth manages JWT tokens automatically in cookies, but we can access tokens via their API
- **Method**:
  - Let Better Auth handle token storage and refresh
  - Access token via `useAuth()` hook when needed for API calls
  - Implement automatic token injection in API client

#### Decision: Redirect Behavior
- **Rationale**: Standard protected route pattern with Next.js middleware
- **Behavior**:
  - Middleware checks authentication status
  - Unauthenticated users redirected to `/auth/login`
  - Redirect URL preserved in query param for post-login redirect

## Phase 1: Design & Contracts

### Data Model

Based on the functional requirements, the frontend will work with these entities:

#### Task Entity
- `id`: Unique identifier
- `title`: String, required
- `description`: String, optional
- `completed`: Boolean, default false
- `userId`: Foreign key to User
- `createdAt`: Timestamp
- `updatedAt`: Timestamp

#### User Entity (handled by Better Auth)
- `id`: Unique identifier
- `email`: String, required, unique
- `name`: String, optional

### API Contracts

Based on functional requirements, the frontend will consume these API endpoints:

#### Authentication Endpoints (handled by Better Auth)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

#### Task Management Endpoints (handled by FastAPI backend)
- `GET /api/{user_id}/tasks` - Get user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Mark task as complete

### Quickstart Guide

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (API URLs, auth secrets)
4. Run development server: `npm run dev`
5. Access the application at `http://localhost:3000`

## Phase 2: Architecture & Components

### Frontend Architecture

#### Directory Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (landing)
│   ├── auth/
│   │   ├── layout.tsx
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── dashboard/
│       ├── layout.tsx
│       ├── page.tsx
│       └── tasks/
│           ├── page.tsx
│           └── [id]/
│               └── page.tsx
├── components/
│   ├── ui/ (shared UI components)
│   ├── auth/ (authentication components)
│   ├── tasks/ (task management components)
│   └── layouts/ (layout components)
├── lib/
│   ├── auth.ts (auth utilities)
│   ├── api.ts (API client)
│   └── types.ts (type definitions)
└── middleware.ts (auth middleware)
```

#### Core Components

1. **ProtectedRoute Component**
   - Checks authentication status
   - Redirects unauthenticated users to login
   - Preserves redirect URL for post-login redirect

2. **TaskList Component**
   - Displays user's tasks
   - Handles loading, error, and empty states
   - Provides controls for task operations

3. **TaskForm Component**
   - Handles task creation and editing
   - Validates input
   - Manages form state

4. **AuthWrapper Component**
   - Provides auth context to the app
   - Handles session state

#### API Client Layer

1. **HTTP Client**
   - Intercepts requests to add JWT token
   - Handles authentication errors
   - Implements retry logic for failed requests

2. **Service Layer**
   - Task service with CRUD operations
   - Authentication service
   - Error handling and normalization

## Phase 3: Implementation Tasks

### Task 1: Setup Project Structure
- [ ] Initialize Next.js project with App Router
- [ ] Configure TypeScript
- [ ] Set up ESLint and Prettier
- [ ] Configure environment variables

### Task 2: Implement Authentication Flow
- [ ] Integrate Better Auth
- [ ] Create login and registration pages
- [ ] Implement auth middleware
- [ ] Create ProtectedRoute component

### Task 3: Create API Client
- [ ] Set up HTTP client with JWT injection
- [ ] Implement error handling
- [ ] Create service layer for task operations

### Task 4: Develop Task Management UI
- [ ] Create TaskList component
- [ ] Create TaskForm component
- [ ] Implement task CRUD operations
- [ ] Add loading, error, and empty state handling

### Task 5: Styling and Responsiveness
- [ ] Implement responsive design
- [ ] Add loading indicators
- [ ] Style error and empty states
- [ ] Ensure accessibility compliance

### Task 6: Testing and Validation
- [ ] Implement unit tests
- [ ] Add integration tests
- [ ] Perform end-to-end testing
- [ ] Validate all success criteria

## Re-evaluation of Constitution Check

Post-design evaluation:

- [x] All architectural decisions support progressive enhancement
- [x] Minimal viable solution designed first
- [x] Clear separation between UI, auth, and data layers
- [x] Production readiness considerations included
- [x] Extensibility patterns implemented