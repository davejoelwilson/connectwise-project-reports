# Changelog

Year - it is 2025.

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Basic ConnectWise API client with connection pooling
- Rate limiting support for API requests
- Pydantic V2 models for data validation:
  - Member model for ConnectWise members
  - Status model for project/ticket statuses
  - Project model with scheduling validation
  - TimeEntry model with time validation
  - Ticket model for project tickets
  - Note model for project/ticket notes
- Comprehensive test suite for data models
- Environment-based configuration
- Detailed logging system
- Sample data collection script with full project data
- Detailed API endpoints documentation
- Streamlit visualization app with:
  - Project metrics dashboard
  - Ticket status and priority charts
  - Risk assessment indicators
  - Detailed ticket table with sorting
  - Stalled ticket tracking
  - Project filtering and sorting options
- Enhanced UI features:
  - Solid white backgrounds for dropdowns
  - Improved text contrast and readability
  - Consistent text colors across components
  - Better visual hierarchy in filters

### Changed
- Updated all models to use Pydantic V2 style validators
- Improved error handling in API client
- Enhanced type safety across all models
- Replaced deprecated Pydantic features with modern alternatives
- Fixed chargeToType enum handling in time entries
- Improved parameter handling in client methods
- Modified project analyzer to include raw ticket data in output
- Enhanced ticket table display with expanded view by default
- Fixed text color contrast issues in frontend components:
  - Changed main content text from gray to black for better readability
  - Updated section headers to black with medium font weight
  - Made labels dark gray (gray-700) with medium font weight
  - Ensured consistent text colors across all analysis cards
  - Improved visual hierarchy with proper contrast ratios
  - Fixed dropdown menu transparency issues
- Updated OpenAI integration:
  - Fixed parameter compatibility with o3-mini model
  - Replaced max_tokens with max_completion_tokens
  - Improved error handling and logging for AI analysis
  - Enhanced caching system for analysis results

### Fixed
- Connection pooling issues in API client
- Coroutine reuse problems in tests
- Rate limiting edge cases
- Validation error messages to match Pydantic V2
- Time entry collection using correct chargeToType enum value
- Project data collection with proper field sets
- Frontend text readability by updating text colors
- OpenAI API compatibility issues:
  - Resolved o3-mini model parameter conflicts
  - Fixed analysis caching and retrieval
  - Improved error handling for failed analyses

## [0.1.0] - 2025-02-11

### Added
- Initial project setup
- Basic project structure
- Environment configuration
- Documentation framework 