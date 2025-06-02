# OCP Analyzer: Code Resiliency and Observability Assessment Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful tool for analyzing codebases to assess their resiliency, observability, and OpenShift Container Platform (OCP) migration readiness. This project evaluates code repositories and generates comprehensive reports with actionable recommendations.

![OCP Analyzer Banner](./assets/banner.png)

## Features

- **Codebase Analysis**: Scans repositories for resiliency and observability patterns
- **Excel Integration**: Process information from Excel files for component analysis
- **Batch Processing**: Analyze multiple components simultaneously via Excel directories
- **OCP Migration Assessment**: Evaluate readiness for OpenShift Container Platform
- **Jira Integration**: Include relevant Jira stories in the analysis reports
- **Comprehensive Reporting**: Generate HTML, Markdown, and PDF reports
- **Customizable Patterns**: Configure what files to include or exclude

## Getting Started

### Prerequisites

- Python 3.8+
- Git (for repository fetching)
- Access to an LLM API (Google Gemini, OpenAI, or Anthropic)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ocp_analyser.git
   cd ocp_analyser
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure LLM API access in `utils/call_llm.py`

4. **Configure the application** (optional):
   ```bash
   cp config.env.example .env
   # Edit .env with your preferred settings
   ```

## Configuration

The OCP Analyzer supports configurable settings through environment variables. See `README_CONFIGURATION.md` for detailed configuration options.

### Quick Configuration

#### Enable ChromaDB Storage (Default)
```env
USE_CHROMADB=true
CHROMADB_PERSIST_DIR=./chroma_db
```

#### Disable ChromaDB Storage
```env
USE_CHROMADB=false
```

When ChromaDB is enabled, the system provides:
- Vector storage for analysis reports and OCP assessments
- Semantic search capabilities
- AI agent interface for querying reports

When ChromaDB is disabled, the system:
- Still generates HTML, Markdown, and PDF reports
- Operates in a minimal mode without vector storage
- Continues functioning normally for analysis tasks

### Usage

#### Analyzing a GitHub Repository

```bash
python main.py --repo https://github.com/username/repo --github-token YOUR_GITHUB_TOKEN
```

#### Analyzing a Local Directory

```bash
python main.py --dir /path/to/your/codebase
```

#### Analyzing from Excel File

```bash
python main.py --excel /path/to/components.xlsx
```

#### Batch Processing Multiple Excel Files

```bash
python main.py --excel-dir /path/to/excel/files
```

#### Including Jira Stories

```bash
python main.py --repo https://github.com/username/repo \
               --jira-url https://your-instance.atlassian.net \
               --jira-username your.email@example.com \
               --jira-api-token YOUR_JIRA_API_TOKEN \
               --jira-project-key XYZ
```

### Command Line Options

- `--repo`: GitHub repository URL to analyze
- `--dir`: Local directory to analyze
- `--excel`: Excel file to extract repository/component info from
- `--excel-dir`: Directory containing multiple Excel files to process
- `--sheet`: Sheet name in Excel file (optional)
- `--include`: File patterns to include (e.g., "*.py" "*.js")
- `--exclude`: File patterns to exclude (e.g., "tests/*" "docs/*")
- `--max-size`: Maximum file size to analyze in bytes (default: 100KB)
- `--output`: Output directory for analysis report (default: ./analysis_output)
- `--no-cache`: Disable LLM response caching
- `--github-token`: GitHub authentication token for private repositories
- `--jira-url`: Jira server URL (e.g., https://your-domain.atlassian.net)
- `--jira-username`: Jira username or email
- `--jira-api-token`: Jira API token
- `--jira-project-key`: Jira project key to search for (default: XYZ)

## Reports

The analyzer generates comprehensive reports in multiple formats:
- **HTML**: Interactive web-based report with visualizations
- **Markdown**: Text-based report for version control systems

### Report Types

#### 1. Hard Gate Assessment Report
- Code architecture overview
- Identified resiliency patterns and gaps
- Observability assessment
- Related Jira stories (if configured)
- Actionable next steps

#### 2. Intake Assessment Report  
- Platform-specific readiness assessment
- Resource utilization analysis
- Configuration recommendations
- Migration considerations

#### 3. Migration Insights Report ✨ NEW
- **OpenShift migration readiness checklist**
- **Platform migration recommendations** (TAS/TKGI to OpenShift)
- **Technology stack compatibility analysis**
- **Service bindings and dependencies assessment**
- **Go/No-Go migration status**
- **Actionable migration insights for teams**

The Migration Insights report is specifically designed for leadership teams and migration specialists, providing structured assessment data for migrating applications from traditional platforms to OpenShift.

Users now get three reports from analysis: Hard Gate Assessment (technical), Intake Assessment (OpenShift readiness), and Migration Insights (migration readiness with Go/No-Go decisions). Implementation follows exact user specifications including system prompt, required sections, HTML formatting, and data integration.

## Excel Integration

For batch processing, prepare Excel files with the following information:
- Repository URL or local directory path
- Component name
- Additional component metadata

See `README_BATCH_PROCESSING.md` for detailed instructions on batch processing.

## Jira Integration

When properly configured, the tool will fetch relevant Jira stories for the analyzed component and include them in the final report. Stories are displayed with:
- Summary
- Status
- Description
- Comments
- Attached images

## Project Structure

```
ocp_analyser/
├── core/           # Core framework functionality
├── utils/          # Utility functions
├── agent/          # AI agent framework components
├── nodes.py        # Node implementations for the analysis pipeline
├── flow.py         # Flow configuration for analysis processes
├── main.py         # Command-line interface and entry point
└── requirements.txt # Project dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using [PocketFlow](https://github.com/The-Pocket/PocketFlow) - A 100-line LLM framework
- Special thanks to all contributors and users