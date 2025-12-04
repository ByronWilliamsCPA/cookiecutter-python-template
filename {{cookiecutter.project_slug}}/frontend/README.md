# {{ cookiecutter.project_name }} Frontend

React + TypeScript frontend for {{ cookiecutter.project_name }}.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework
- **Axios** - HTTP client
- **ESLint + Prettier** - Code quality

## Quick Start

```bash
# Install dependencies
{{ cookiecutter.frontend_package_manager }} install

# Start development server (http://localhost:3000)
{{ cookiecutter.frontend_package_manager }} run dev

# Run tests
{{ cookiecutter.frontend_package_manager }} run test

# Build for production
{{ cookiecutter.frontend_package_manager }} run build
```

## Development

### Prerequisites

- Node.js {{ cookiecutter.node_version }}+
- Backend API running on port 8000

### Available Scripts

| Command | Description |
|---------|-------------|
| `{{ cookiecutter.frontend_package_manager }} run dev` | Start dev server with HMR |
| `{{ cookiecutter.frontend_package_manager }} run build` | Build for production |
| `{{ cookiecutter.frontend_package_manager }} run preview` | Preview production build |
| `{{ cookiecutter.frontend_package_manager }} run test` | Run tests in watch mode |
| `{{ cookiecutter.frontend_package_manager }} run test:run` | Run tests once |
| `{{ cookiecutter.frontend_package_manager }} run test:coverage` | Run tests with coverage |
| `{{ cookiecutter.frontend_package_manager }} run lint` | Lint code |
| `{{ cookiecutter.frontend_package_manager }} run lint:fix` | Fix lint issues |
| `{{ cookiecutter.frontend_package_manager }} run format` | Format code with Prettier |
| `{{ cookiecutter.frontend_package_manager }} run typecheck` | Run TypeScript type checking |
| `{{ cookiecutter.frontend_package_manager }} run generate-client` | Generate API client from OpenAPI |

### API Integration

The frontend connects to the backend API. In development, Vite proxies `/api` requests to `http://localhost:8000`.

#### Generate TypeScript API Client

Generate a type-safe API client from the FastAPI OpenAPI schema:

```bash
# Make sure backend is running first
cd .. && uv run uvicorn {{ cookiecutter.project_slug }}.main:app &

# Generate client
{{ cookiecutter.frontend_package_manager }} run generate-client
```

This creates typed API functions in `src/client/`.

### Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/          # Images, fonts, etc.
│   ├── client/          # Auto-generated API client
│   ├── components/      # React components
│   ├── hooks/           # Custom React hooks
│   ├── test/            # Test setup and utilities
│   ├── App.tsx          # Root component
│   ├── App.css          # Root styles
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── Dockerfile           # Production Docker image
├── nginx.conf           # Production nginx config
└── vite.config.ts       # Vite configuration
```

## Docker

### Development

```bash
# From project root
docker-compose up frontend
```

### Production

```bash
# Build production image
docker build -t {{ cookiecutter.project_slug }}-frontend .

# Run with custom API URL
docker run -p 80:80 \
  --build-arg VITE_API_URL=https://api.example.com \
  {{ cookiecutter.project_slug }}-frontend
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_DEBUG` | Enable debug mode | `false` |

Create `.env.local` for local overrides (gitignored).

## Testing

```bash
# Run tests in watch mode
{{ cookiecutter.frontend_package_manager }} run test

# Run tests once with coverage
{{ cookiecutter.frontend_package_manager }} run test:coverage
```

Tests use Vitest with React Testing Library.
