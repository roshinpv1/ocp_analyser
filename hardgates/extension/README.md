# Hard Gate Assessment VS Code Extension

A VS Code extension for analyzing GitHub repositories for hard gate compliance directly within the editor.

## Features

- Analyze GitHub repositories from within VS Code
- Focus on 15 primary hard gates for comprehensive assessment
- Interactive results displayed in a webview panel
- Support for both public and private repositories
- Real-time assessment progress tracking

## 15 Primary Hard Gates

This extension focuses specifically on these 15 primary hard gates:

### Auditability (7 gates)
1. **Logs are searchable and available**
2. **Avoid logging confidential data**
3. **Create audit trail logs**
4. **Implement tracking ID for log messages**
5. **Log REST API calls**
6. **Log application messages**
7. **Client UI errors are logged**

### Availability (4 gates)
8. **Retry Logic**
9. **Set timeouts on IO operation**
10. **Throttling, drop request**
11. **Set circuit breakers on outgoing requests**

### Error Handling (3 gates)
12. **Log system errors**
13. **Use HTTP standard error codes**
14. **Include Client error tracking**

### Testing (1 gate)
15. **Automated Regression Testing**

## Installation

1. Package the extension:
   ```bash
   npm run compile
   ```

2. Install in VS Code:
   - Open VS Code
   - Press `Ctrl+Shift+P` (Cmd+Shift+P on macOS)
   - Run "Developer: Install Extension from Location..."
   - Select the extension folder

## Usage

1. Open VS Code
2. Press `Ctrl+Shift+P` (Cmd+Shift+P on macOS)
3. Type "Hard Gate Assessment: Analyze Repository"
4. Enter the GitHub repository URL
5. Specify the branch to analyze
6. Optionally provide a GitHub token for private repositories
7. Wait for analysis to complete
8. View results in the webview panel

## Configuration

Configure the extension through VS Code settings:

- `hardgates.apiUrl`: URL of the Hard Gate Assessment API server (default: http://localhost:8000)
- `hardgates.githubToken`: GitHub personal access token for private repositories
- `hardgates.defaultBranch`: Default branch to analyze (default: main)

## Requirements

- The Hard Gate Assessment API server must be running
- LLM API key configured (OpenAI, Anthropic, or Google)
- Internet connection for GitHub access

## API Server

Start the API server before using the extension:

```bash
cd ../
python3 api.py
```

The API server will run on http://localhost:8000 by default.

## Results Format

The extension displays results in a table format with:
- **Practice**: The hard gate being evaluated
- **Status**: ✓ Implemented, ⚬ Partial, or ✗ Missing
- **Evidence**: Specific code evidence found
- **Recommendation**: Actionable improvement suggestions

### Executive Summary
- Total Gates Evaluated: 15
- Gates Met: Number of fully implemented gates
- Partially Met: Number of partially implemented gates
- Not Met: Number of missing gates
- Overall Compliance Percentage

## Consistency with Main Tool

This extension maintains complete consistency with the main command-line tool:
- Uses identical 15 primary hard gates
- Same assessment logic and scoring
- Identical compliance percentage calculations
- Same evidence and recommendation generation

## Troubleshooting

### Extension won't start
- Ensure the API server is running on the configured URL
- Check that LLM API keys are properly configured
- Verify internet connectivity

### Assessment fails
- Check GitHub token permissions for private repositories
- Verify the repository URL is correct and accessible
- Check API server logs for detailed error information

### Results not displaying
- Ensure the webview panel has loaded completely
- Check browser console for JavaScript errors
- Try refreshing the webview panel

## Development

### Building from Source
```bash
npm install
npm run compile
```

### VS Code Development Setup

This extension includes complete VS Code development configuration:

#### Quick Start for Debugging
1. **Option A**: Open the workspace file in VS Code:
   ```bash
   code hardgates-extension.code-workspace
   ```
2. **Option B**: Open the extension folder directly in VS Code:
   ```bash
   code .
   ```
3. Press `F5` or go to Run and Debug view
4. Select "Launch Extension" and click the play button
5. A new VS Code window opens with your extension loaded

#### Debug Configuration
- **Launch Extension**: Debug the extension in a new Extension Development Host window
- **Launch Extension (No Build)**: Quick launch without running the compile task
- **Extension Tests**: Run extension tests with debugging
- **Attach to Extension Host**: Attach debugger to running extension host

To debug the extension:
1. Open the extension folder in VS Code
2. Press `F5` or go to Run and Debug view
3. Select "Launch Extension" and click the play button
4. A new VS Code window opens with your extension loaded
5. Set breakpoints in `extension.js` and test the extension

#### Available Tasks
- **Compile Extension**: Build the extension (runs `npm run compile`)
- **Lint Extension**: Check code quality with ESLint
- **Lint and Fix Extension**: Auto-fix ESLint issues
- **Package Extension**: Create a VSIX package for distribution
- **Install Extension**: Package and install the extension in VS Code

#### Recommended Extensions
The workspace includes recommendations for useful extensions:
- TypeScript support
- ESLint for code quality
- Prettier for formatting
- JSON support

#### ESLint Integration
Code quality is maintained with ESLint:
```bash
npm run lint          # Check for issues
npm run lint:fix      # Automatically fix issues
```

#### Packaging and Installation
```bash
npm run package       # Create VSIX file
npm run install-extension  # Package and install in VS Code
```

### Development Workflow

1. **Setup**: `npm install` to install dependencies
2. **Development**: Open in VS Code and press `F5` to debug
3. **Testing**: Use Command Palette to test "Hard Gate Assessment: Analyze Repository"
4. **Quality**: Run `npm run lint:fix` to ensure code quality
5. **Packaging**: Run `npm run package` to create distribution file

### File Structure
```
extension/
├── .vscode/                 # VS Code development configuration
│   ├── launch.json         # Debug configurations
│   ├── tasks.json          # Build tasks
│   ├── settings.json       # Workspace settings
│   └── extensions.json     # Recommended extensions
├── extension.js            # Main extension code
├── package.json            # Extension manifest
├── tsconfig.json           # TypeScript configuration
├── .eslintrc.js           # ESLint configuration
├── .vscodeignore          # Files excluded from packaging
└── README.md              # This file
```

### Testing
The extension includes consistency tests with the main tool to ensure alignment on the 15 primary hard gates assessment. 