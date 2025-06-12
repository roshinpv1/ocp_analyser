# Hard Gate Assessment Tool

A focused tool for analyzing GitHub repositories to assess their compliance with hard gates for:
- **Auditability**: Logging practices, audit trails, tracking IDs
- **Availability**: Retry logic, timeouts, circuit breakers  
- **Error Handling**: Error logging, HTTP codes, client error tracking
- **Monitoring**: Health checks, URL monitoring, metrics collection
- **Testing**: Automated testing, unit tests, integration tests
- **Security**: Authentication, authorization, input validation, encryption
- **Performance**: Caching, connection pooling, async processing
- **Data Management**: Database practices, data validation, backup strategies

## Features

✅ **Three Access Methods**:
- **CLI**: Generate HTML reports locally
- **API**: JSON responses for programmatic access
- **VS Code Extension**: Table view within IDE

✅ **GitHub Integration**: Analyze any GitHub repository with authentication support  
✅ **Multi-LLM Support**: Works with OpenAI, Anthropic Claude, or Google Gemini  
✅ **Comprehensive Reports**: Detailed compliance assessment with actionable recommendations  

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd hardgates
pip install -r requirements.txt
```

### 2. Configuration

Set up your LLM API key (choose one):

```bash
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"  
# OR
export GOOGLE_API_KEY="your-google-key"
```

Optionally set GitHub token for private repositories:

```bash
export GITHUB_TOKEN="your-github-token"
```

## Usage

### CLI Tool

Analyze a repository and generate an HTML report:

```bash
python main.py --repo https://github.com/user/repo --token YOUR_TOKEN --output ./report.html
```

**Options:**
- `--repo`: GitHub repository URL (required)
- `--branch`: Branch to analyze (default: main)
- `--token`: GitHub authentication token
- `--output`: Output HTML file path (default: ./hard_gate_assessment.html)
- `--verbose`: Enable detailed output

**Examples:**

```bash
# Public repository
python main.py --repo https://github.com/fastapi/fastapi

# Private repository with token
python main.py --repo https://github.com/myorg/private-repo --token ghp_xxxx

# Specific branch
python main.py --repo https://github.com/user/repo --branch develop --token ghp_xxxx
```

### API Server

Start the API server:

```bash
python api.py
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

**Endpoints:**

- `POST /analyze` - Start asynchronous assessment
- `POST /analyze/sync` - Synchronous assessment (slower)
- `GET /analyze/{assessment_id}` - Get assessment results
- `GET /health` - Health check

**Example API Usage:**

```bash
# Start assessment
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "branch": "main",
    "github_token": "your-token"
  }'

# Get results
curl "http://localhost:8000/analyze/{assessment_id}"
```

### VS Code Extension

1. **Install Dependencies**: Make sure the API server is running
2. **Open Command Palette**: `Cmd/Ctrl + Shift + P`
3. **Run Command**: "Hard Gate Assessment: Analyze Repository"
4. **Enter Details**: Repository URL, branch, and GitHub token
5. **View Results**: Results will appear in a new panel with filterable table

**Extension Configuration:**

```json
{
  "hardgates.apiUrl": "http://localhost:8000",
  "hardgates.githubToken": "your-token",
  "hardgates.defaultBranch": "main"
}
```

## Project Structure

```
hardgates/
├── main.py                  # CLI interface
├── api.py                   # FastAPI server
├── core/
│   └── flow.py             # PocketFlow framework
├── nodes/
│   ├── fetch_repo.py       # GitHub repository fetching
│   ├── analyze_code.py     # Hard gate assessment
│   └── format_output.py    # Output formatting
├── utils/
│   ├── github_client.py    # GitHub API integration
│   ├── llm_client.py       # LLM provider interface
│   └── formatters.py       # Output format utilities
├── extension/              # VS Code extension
│   ├── package.json
│   └── extension.js
├── docs/
│   └── design.md          # Technical design document
└── requirements.txt        # Python dependencies
```

## Hard Gates Assessment Categories

The tool evaluates **8 core categories** with specific practices:

### 1. Auditability
- Avoid logging confidential data
- Create audit trail logs  
- Add tracking IDs for log messages
- Log REST API calls
- Log application messages
- Ensure client/UI errors are logged

### 2. Availability  
- Implement retry logic
- Set timeouts on I/O operations
- Add throttling/request dropping
- Use circuit breakers on outgoing requests

### 3. Error Handling
- Log system errors
- Use HTTP standard error codes
- Include client error tracking

### 4. Monitoring
- Implement URL monitoring/health checks
- Add metrics collection
- Set up performance monitoring

### 5. Testing
- Automated regression testing
- Unit testing coverage
- Integration testing

### 6. Security
- Input validation
- Authentication mechanisms
- Authorization controls
- Encryption at rest
- Encryption in transit

### 7. Performance
- Caching strategies
- Connection pooling
- Asynchronous processing

### 8. Data Management
- Database connection security
- Data validation
- Backup strategies

## Output Formats

### CLI: HTML Report
- Professional styling with compliance statistics
- Detailed breakdown by category
- Technology stack analysis
- Actionable recommendations
- Filterable findings

### API: JSON Response
```json
{
  "assessment_id": "uuid",
  "project_name": "repository-name",
  "assessment_date": "2024-01-01T12:00:00Z",
  "assessment_type": "hard_gate_assessment",
  "results": {
    "technology_stack": {...},
    "security_quality_analysis": {...},
    "findings": [...],
    "component_analysis": {...}
  }
}
```

### Extension: Interactive Table
- Sortable and filterable results
- Status indicators (✓ Implemented, ⚬ Partial, ✗ Missing)
- Evidence and recommendations
- Compliance statistics dashboard

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

### VS Code Extension Development

```bash
cd extension/
npm install
npm run compile
# Press F5 in VS Code to launch extension development host
```

## Troubleshooting

### Common Issues

**"No LLM API key found"**
- Set one of: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`

**"Repository not found"**  
- Check repository URL format: `https://github.com/user/repo`
- Verify GitHub token has access to private repositories

**"Assessment failed"**
- Check API server is running for VS Code extension
- Verify LLM API quotas and rate limits
- Use `--verbose` flag for detailed error information

**VS Code Extension Issues**
- Ensure API server is running on configured URL
- Check extension settings in VS Code preferences
- Restart VS Code after configuration changes

### API Rate Limits

- **GitHub API**: 5000 requests/hour with token, 60 without
- **OpenAI**: Varies by plan and model
- **Anthropic**: Varies by plan  
- **Google**: Varies by plan

Consider implementing retries with exponential backoff for production use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the design patterns in `docs/design.md`
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 