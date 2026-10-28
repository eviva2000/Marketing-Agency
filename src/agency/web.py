"""Local browser interface for the Offer to Lead Gen to Outbound pipeline."""

import asyncio
import json
import logging
import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from agents import Agent, Runner, SQLiteSession
from agents.items import HandoffOutputItem, ToolCallItem
from dotenv import load_dotenv
from pydantic import BaseModel

from agency.agents.offer_agent import offer_agent
from agency.observability import configure_tracing, run_config

MAX_REQUEST_BYTES = 64 * 1024
MAX_MESSAGE_LENGTH = 10_000
WEB_ASSETS = Path(__file__).parent / "web_ui"
logger = logging.getLogger(__name__)


class _AgentRuntime:
    """Runs all agent calls on one event loop so the shared async client stays loop-bound."""

    def __init__(self) -> None:
        self._ready = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread = threading.Thread(target=self._serve, name="agency-agent-loop", daemon=True)
        self._thread.start()
        self._ready.wait()

    def _serve(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._ready.set()
        loop.run_forever()

    def run(self, agent: Agent, message: str, session: SQLiteSession, group_id: str) -> object:
        if self._loop is None:
            raise RuntimeError("Agent event loop did not start.")

        async def run_agent() -> object:
            return await Runner.run(
                agent,
                message,
                session=session,
                run_config=run_config("Agency Pipeline Web UI", group_id),
            )

        future = asyncio.run_coroutine_threadsafe(run_agent(), self._loop)
        return future.result()


_agent_runtime: _AgentRuntime | None = None
_agent_runtime_lock = threading.Lock()


def _get_agent_runtime() -> _AgentRuntime:
    global _agent_runtime
    with _agent_runtime_lock:
        if _agent_runtime is None:
            _agent_runtime = _AgentRuntime()
        return _agent_runtime


class SessionNotFoundError(Exception):
    """Raised when a request references a conversation that is no longer active."""


@dataclass
class _Conversation:
    session: SQLiteSession
    current_agent: Agent
    trace_id: str
    lock: threading.Lock = field(default_factory=threading.Lock)
    closed: bool = False


def _run_agent_turn(agent: Agent, message: str, session: SQLiteSession, group_id: str) -> object:
    return _get_agent_runtime().run(agent, message, session, group_id)


def _safe_activity(items: list) -> list[dict[str, str]]:
    activity = []
    for item in items:
        if isinstance(item, ToolCallItem):
            activity.append({"type": "tool", "label": "Research tool used"})
        elif isinstance(item, HandoffOutputItem):
            activity.append(
                {
                    "type": "handoff",
                    "label": f"{item.source_agent.name} → {item.target_agent.name}",
                }
            )
    return activity


def _serialize_output(output: object) -> tuple[str, dict | None]:
    if isinstance(output, BaseModel):
        return "Structured result ready.", output.model_dump(mode="json")
    return str(output), None


class ConversationManager:
    """Keeps in-memory SDK sessions and the active agent for local browser conversations."""

    def __init__(
        self,
        run_turn: Callable[[Agent, str, SQLiteSession, str], object] = _run_agent_turn,
        starting_agent: Agent = offer_agent,
    ) -> None:
        self._run_turn = run_turn
        self._starting_agent = starting_agent
        self._conversations: dict[str, _Conversation] = {}
        self._lock = threading.Lock()

    def start(self) -> str:
        session_id = secrets.token_urlsafe(32)
        conversation = _Conversation(
            SQLiteSession(session_id, db_path=":memory:"), self._starting_agent, secrets.token_urlsafe(16)
        )
        with self._lock:
            self._conversations[session_id] = conversation
        return session_id

    def submit(self, session_id: str, message: str) -> dict:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message must not be empty.")
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message must be {MAX_MESSAGE_LENGTH} characters or fewer.")
        conversation = self._get_conversation(session_id)
        with conversation.lock:
            if conversation.closed:
                raise SessionNotFoundError
            result = self._run_turn(
                conversation.current_agent, message.strip(), conversation.session, conversation.trace_id
            )
            conversation.current_agent = result.last_agent
            reply, structured = _serialize_output(result.final_output)
            return {
                "reply": reply,
                "structured": structured,
                "activity": _safe_activity(result.new_items),
                "agent": conversation.current_agent.name,
            }

    def reset(self, session_id: str) -> None:
        with self._lock:
            conversation = self._conversations.pop(session_id, None)
        if conversation is None:
            raise SessionNotFoundError
        with conversation.lock:
            conversation.closed = True
            conversation.session.close()

    def _get_conversation(self, session_id: str) -> _Conversation:
        with self._lock:
            conversation = self._conversations.get(session_id)
        if conversation is None:
            raise SessionNotFoundError
        return conversation

    def close_all(self) -> None:
        with self._lock:
            session_ids = list(self._conversations)
        for session_id in session_ids:
            try:
                self.reset(session_id)
            except SessionNotFoundError:
                pass


def create_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    manager = ConversationManager()

    class Handler(BaseHTTPRequestHandler):
        server_version = "AgencyDemo"

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            assets = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            }
            if path not in assets:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
                return
            filename, content_type = assets[path]
            body = (WEB_ASSETS / filename).read_bytes()
            self._send(HTTPStatus.OK, body, content_type)

        def do_POST(self) -> None:
            if not self._same_origin():
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "Request origin is not allowed."})
                return
            payload = self._read_json()
            if payload is None:
                return
            path = urlsplit(self.path).path
            if path == "/api/sessions":
                self._send_json(HTTPStatus.CREATED, {"session_id": manager.start()})
            elif path == "/api/chat":
                session_id = payload.get("session_id")
                if not isinstance(session_id, str):
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": "A session_id is required."})
                    return
                try:
                    response = manager.submit(session_id, payload.get("message"))
                except SessionNotFoundError:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Conversation expired. Start a new chat."})
                except ValueError as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                except Exception:
                    logger.exception("Browser conversation turn failed")
                    self._send_json(
                        HTTPStatus.BAD_GATEWAY,
                        {
                            "error": (
                                "The assistant request failed. Check the server terminal for details, "
                                "then retry your answer."
                            )
                        },
                    )
                else:
                    self._send_json(HTTPStatus.OK, response)
            else:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

        def do_DELETE(self) -> None:
            if not self._same_origin():
                self._send_json(HTTPStatus.FORBIDDEN, {"error": "Request origin is not allowed."})
                return
            path = urlsplit(self.path).path
            prefix = "/api/sessions/"
            if not path.startswith(prefix) or "/" in path[len(prefix):]:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
                return
            try:
                manager.reset(path[len(prefix):])
            except SessionNotFoundError:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Conversation expired."})
            else:
                self._send_json(HTTPStatus.OK, {"ok": True})

        def _read_json(self) -> dict | None:
            if self.headers.get_content_type() != "application/json":
                self._send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Send application/json."})
                return None
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = MAX_REQUEST_BYTES + 1
            if length < 0 or length > MAX_REQUEST_BYTES:
                self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request is too large."})
                return None
            try:
                payload = json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON."})
                return None
            if not isinstance(payload, dict):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "A JSON object is required."})
                return None
            return payload

        def _same_origin(self) -> bool:
            host = self.headers.get("Host", "").split(":", maxsplit=1)[0].lower()
            if host not in {"127.0.0.1", "localhost"}:
                return False
            origin = self.headers.get("Origin")
            if origin is None:
                return True
            parsed = urlsplit(origin)
            return parsed.scheme == "http" and parsed.netloc.lower() == self.headers.get("Host", "").lower()

        def _send_json(self, status: HTTPStatus, payload: dict) -> None:
            self._send(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

        def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                "img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:
            logger.info("%s request completed", self.command)

    class Server(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

        def server_close(self):
            manager.close_all()
            super().server_close()

    return Server((host, port), Handler)


def main() -> None:
    load_dotenv()
    configure_tracing()
    server = create_server()
    print("Agency web demo running at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
