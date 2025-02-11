# Project Structure Documentation

## Overview
The project is split into frontend and backend components:

```
ConnectWise - Project Reporting/
├── backend/
│   ├── main.py              # Main FastAPI application
│   ├── connectwise/         # ConnectWise API client
│   ├── analysis/           # Analysis logic
│   ├── ai/                # AI integration
│   ├── scripts/           # Utility scripts
│   └── tests/            # Backend tests
├── frontend/
│   └── ai-dashboard/     # Next.js frontend application
├── data/                # Data storage
│   ├── detailed/        # Detailed project data
│   ├── analysis/        # Analysis results
│   └── ai_analysis/     # AI-generated insights
└── docs/               # Project documentation
```

## Installation

### Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install in development mode:
```bash
pip install -e .  # Install package in editable mode
pip install -r backend/tests/requirements-test.txt  # Install test dependencies
```

### Frontend Setup
1. Install dependencies:
```bash
cd frontend/ai-dashboard
npm install
```

## Key Components

### Backend (`backend/main.py`)
- FastAPI application
- Endpoints for project data and analysis
- ConnectWise API integration
- Running on `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`

### Frontend (`frontend/ai-dashboard`)
- Next.js application
- Modern UI with Tremor components
- Running on `http://localhost:3000`
- TypeScript and Tailwind CSS

## Running the Project

1. Start both services:
```bash
python run.py
```

This will:
- Start the FastAPI backend on port 8000
- Start the Next.js frontend on port 3000
- Create necessary data directories
- Handle graceful shutdown

## API Endpoints

### Projects
- `GET /projects` - List all projects
- `GET /projects/{id}` - Get project details
- `GET /projects/{id}/tickets` - Get project tickets
- `GET /projects/{id}/notes` - Get project notes

### Tickets
- `GET /tickets` - List all tickets
- `GET /tickets/{id}` - Get ticket details
- `GET /tickets/{id}/time-entries` - Get ticket time entries
- `GET /tickets/{id}/notes` - Get ticket notes

### Time Entries
- `GET /time-entries` - List time entries with filtering

### Members
- `GET /members` - List team members

## Environment Variables
Required variables in `.env`:
- `CONNECTWISE_URL`
- `CONNECTWISE_COMPANY`
- `CONNECTWISE_PUBLIC_KEY`
- `CONNECTWISE_PRIVATE_KEY`
- `CONNECTWISE_CLIENT_ID`
- `OPENAI_API_KEY`
- `AGENTOPS_API_KEY`

## Development Guidelines

### Backend
- All API endpoints in `backend/main.py`
- Use FastAPI dependency injection for shared resources
- Follow REST principles
- Include type hints and docstrings

### Frontend
- Page components in `src/app`
- Shared components in `src/components`
- TypeScript interfaces in `src/types`
- Use Tremor for data visualization
- Follow Next.js 14 app router conventions

## Testing
- Backend tests in `backend/tests/`
- Frontend tests in `frontend/ai-dashboard/cypress`
- Run backend tests: `pytest`
- Run frontend tests: `npm test`

## Common Issues

1. **Backend Not Starting**
   - Check if port 8000 is available
   - Verify all environment variables are set
   - Ensure Python dependencies are installed

2. **Frontend Not Starting**
   - Check if port 3000 is available
   - Run `npm install` in frontend directory
   - Verify Node.js version (>=18)

3. **API Connection Issues**
   - Backend must be running
   - Check CORS configuration
   - Verify API URL in frontend environment 