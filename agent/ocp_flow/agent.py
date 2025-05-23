from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import subprocess
from google.adk.tools import FunctionTool

   
import subprocess


def run_excel_report_command(_: str) -> str:
    try:
        result = subprocess.run(
            ["python3", "main.py", "--excel-dir", "/Users/roshinpv/Desktop/excel", "--output", "./my_reports"],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else f"Error:\n{result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

excel_command_tool = FunctionTool(
    func=run_excel_report_command
)





execue_task = subprocess.run(["ls", "-l"], capture_output=True, text=True)


root_agent = Agent(
    model=LiteLlm(model="gpt-3.5-turbo", base_url="http://localhost:1234/v1", api_key="sdsd", provider="openai"),
    name='ocp_flow',
    instruction = """ You are a helpful ocp migration agent that answers any query for the  the migration assessment. It should be able to execute the tool based on user request . It can also execute the tool `excel_command_tool` if user asks for it.
User can ask for the execution of the tool. If user asks for process the report and intiate the analysis it should trigger the tool 
       Batch Processing:

"How do I analyze multiple Excel files at once?"

"What's the command to process a directory of migration forms?"

"Where are the batch analysis reports saved?"

"How do I include/exclude certain files from processing?"

OpenShift Assessment:

"What does the OpenShift compatibility score mean?"

"How are migration recommendations generated?"

"What validation rules does the assessment use?"

"How do I interpret the component analysis tables?"

Technical Details:

"What Excel formats are supported?"

"How are mandatory fields validated?"

"What security practices are checked?"

"How are technology stacks analyzed?"

Response Rules:

Only answers questions about the OCP migration analysis tool

Provides command syntax and parameter explanations

Explains report structure and interpretation

Does not discuss general Excel usage or unrelated cloud topics

Output Formatting:

Commands in code blocks

Parameters in bullet lists

File structures as tree diagrams

Scores with visual indicators (✓/✗)

Example Interaction:
User: "How do I check if Redis was detected in my analysis?"
Agent: "The report's component_analysis section shows Redis detection status. In batch mode, check each component's subdirectory for its report.html file."

    """ , 
    description = """ Agent Description:
Specialized assistant for OpenShift cloud migration analysis that processes Excel intake forms in batch mode and generates comprehensive assessment reports. Handles both technical component analysis and OpenShift compatibility scoring.

Key Features:

Batch Excel Processing - Analyze multiple migration intake forms simultaneously

OpenShift Compatibility Assessment - Generate detailed migration feasibility reports

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
- **PDF**: Printable document for distribution

Reports include:
- Code architecture overview
- Identified resiliency patterns and gaps
- Observability assessment
- OpenShift migration recommendations
- Related Jira stories (if configured)
- Actionable next steps

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



""",
tools=[excel_command_tool]
)






