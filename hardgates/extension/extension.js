const vscode = require('vscode');
const axios = require('axios');

// Extension activation
function activate(context) {
    console.log('Hard Gate Assessment extension is now active');
    
    try {
        // Register the analyze command
        let disposable = vscode.commands.registerCommand('hardgates.analyze', async () => {
            console.log('hardgates.analyze command executed');
            try {
                await analyzeRepository();
            } catch (error) {
                console.error('Error in analyzeRepository:', error);
                vscode.window.showErrorMessage(`Extension error: ${error.message}`);
            }
        });

        context.subscriptions.push(disposable);
        console.log('hardgates.analyze command registered successfully');
        
        // Register a simple test command
        let testDisposable = vscode.commands.registerCommand('hardgates.test', () => {
            console.log('hardgates.test command executed');
            vscode.window.showInformationMessage('Hard Gate Assessment extension is working! Commands are registered.');
        });
        
        context.subscriptions.push(testDisposable);
        console.log('hardgates.test command registered successfully');
        
        // Show a notification that the extension is ready
        vscode.window.showInformationMessage('Hard Gate Assessment extension is ready!');
        
    } catch (error) {
        console.error('Error during extension activation:', error);
        vscode.window.showErrorMessage(`Failed to activate Hard Gate Assessment extension: ${error.message}`);
    }
}

// Main analysis function
async function analyzeRepository() {
    try {
        // Get configuration
        const config = vscode.workspace.getConfiguration('hardgates');
        const apiUrl = config.get('apiUrl', 'http://localhost:8000');
        const defaultToken = config.get('githubToken', '');
        const defaultBranch = config.get('defaultBranch', 'main');

        // Show input dialogs
        const repoUrl = await vscode.window.showInputBox({
            prompt: 'Enter GitHub repository URL',
            placeholder: 'https://github.com/user/repo or https://github.company.com/user/repo',
            validateInput: (value) => {
                if (!value) {
                    return 'Please enter a repository URL';
                }
                if (!value.startsWith('https://')) {
                    return 'URL must start with https://';
                }
                const domain = value.split('//')[1]?.split('/')[0];
                if (!domain || !domain.includes('github')) {
                    return 'Please enter a valid GitHub repository URL (supports github.com and GitHub Enterprise domains)';
                }
                return null;
            }
        });

        if (!repoUrl) {
            return; // User cancelled
        }

        const branch = await vscode.window.showInputBox({
            prompt: 'Enter branch name',
            value: defaultBranch,
            placeholder: 'main'
        });

        if (!branch) {
            return; // User cancelled
        }

        const githubToken = await vscode.window.showInputBox({
            prompt: 'Enter GitHub token (optional for public repos)',
            value: defaultToken,
            password: true,
            placeholder: 'ghp_...'
        });

        // Start analysis
        vscode.window.showInformationMessage('Starting hard gate assessment...');

        const assessmentId = await startAssessment(apiUrl, repoUrl, branch, githubToken);

        if (assessmentId) {
            await pollForResults(apiUrl, assessmentId);
        }

    } catch (error) {
        vscode.window.showErrorMessage(`Assessment failed: ${error.message}`);
        console.error('Assessment error:', error);
    }
}

// Start assessment via API
async function startAssessment(apiUrl, repoUrl, branch, githubToken) {
    try {
        const response = await axios.post(`${apiUrl}/analyze`, {
            repo_url: repoUrl,
            branch: branch,
            github_token: githubToken || undefined
        });

        return response.data.assessment_id;
    } catch (error) {
        if (error.response) {
            throw new Error(`API Error: ${error.response.data.detail || error.response.statusText}`);
        } else if (error.request) {
            throw new Error('Cannot connect to Hard Gate Assessment API. Make sure the API server is running.');
        } else {
            throw new Error(`Request failed: ${error.message}`);
        }
    }
}

