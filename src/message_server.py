import socket
import threading
from PyQt5.QtCore import QObject, pyqtSignal


def parse_message(raw: str) -> dict | None:
    """Parse a message in the key:value line format."""
    fields = {}
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip().lower()] = value.strip()
    if "sender" in fields and "content" in fields and "date" in fields:
        return fields
    return None


class MessageServer(QObject):
    message_received = pyqtSignal(str, str, str)   # sender, content, date
    status_changed = pyqtSignal(bool, str)          # running, info_text
    error_occurred = pyqtSignal(str)

    def __init__(self, port: int = 774):
        super().__init__()
        self.port = port
        self._running = False
        self._server_socket: socket.socket | None = None
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._running

    def start(self, port: int | None = None) -> bool:
        if self._running:
            return True
        if port is not None:
            self.port = port
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", self.port))
            self._server_socket.listen(10)
            self._server_socket.settimeout(1.0)
            self._running = True
            self._thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._thread.start()
            self.status_changed.emit(True, f"Listening on port {self.port}")
            return True
        except OSError as e:
            self.error_occurred.emit(f"Could not start server: {e}")
            return False

    def stop(self):
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None
        self.status_changed.emit(False, "Server stopped")

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                threading.Thread(
                    target=self._handle_client, args=(conn, addr), daemon=True
                ).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_client(self, conn: socket.socket, addr):
        try:
            chunks = []
            conn.settimeout(5.0)
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                chunks.append(data)
            raw = b"".join(chunks).decode("utf-8", errors="replace")
            msg = parse_message(raw)
            if msg:
                self.message_received.emit(msg["sender"], msg["content"], msg["date"])
                conn.sendall(b"OK\n")
            else:
                conn.sendall(b"ERR: invalid format\n")
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
