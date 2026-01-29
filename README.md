# Full-Stack Todo Application

A comprehensive full-stack todo application featuring user authentication, task management, and a modern web interface built with Next.js and FastAPI.

## 🚀 Features

- **User Authentication**: Secure user registration and login with Better Auth integration
- **Task Management**: Create, read, update, and delete (CRUD) operations for todo tasks
- **Task Completion**: Mark tasks as complete/incomplete with toggle functionality
- **User Isolation**: Each user can only access their own tasks
- **Responsive UI**: Modern, mobile-friendly interface built with Tailwind CSS
- **Real-time Updates**: Dynamic task management without page refreshes
- **Security**: JWT token-based authentication with secure API endpoints
- **Rate Limiting**: Protection against API abuse

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **Runtime**: Node.js

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: Better Auth with JWT tokens
- **Database Migrations**: Alembic

### Additional Technologies
- **Environment Management**: python-dotenv
- **Security**: python-jose, passlib for JWT handling
- **API Documentation**: Swagger UI and ReDoc
- **CORS Handling**: Cross-origin resource sharing support

## 🏗️ Architecture

### Frontend Structure
- `app/` - Next.js App Router pages
  - `auth/` - Authentication pages (login, register)
  - `dashboard/` - User dashboard with task management
  - `dashboard/tasks/` - Task management interface
- `components/` - Reusable React components
- `lib/` - Utility functions and API service layer
- `public/` - Static assets

### Backend Structure
- `api/` - API route definitions
- `models/` - Database models (SQLModel)
- `schemas/` - Pydantic schemas for request/response validation
- `auth/` - Authentication and JWT utilities
- `database/` - Database connection and session management
- `middleware/` - Custom middleware (auth, rate limiting)
- `services/` - Business logic implementations

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Task Management
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks` - Retrieve all user tasks (with pagination/filtering)
- `GET /api/{user_id}/tasks/{task_id}` - Retrieve a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a specific task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle task completion status
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task (soft delete)

### System
- `GET /` - Welcome endpoint
- `GET /health` - Health check endpoint

## 🔧 Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- PostgreSQL (or Neon Serverless account)
- Git

### Frontend Setup

1. Clone the repository:
```bash
git clone https://github.com/Mariyam-Asif/Hackathon-II-Phase-2.git
cd Hackathon-II-Phase-2
```

2. Navigate to the frontend directory:
```bash
cd frontend
```

3. Install dependencies:
```bash
npm install
```

4. Create a `.env.local` file with the following content:
```env
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following content:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DELTA=604800  # 7 days in seconds
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days in minutes
LOG_LEVEL=INFO
NEON_DATABASE_URL=your-neon-database-url-here
```

5. Initialize the database:
```bash
# Run database migrations
alembic upgrade head
# Or alternatively, run the create_db_and_tables function in main.py
```

6. Start the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`, with documentation at `http://localhost:8000/docs`.

## 🚀 Running the Application

1. Start the backend server (FastAPI) first:
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. In a new terminal, start the frontend server (Next.js):
```bash
cd frontend
npm run dev
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔐 Authentication Flow

1. **User Registration/Login**: Users authenticate via Better Auth
2. **JWT Token Issuance**: Better Auth creates a session and issues a JWT token
3. **API Requests**: Frontend includes the JWT token in the `Authorization: Bearer <token>` header
4. **Token Verification**: Backend verifies the token signature using the shared secret
5. **User Identification**: Backend decodes the token to get user ID and matches it with the URL parameter
6. **Data Filtering**: Backend returns only tasks belonging to the authenticated user

## 🧪 Testing

### Backend Tests
Run the backend tests using pytest:
```bash
cd backend
pytest
```

### Frontend Development
The Next.js application includes hot-reloading for immediate updates during development.

## 📊 Database Schema

The application uses the following main entities:

### Users Table
- `id`: UUID primary key
- `email`: Unique email address
- `hashed_password`: Securely hashed password
- `created_at`: Timestamp of account creation
- `updated_at`: Timestamp of last update

### Tasks Table
- `id`: UUID primary key
- `title`: Task title (string)
- `description`: Task description (optional text)
- `completed`: Boolean indicating completion status
- `user_id`: Foreign key linking to the user
- `created_at`: Timestamp of task creation
- `updated_at`: Timestamp of last update
- `deleted`: Boolean for soft deletion

## 🛡️ Security Features

- JWT token validation for all authenticated endpoints
- User data isolation - each user can only access their own data
- Rate limiting on authentication endpoints
- Proper error handling without information leakage
- Security headers for enhanced protection
- Input validation and sanitization
- Password hashing with bcrypt

## 🚀 Deployment

### Backend Deployment
1. Set up a production-ready database (PostgreSQL or Neon)
2. Configure environment variables for production
3. Deploy the FastAPI application using a WSGI/ASGI server (Gunicorn/Uvicorn)

### Frontend Deployment
1. Build the Next.js application:
```bash
npm run build
```
2. Deploy to a hosting platform (Vercel, Netlify, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the API documentation at `/docs`
2. Review the error logs in both frontend and backend
3. Ensure all environment variables are properly configured
4. Verify database connectivity
5. Confirm that both frontend and backend servers are running

---

Built with ❤️ using Next.js, FastAPI, and Better Auth.