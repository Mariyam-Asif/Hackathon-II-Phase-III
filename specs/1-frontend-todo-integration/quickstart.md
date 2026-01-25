# Quickstart Guide: Frontend UI and API Integration

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to the backend API endpoints
- Better Auth configuration set up

## Setup Instructions

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 2. Environment Configuration
Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_JWT_ALGORITHM=HS256
```

### 3. Run Development Server
```bash
# Start the development server
npm run dev
# or
yarn dev

# The application will be available at http://localhost:3000
```

## Key Directories and Files

### App Router Structure
```
app/
├── layout.tsx          # Root layout
├── page.tsx            # Landing page
├── auth/
│   ├── layout.tsx      # Auth section layout
│   ├── login/page.tsx  # Login page
│   └── register/page.tsx # Registration page
└── dashboard/
    ├── layout.tsx      # Dashboard layout
    └── tasks/
        └── page.tsx    # Task management page
```

### Components
```
components/
├── ui/                 # Shared UI components
├── auth/               # Authentication components
└── tasks/              # Task management components
```

### Utilities
```
lib/
├── auth.ts             # Authentication utilities
├── api.ts              # API client implementation
└── types.ts            # Type definitions
```

## Running Tests

```bash
# Run all tests
npm test
# or
yarn test

# Run tests in watch mode
npm run test:watch
# or
yarn test:watch

# Run linting
npm run lint
# or
yarn lint

# Run type checking
npm run type-check
# or
yarn type-check
```

## Building for Production

```bash
# Build the application
npm run build
# or
yarn build

# Run the production build locally
npm start
# or
yarn start
```

## Common Commands

```bash
# Format code with Prettier
npm run format
# or
yarn format

# Check for security vulnerabilities
npm audit
# or
yarn audit

# Analyze bundle size
npm run analyze
# or
yarn analyze
```

## Troubleshooting

### Common Issues

1. **Authentication not working**
   - Verify `BETTER_AUTH_SECRET` matches backend configuration
   - Check that backend is running and accessible

2. **API calls failing**
   - Verify `NEXT_PUBLIC_API_BASE_URL` points to running backend
   - Check network connectivity to backend

3. **Environment variables not loading**
   - Ensure `.env.local` file is in the correct directory
   - Restart development server after changing environment variables