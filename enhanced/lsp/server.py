#!/usr/bin/env python3
"""
Enhanced Language Server — LSP over stdin/stdout using JSON-RPC 2.0.
Python stdlib only. No external dependencies.

Launch: python lsp/server.py
   or:  enhanced --lsp
"""
import json
import sys
import os
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lsp.handlers import LSPHandlers


class LSPServer:
    """JSON-RPC 2.0 Language Server over stdin/stdout."""

    def __init__(self):
        self._lock = threading.Lock()
        self.handlers = LSPHandlers(self._send_notification)
        self._running = True

    def run(self):
        """Main loop: read JSON-RPC messages from stdin, dispatch, respond."""
        while self._running:
            try:
                message = self._read_message()
                if message is None:
                    break
                self._handle_message(message)
            except Exception as e:
                self._log(f"Server error: {e}")

    def _read_message(self):
        """Read one LSP message (Content-Length header + JSON body)."""
        headers = {}
        while True:
            line = sys.stdin.buffer.readline()
            if not line:
                return None  # EOF
            line = line.decode('utf-8').rstrip('\r\n')
            if line == '':
                break  # End of headers
            if ':' in line:
                key, val = line.split(':', 1)
                headers[key.strip()] = val.strip()

        content_length = int(headers.get('Content-Length', '0'))
        if content_length == 0:
            return None

        body = sys.stdin.buffer.read(content_length)
        if not body:
            return None

        try:
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            self._send_error(None, -32700, f"Parse error: {e}")
            return None

    def _handle_message(self, msg):
        """Dispatch a JSON-RPC message."""
        method = msg.get('method')
        params = msg.get('params', {})
        msg_id = msg.get('id')

        if method is None and msg_id is not None:
            # This is a response — we don't send requests, ignore
            return

        if method is None:
            return

        try:
            result = self.handlers.dispatch(method, params)
        except SystemExit:
            raise
        except Exception as e:
            if msg_id is not None:
                self._send_error(msg_id, -32603, str(e))
            return

        # Notifications (no id) don't get a response
        if msg_id is not None:
            self._send_response(msg_id, result)

        # Handle exit
        if method == 'exit':
            self._running = False

    def _send_response(self, msg_id, result):
        """Send a JSON-RPC success response."""
        response = {
            'jsonrpc': '2.0',
            'id': msg_id,
            'result': result
        }
        self._write_message(response)

    def _send_error(self, msg_id, code, message):
        """Send a JSON-RPC error response."""
        response = {
            'jsonrpc': '2.0',
            'id': msg_id,
            'error': {
                'code': code,
                'message': message
            }
        }
        self._write_message(response)

    def _send_notification(self, method, params):
        """Send a JSON-RPC notification (no id)."""
        notification = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }
        self._write_message(notification)

    def _write_message(self, obj):
        """Write a JSON-RPC message with Content-Length framing."""
        body = json.dumps(obj, ensure_ascii=False)
        body_bytes = body.encode('utf-8')
        header = f"Content-Length: {len(body_bytes)}\r\n\r\n"
        with self._lock:
            sys.stdout.buffer.write(header.encode('ascii'))
            sys.stdout.buffer.write(body_bytes)
            sys.stdout.buffer.flush()

    def _log(self, message):
        """Log to stderr (visible to editor, not mixed with LSP protocol)."""
        sys.stderr.write(f"[enhanced-lsp] {message}\n")
        sys.stderr.flush()


def main():
    server = LSPServer()
    server.run()


if __name__ == '__main__':
    main()
