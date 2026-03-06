"""
Enhanced LSP — Diagnostics Engine.
Converts compiler errors into LSP Diagnostic objects with debounce.
"""
import threading
import time


class DiagnosticsEngine:
    """Manages debounced diagnostic publishing."""

    def __init__(self, publish_fn, delay=0.15):
        self.publish_fn = publish_fn
        self.delay = delay
        self._timer = None
        self._lock = threading.Lock()

    def schedule(self, uri, doc_store):
        """Schedule a diagnostic run after debounce delay."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(
                self.delay,
                self._run,
                args=(uri, doc_store)
            )
            self._timer.daemon = True
            self._timer.start()

    def _run(self, uri, doc_store):
        """Run analysis and publish diagnostics."""
        doc = doc_store.get(uri)
        if not doc:
            return
        # Re-analyze (document_sync already did this on change)
        diagnostics = doc.diagnostics or []
        self.publish_fn(uri, diagnostics)

    def cancel(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
