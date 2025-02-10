# ConnectWise Project Reporting

A Python-based system for automated project reporting using ConnectWise Manage API.

## Features
- Asynchronous ConnectWise API client with connection pooling
- Comprehensive project, ticket, and time entry data collection
- Efficient caching and retry mechanisms
- Type-safe data models
- Detailed logging and error handling

## Quick Start

1. Clone the repository
2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your ConnectWise credentials
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest
```

## Documentation
- [ConnectWise Setup](docs/connectwise_setup.md)
- [API Endpoints](docs/api_endpoints.md)
- [Testing Plan](docs/testing_plan.md)
- [Project Planning](docs/planning.md)

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
