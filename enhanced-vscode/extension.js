// Enhanced Language — VSCode Extension Entry Point
// Spawns the Enhanced LSP server and connects via stdio.

const path = require('path');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');
const vscode = require('vscode');

let client;

function activate(context) {
    const config = vscode.workspace.getConfiguration('enhanced.lsp');
    const pythonPath = config.get('pythonPath', 'python');

    // Find the LSP server script
    let serverPath = config.get('path', '');
    if (!serverPath) {
        // Auto-detect: look relative to extension, or in common install paths
        const candidates = [
            path.join(__dirname, '..', 'enhanced', 'lsp', 'server.py'),
            path.join(__dirname, '..', 'lsp', 'server.py'),
            '/usr/local/lib/enhanced/lsp/server.py',
            'C:\\Program Files\\Enhanced\\lsp\\server.py',
        ];
        for (const p of candidates) {
            try {
                require('fs').accessSync(p);
                serverPath = p;
                break;
            } catch { }
        }
    }

    if (!serverPath) {
        vscode.window.showWarningMessage(
            'Enhanced LSP server not found. Set enhanced.lsp.path in settings.'
        );
        return;
    }

    const serverOptions = {
        command: pythonPath,
        args: [serverPath],
        transport: TransportKind.stdio,
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'enhanced' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.en'),
        },
    };

    client = new LanguageClient(
        'enhanced-lsp',
        'Enhanced Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
    context.subscriptions.push(client);
}

function deactivate() {
    if (client) {
        return client.stop();
    }
}

module.exports = { activate, deactivate };
