const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.runCodeInsight', runCodeInsight);
    context.subscriptions.push(disposable);

    let statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(microscope) CodeInsight";
    statusBarItem.command = 'extension.runCodeInsight';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

async function runCodeInsight() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('CodeInsight: No active editor found');
        return;
    }

    const document = editor.document;
    const fileName = document.fileName;
    const languageId = document.languageId;

    const languageMap = {
        'python': 'python',
        'javascript': 'javascript',
        // Add more mappings as needed
    };

    const codeInsightLanguage = languageMap[languageId];
    if (!codeInsightLanguage) {
        vscode.window.showErrorMessage(`CodeInsight: Unsupported language ${languageId}`);
        return;
    }

    const pythonPath = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
    const scriptPath = path.join(__dirname, 'codeinsight.py');

    if (!fs.existsSync(scriptPath)) {
        vscode.window.showErrorMessage('CodeInsight: Python script not found');
        return;
    }

    const command = `"${pythonPath}" "${scriptPath}" "${fileName}" --language ${codeInsightLanguage} --structure --complexity --smells --performance --document`;

    try {
        const output = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Running CodeInsight Analysis",
            cancellable: false
        }, async (progress) => {
            return new Promise((resolve, reject) => {
                exec(command, (error, stdout, stderr) => {
                    if (error) reject(error);
                    else if (stderr) reject(new Error(stderr));
                    else resolve(stdout);
                });
            });
        });

        const results = JSON.parse(output);
        
        // Display results in a WebView
        const panel = vscode.window.createWebviewPanel(
            'codeinsightResults',
            'CodeInsight Results',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true
            }
        );
        panel.webview.html = getWebviewContent(results);
    } catch (error) {
        vscode.window.showErrorMessage(`CodeInsight error: ${error.message}`);
    }
}

function getWebviewContent(results) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CodeInsight Results</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #333; }
            h2 { color: #666; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>CodeInsight Analysis Results</h1>
        ${Object.entries(results).map(([key, value]) => `
            <h2>${key.charAt(0).toUpperCase() + key.slice(1)}</h2>
            <pre>${JSON.stringify(value, null, 2)}</pre>
        `).join('')}
    </body>
    </html>`;
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};