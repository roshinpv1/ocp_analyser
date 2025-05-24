# Code Analyzer Nodes

This directory contains the modular implementation of nodes used in the code analyzer.

## Directory Structure

The nodes are organized by functionality:

- `/assessment` - Nodes for analyzing and assessing codebase quality and OpenShift compatibility
  - `ocp_assessment.py` - Evaluates migration readiness for OpenShift
  - `code_analysis.py` - Performs comprehensive code analysis including tech stack, components, and quality

- `/data_processing` - Nodes for retrieving and processing input data
  - `repo_fetcher.py` - Fetches code from GitHub repositories or local directories
  - `excel_processor.py` - Processes Excel intake forms
  - `jira_connector.py` - Fetches Jira stories related to the project

- `/reporting` - Nodes for generating output reports
  - `report_generator.py` - Creates HTML, Markdown, and PDF reports

- `/utils` - Utility functions for nodes
  - `node_helpers.py` - Common helper functions

## Usage

Import nodes directly from their respective modules:

```python
from nodes import (
    FetchRepo, 
    AnalyzeCode, 
    GenerateReport, 
    ProcessExcel,
    FetchJiraStories,
    OcpAssessmentNode
)
```

## Adding New Nodes

To add a new node:

1. Create a new file in the appropriate subdirectory
2. Implement the Node class
3. Update the `__init__.py` in the subdirectory to export the node
4. Update the root `__init__.py` to re-export the node

Example:

```python
# nodes/assessment/new_node.py
from core.genflow import Node

class NewAssessmentNode(Node):
    def prep(self, shared):
        # ...

    def exec(self, prep_res):
        # ...

    def post(self, shared, prep_res, exec_res):
        # ...
        return "default"
```

```python
# nodes/assessment/__init__.py
from nodes.assessment.ocp_assessment import OcpAssessmentNode
from nodes.assessment.code_analysis import AnalyzeCode
from nodes.assessment.new_node import NewAssessmentNode

__all__ = [
    'OcpAssessmentNode',
    'AnalyzeCode',
    'NewAssessmentNode'
]
```

```python
# nodes/__init__.py
from nodes.assessment.new_node import NewAssessmentNode
# ... other imports

__all__ = [
    # ... existing nodes
    'NewAssessmentNode'
] 