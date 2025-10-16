# LLM Code Deployment Application

A Python/Flask application that automates the entire process of building, deploying, and updating web applications based on project briefs using Large Language Models (LLMs).

## Overview

This application receives project briefs via JSON POST requests, uses OpenRouter's LLM services to generate complete web applications, deploys them to GitHub Pages, and notifies evaluation services. It supports both initial deployments and revisions.

## Features

- **OpenRouter LLM Integration**: Uses OpenRouter API for code generation
- **Automatic GitHub Deployment**: Creates repositories, pushes code, and enables GitHub Pages
- **Retry Mechanisms**: Robust error handling with exponential backoff
- **Revision Support**: Handles multiple rounds of updates to existing projects
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Environment-based Configuration**: Secure configuration management

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   POST Request  │───▶│  Flask API       │───▶│  Background     │
│   /api-endpoint │    │  - Verify Secret │    │  Processing     │
│                 │    │  - Return 200 OK │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┘
                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Evaluation    │◀───│  GitHub Pages    │◀───│  OpenRouter     │
│   Notification  │    │  Deployment      │    │  Code Generation│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- GitHub Personal Access Token
- OpenRouter API Key

### Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd llm-code-deployment-py
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env .env.local
   # Edit .env.local with your actual values
   ```

4. **Required Environment Variables:**
   ```env
   # OpenRouter Configuration
   OPENROUTER_API_KEY=your-key-here        # Required for LLM code generation
   
   # Application Security
   SHARED_SECRET=your-secret-here          # Shared secret for request verification
   
   # GitHub Configuration
   GITHUB_PAT=ghp_your-token-here          # GitHub Personal Access Token
   GITHUB_USERNAME=your-username           # Your GitHub username
   
   # Optional
   LLM_MODEL=tngtech/deepseek-r1t2-chimera:free  # Free LLM model to use
   ```

## Usage

### Starting the Server

**Development:**
```bash
uv run python app.py
```

**Production:**
```bash
uv run gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### API Endpoint

**POST `/api-endpoint`**

Accepts JSON requests with the following structure:

```json
{
  "email": "student@example.com",
  "secret": "your-shared-secret",
  "task": "captcha-solver-abc123",
  "round": 1,
  "nonce": "unique-nonce-value",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=..."
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

**Response:**
```json
{
  "status": "Request received and is being processed."
}
```

### Health Check

**GET `/health`**

Returns server health status:

```json
{
  "status": "healthy",
  "service": "llm-code-deployment"
}
```

## Project Structure

```
llm-code-deployment-py/
├── app.py                    # Main Flask application
├── modules/
│   ├── __init__.py          # Module initialization
│   ├── llm_generator.py     # OpenRouter LLM integration
│   ├── github_manager.py    # GitHub API operations
│   └── notifier.py          # Evaluation notifications with retry
├── pyproject.toml           # Project configuration and dependencies
├── requirements.txt         # Generated requirements file
├── .env                     # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Core Components

### 1. Flask API Server (`app.py`)
- Handles incoming POST requests
- Verifies shared secrets
- Manages background processing with threading
- Provides health check endpoint

### 2. LLM Generator (`modules/llm_generator.py`)
- Integrates with OpenRouter API
- Processes project briefs and attachments
- Generates complete HTML applications
- Validates generated code

### 3. GitHub Manager (`modules/github_manager.py`)
- Creates and manages GitHub repositories
- Handles file commits and updates
- Enables GitHub Pages deployment
- Supports both initial creation and updates

### 4. Notification Service (`modules/notifier.py`)
- Sends notifications to evaluation URLs
- Implements exponential backoff retry logic
- Validates notification data
- Comprehensive error handling

## Workflow

1. **Request Reception**: API endpoint receives and validates JSON request
2. **Secret Verification**: Confirms shared secret matches configuration
3. **Immediate Response**: Returns 200 OK status immediately
4. **Background Processing**: Starts threaded processing of the request
5. **Code Generation**: OpenRouter LLM generates complete web application
6. **Repository Management**: Creates/updates GitHub repository
7. **Pages Deployment**: Enables GitHub Pages for the repository
8. **Evaluation Notification**: Sends notification with repository details

## Error Handling

- **LLM Failures**: Comprehensive error logging and graceful failure handling
- **GitHub API**: Retry mechanisms for rate limits and temporary failures
- **Notifications**: Exponential backoff (1s, 2s, 4s, 8s delays)
- **Comprehensive Logging**: All errors logged with context
- **Graceful Degradation**: Continues processing where possible

## Security Considerations

- **Secret Verification**: All requests must include valid shared secret
- **Environment Variables**: Sensitive data stored in environment variables
- **No Hardcoded Secrets**: All secrets loaded from environment
- **Git History**: `.gitignore` prevents committing sensitive files
- **Request Validation**: Comprehensive input validation

## Development

### Running Tests
```bash
uv run python quick_test.py
```

### Code Formatting
```bash
uv run black .
```

### Linting
```bash
uv run flake8
```

### Adding Dependencies
```bash
uv add package-name
uv export --format requirements-txt > requirements.txt
```

## Deployment

### Environment Setup
1. Configure all required environment variables
2. Ensure GitHub PAT has repository creation permissions
3. Verify OpenRouter API key is valid
4. Test with a sample request

### Production Considerations
- Use a production WSGI server (gunicorn, uwsgi)
- Configure proper logging levels
- Set up monitoring and alerting
- Implement rate limiting if needed
- Use HTTPS for all endpoints

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify GitHub PAT has correct permissions
   - Check OpenRouter API key is valid
   - Confirm shared secret matches

2. **Repository Creation Failures**
   - Ensure GitHub username is correct
   - Check repository name conflicts
   - Verify PAT has repo creation permissions

3. **LLM Generation Issues**
   - Check OpenRouter API key validity and quotas
   - Verify network connectivity
   - Review model availability

4. **Notification Failures**
   - Confirm evaluation URL is accessible
   - Check network connectivity
   - Review notification payload format

### Logging

The application provides comprehensive logging:
- **INFO**: Normal operation flow
- **WARNING**: Recoverable issues and retries
- **ERROR**: Serious issues requiring attention
- **DEBUG**: Detailed debugging information

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Create an issue with detailed information
4. Include relevant log entries and configuration (without secrets)