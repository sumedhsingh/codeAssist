const vscode = require('vscode');
const { exec } = require('child_process');

function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.runCodeInsight', function () {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const document = editor.document;
            const fileName = document.fileName;
            const languageId = document.languageId;

            // Map VS Code language IDs to CodeInsight language options
            const languageMap = {
                'python': 'python',
                'javascript': 'javascript',
                // Add more mappings as needed
            };

            const codeInsightLanguage = languageMap[languageId] || 'python';  // Default to Python if unknown

            // Run CodeInsight
            exec(`python path/to/codeinsight.py "${fileName}" --language ${codeInsightLanguage} --structure --complexity --smells --performance --document`, (error, stdout, stderr) => {
                if (error) {
                    vscode.window.showErrorMessage(`CodeInsight error: ${error.message}`);
                    return;
                }
                if (stderr) {
                    vscode.window.showErrorMessage(`CodeInsight stderr: ${stderr}`);
                    return;
                }
                
                // Show results in a new editor tab
                vscode.workspace.openTextDocument({ content: stdout }).then(doc => {
                    vscode.window.showTextDocument(doc, { preview: false });
                });
            });
        }
    });

    context.subscriptions.push(disposable);
}

exports.activate = activate;

function deactivate() {}

exports.deactivate = deactivate;