// Poll for assessment results
async function pollForResults(apiUrl, assessmentId) {
    const maxPolls = 60; // 5 minutes with 5-second intervals
    let polls = 0;

    const poll = async () => {
        try {
            polls++;
            const response = await axios.get(`${apiUrl}/analyze/${assessmentId}`);
            const data = response.data;

            if (data.status === 'running') {
                if (polls < maxPolls) {
                    vscode.window.showInformationMessage(`Assessment in progress... (${polls * 5}s)`);
                    setTimeout(poll, 5000); // Poll every 5 seconds
                } else {
                    vscode.window.showWarningMessage('Assessment is taking longer than expected. Check API status.');
                }
            } else if (data.error) {
                vscode.window.showErrorMessage(`Assessment failed: ${data.message}`);
            } else {
                // Success - show results
                await showResults(data);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get assessment results: ${error.message}`);
        }
    };

    // Start polling
    setTimeout(poll, 2000); // Initial delay of 2 seconds
}

// Display results in a table view
async function showResults(data) {
    try {
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'hardGateResults',
            `Hard Gate Assessment - ${data.project_name}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Convert results to table data
        const tableData = convertToTableData(data.results);

        // Generate HTML content
        panel.webview.html = generateWebviewHtml(data, tableData);

        vscode.window.showInformationMessage('Hard gate assessment completed! Results displayed in new panel.');

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to display results: ${error.message}`);
    }
}

// Convert assessment results to table data - Updated for 15 Primary Hard Gates
function convertToTableData(results) {
    const tableRows = [];

    // Define the 15 primary hard gates mapping
    const primaryGatesMapping = {
        'logs_searchable_available': 'Logs Are Searchable And Available',
        'avoid_logging_confidential_data': 'Avoid Logging Confidential Data',
        'create_audit_trail_logs': 'Create Audit Trail Logs',
        'tracking_id_for_log_messages': 'Implement Tracking ID For Log Messages',
        'log_rest_api_calls': 'Log REST API Calls',
        'log_application_messages': 'Log Application Messages',
        'client_ui_errors_logged': 'Client UI Errors Are Logged',
        'retry_logic': 'Retry Logic',
        'set_timeouts_io_operations': 'Set Timeouts On IO Operation',
        'throttling_drop_request': 'Throttling, Drop Request',
        'circuit_breakers_outgoing_requests': 'Set Circuit Breakers On Outgoing Requests',
        'log_system_errors': 'Log System Errors',
        'use_http_standard_error_codes': 'Use HTTP Standard Error Codes',
        'include_client_error_tracking': 'Include Client Error Tracking',
        'automated_regression_testing': 'Automated Regression Testing'
    };

    // Category mapping for the 15 primary gates
    const categoryMapping = {
        'logs_searchable_available': 'Auditability',
        'avoid_logging_confidential_data': 'Auditability',
        'create_audit_trail_logs': 'Auditability',
        'tracking_id_for_log_messages': 'Auditability',
        'log_rest_api_calls': 'Auditability',
        'log_application_messages': 'Auditability',
        'client_ui_errors_logged': 'Auditability',
        'retry_logic': 'Availability',
        'set_timeouts_io_operations': 'Availability',
        'throttling_drop_request': 'Availability',
        'circuit_breakers_outgoing_requests': 'Availability',
        'log_system_errors': 'Error Handling',
        'use_http_standard_error_codes': 'Error Handling',
        'include_client_error_tracking': 'Error Handling',
        'automated_regression_testing': 'Testing'
    };

    // Process primary hard gates first
    const primaryHardGates = results.primary_hard_gates || {};

    for (const [gateKey, details] of Object.entries(primaryHardGates)) {
        if (primaryGatesMapping[gateKey] && typeof details === 'object' && details !== null) {
            const practiceDisplay = primaryGatesMapping[gateKey];
            const categoryDisplay = categoryMapping[gateKey] || 'Other';

            const status = details.implemented || 'no';
            const statusDisplay = {
                'yes': '✓ Implemented',
                'partial': '⚬ Partial',
                'no': '✗ Missing'
            }[status] || status;

            tableRows.push({
                category: categoryDisplay,
                practice: practiceDisplay,
                status: statusDisplay,
                evidence: details.evidence || 'No evidence',
                recommendation: details.recommendation || 'No recommendation'
            });
        }
    }

    // If no primary_hard_gates, fall back to security_quality_analysis but only for the 15 primary gates
    if (tableRows.length === 0) {
        const securityQuality = results.security_quality_analysis || {};

        // Map security_quality_analysis structure to primary gates
        const fallbackMapping = {
            'auditability': {
                'avoid_logging_confidential_data': 'avoid_logging_confidential_data',
                'create_audit_trail_logs': 'create_audit_trail_logs',
                'tracking_id_for_log_messages': 'tracking_id_for_log_messages',
                'log_rest_api_calls': 'log_rest_api_calls',
                'log_application_messages': 'log_application_messages',
                'client_ui_errors_are_logged': 'client_ui_errors_logged'
            },
            'availability': {
                'retry_logic': 'retry_logic',
                'set_timeouts_on_io_operations': 'set_timeouts_io_operations',
                'throttling_drop_request': 'throttling_drop_request',
                'circuit_breakers_on_outgoing_requests': 'circuit_breakers_outgoing_requests'
            },
            'error_handling': {
                'log_system_errors': 'log_system_errors',
                'use_http_standard_error_codes': 'use_http_standard_error_codes',
                'include_client_error_tracking': 'include_client_error_tracking'
            },
            'testing': {
                'automated_regression_testing': 'automated_regression_testing'
            }
        };

        for (const [category, practices] of Object.entries(securityQuality)) {
            const categoryMapping = fallbackMapping[category];
            if (categoryMapping && typeof practices === 'object' && practices !== null) {
                for (const [practice, details] of Object.entries(practices)) {
                    const primaryGateKey = categoryMapping[practice];
                    if (primaryGateKey && primaryGatesMapping[primaryGateKey] && typeof details === 'object' && details !== null) {
                        const practiceDisplay = primaryGatesMapping[primaryGateKey];
                        const categoryDisplay = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                        const status = details.implemented || 'no';
                        const statusDisplay = {
                            'yes': '✓ Implemented',
                            'partial': '⚬ Partial',
                            'no': '✗ Missing'
                        }[status] || status;

                        tableRows.push({
                            category: categoryDisplay,
                            practice: practiceDisplay,
                            status: statusDisplay,
                            evidence: details.evidence || 'No evidence',
                            recommendation: details.recommendation || 'No recommendation'
                        });
                    }
                }
            }
        }
    }

    // Add technology stack information
    const techStack = results.technology_stack || {};
    ['languages', 'frameworks', 'databases'].forEach(techType => {
        const items = techStack[techType] || [];
        items.forEach(item => {
            if (typeof item === 'object' && item !== null) {
                tableRows.push({
                    category: 'Technology',
                    practice: `${techType.slice(0, -1)}: ${item.name || 'Unknown'}`,
                    status: '✓ Detected',
                    evidence: `Version: ${item.version || 'N/A'}, Purpose: ${item.purpose || 'N/A'}`,
                    recommendation: 'Continue using as appropriate'
                });
            }
        });
    });

    return tableRows;
}

// Generate HTML for webview
function generateWebviewHtml(data, tableData) {
    const calculateStats = (results) => {
        // Calculate stats based on the 15 primary hard gates
        const primaryHardGates = results.primary_hard_gates || {};
        const primaryGatesKeys = [
            'logs_searchable_available', 'avoid_logging_confidential_data', 'create_audit_trail_logs',
            'tracking_id_for_log_messages', 'log_rest_api_calls', 'log_application_messages',
            'client_ui_errors_logged', 'retry_logic', 'set_timeouts_io_operations',
            'throttling_drop_request', 'circuit_breakers_outgoing_requests', 'log_system_errors',
            'use_http_standard_error_codes', 'include_client_error_tracking', 'automated_regression_testing'
        ];

        let total = 0, implemented = 0, partial = 0, missing = 0;

        // Count from primary_hard_gates first
        for (const gateKey of primaryGatesKeys) {
            const details = primaryHardGates[gateKey];
            if (details && typeof details === 'object') {
                total++;
                const status = details.implemented || 'no';
                if (status === 'yes') implemented++;
                else if (status === 'partial') partial++;
                else missing++;
            }
        }

        // If no primary_hard_gates found, fall back to security_quality_analysis but only count the 15 primary gates
        if (total === 0) {
            const securityQuality = results.security_quality_analysis || {};

            // Map to find the 15 primary gates in security_quality_analysis
            const fallbackMapping = {
                'auditability': ['avoid_logging_confidential_data', 'create_audit_trail_logs', 'tracking_id_for_log_messages', 'log_rest_api_calls', 'log_application_messages', 'client_ui_errors_are_logged'],
                'availability': ['retry_logic', 'set_timeouts_on_io_operations', 'throttling_drop_request', 'circuit_breakers_on_outgoing_requests'],
                'error_handling': ['log_system_errors', 'use_http_standard_error_codes', 'include_client_error_tracking'],
                'testing': ['automated_regression_testing']
            };

            for (const [category, practices] of Object.entries(securityQuality)) {
                const expectedPractices = fallbackMapping[category] || [];
                if (typeof practices === 'object' && practices !== null) {
                    for (const [practice, details] of Object.entries(practices)) {
                        if (expectedPractices.includes(practice) && typeof details === 'object' && details !== null) {
                            total++;
                            const status = details.implemented || 'no';
                            if (status === 'yes') implemented++;
                            else if (status === 'partial') partial++;
                            else missing++;
                        }
                    }
                }
            }
        }

        // Ensure we show 15 as the total for the primary gates
        if (total === 0) {
            total = 15;
            missing = 15;
        }

        const compliance = total > 0 ? ((implemented + 0.5 * partial) / total * 100).toFixed(1) : 0;
        return { total, implemented, partial, missing, compliance };
    };

    const stats = calculateStats(data.results);

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hard Gate Assessment Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        
        h1 {
            color: var(--vscode-editor-foreground);
            border-bottom: 2px solid var(--vscode-panel-border);
            padding-bottom: 10px;
        }
        
        .summary {
            background: var(--vscode-panel-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .stat {
            text-align: center;
            padding: 10px;
            background: var(--vscode-input-background);
            border-radius: 4px;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--vscode-button-background);
        }
        
        .stat-label {
            font-size: 0.9em;
            color: var(--vscode-descriptionForeground);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--vscode-panel-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            overflow: hidden;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        th {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            font-weight: 600;
        }
        
        tr:hover {
            background: var(--vscode-list-hoverBackground);
        }
        
        .status-implemented {
            color: #4CAF50;
        }
        
        .status-partial {
            color: #FF9800;
        }
        
        .status-missing {
            color: #F44336;
        }
        
        .filter-container {
            margin: 20px 0;
        }
        
        .filter-input {
            width: 100%;
            padding: 8px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
        }
    </style>
</head>
<body>
    <h1>Hard Gate Assessment - ${data.project_name}</h1>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">${stats.total}</div>
                <div class="stat-label">Total Gates</div>
            </div>
            <div class="stat">
                <div class="stat-value">${stats.implemented}</div>
                <div class="stat-label">Implemented</div>
            </div>
            <div class="stat">
                <div class="stat-value">${stats.partial}</div>
                <div class="stat-label">Partial</div>
            </div>
            <div class="stat">
                <div class="stat-value">${stats.missing}</div>
                <div class="stat-label">Missing</div>
            </div>
            <div class="stat">
                <div class="stat-value">${stats.compliance}%</div>
                <div class="stat-label">Compliance</div>
            </div>
        </div>
    </div>
    
    <div class="filter-container">
        <input type="text" class="filter-input" placeholder="Filter results..." onkeyup="filterTable(this.value)">
    </div>
    
    <table id="resultsTable">
        <thead>
            <tr>
                <th>Category</th>
                <th>Practice</th>
                <th>Status</th>
                <th>Evidence</th>
                <th>Recommendation</th>
            </tr>
        </thead>
        <tbody>
            ${tableData.map(row => `
                <tr>
                    <td>${row.category}</td>
                    <td>${row.practice}</td>
                    <td class="status-${row.status.includes('Implemented') ? 'implemented' : row.status.includes('Partial') ? 'partial' : 'missing'}">${row.status}</td>
                    <td>${row.evidence}</td>
                    <td>${row.recommendation}</td>
                </tr>
            `).join('')}
        </tbody>
    </table>
    
    <script>
        function filterTable(value) {
            const table = document.getElementById('resultsTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(value.toLowerCase()) ? '' : 'none';
            }
        }
    </script>
</body>
</html>`;
}

// Extension deactivation
function deactivate() {
    console.log('Hard Gate Assessment extension deactivated');
}

module.exports = {
    activate,
    deactivate
};
