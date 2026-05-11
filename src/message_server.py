import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from PyQt5.QtCore import QObject, pyqtSignal


class MessageServer(QObject):
    message_received = pyqtSignal(str, str, str, str)  # sender, content, date, conversation
    status_changed = pyqtSignal(bool, str)              # running, info_text
    error_occurred = pyqtSignal(str)

    def __init__(self, port: int = 774):
        super().__init__()
        self.port = port
        self._http_server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._http_server is not None

    def start(self, port: int | None = None) -> bool:
        if self.running:
            return True
        if port is not None:
            self.port = port

        emitter = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path not in ("/message", "/message/"):
                    self._respond(404, {"error": "use POST /message"})
                    return
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8", errors="replace")

                ct = self.headers.get("Content-Type", "")
                if "json" in ct:
                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        self._respond(400, {"error": "invalid JSON"})
                        return
                else:
                    self._respond(400, {"error": "Content-Type: application/json required"})
                    return

                sender       = str(data.get("sender",       "")).strip()
                content      = str(data.get("content",      "")).strip()
                date         = str(data.get("date",         "")).strip()
                conversation = str(data.get("conversation", "")).strip()

                if not (sender and content and date and conversation):
                    self._respond(400, {"error": "sender, content, date and conversation are required"})
                    return

                emitter.message_received.emit(sender, content, date, conversation)
                self._respond(200, {"status": "ok", "sender": sender, "conversation": conversation})

            def do_GET(self):
                if self.path in ("/", "/health"):
                    self._respond(200, {"status": "AIApp message server running"})
                else:
                    self._respond(404, {"error": "not found"})

            def _respond(self, code: int, body: dict):
                payload = json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        try:
            self._http_server = HTTPServer(("0.0.0.0", self.port), Handler)
            self._thread = threading.Thread(
                target=self._http_server.serve_forever, daemon=True
            )
            self._thread.start()
            self.status_changed.emit(True, f"Listening on port {self.port}")
            return True
        except OSError as e:
            self._http_server = None
            self.error_occurred.emit(f"Could not start server: {e}")
            return False

    def stop(self):
        if self._http_server:
            self._http_server.shutdown()
            self._http_server = None
        self.status_changed.emit(False, "Server stopped")
