# ConnectWise Project Reporting

A modern web application for automated project reporting and analysis using ConnectWise Manage API.

## Features
- Real-time project analytics with AI insights
- Comprehensive data collection from ConnectWise
- Modern React frontend with Tremor components
- FastAPI backend with async support
- Automated analysis pipeline

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/connectwise-project-reporting.git
cd connectwise-project-reporting
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Install dependencies:
```bash
# Backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install backend requirements
pip install -r backend/requirements.txt
pip install -e .  # Install package in development mode

# Frontend
cd frontend/ai-dashboard
npm install
cd ../..  # Return to project root
```

4. Start the application:
```bash
python run.py
```

Visit:
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Documentation
- [Project Structure](docs/project_structure.md) - Architecture and setup
- [API Reference](docs/api_endpoints.md) - API documentation
- [Development Guide](docs/development.md) - Development workflow
- [Testing Guide](docs/testing_guide.md) - Testing procedures

## Project Structure
```
.
├── backend/
│   ├── connectwise/     # ConnectWise API client
│   ├── tests/          # Test suite
│   └── main.py         # FastAPI application
├── docs/               # Documentation
└── project_config.json # Project configuration
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
MIT License
