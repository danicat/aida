import asyncio
import json
import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from ag_ui.core import (
    EventType,
    RunStartedEvent,
    TextMessageStartEvent,
    TextMessageContentEvent,
    RunFinishedEvent,
)
from main import app, adk_agent


class TestAgUiStreaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_system_status_response_structure(self):
        """Verify system status contains complete metric fields for UI header."""
        resp = self.client.get("/api/system-status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["health"], "NOMINAL")
        self.assertIn("uptime_str", data)
        self.assertIn("percent", data["cpu"])
        self.assertIn("count", data["cpu"])
        self.assertIn("total", data["memory"])
        self.assertIn("used", data["memory"])
        self.assertIn("percent", data["memory"])

    def test_session_clear(self):
        """Verify /session/clear resets cleanly."""
        resp = self.client.post("/session/clear")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_chat_sse_stream_mocked(self):
        """Verify /chat endpoint streams valid SSE events conforming to AG-UI protocol."""
        async def fake_run(input_data):
            yield RunStartedEvent(thread_id="test", run_id="run-1")
            yield TextMessageStartEvent(message_id="msg-1", role="assistant")
            yield TextMessageContentEvent(message_id="msg-1", delta="Hello! AIDA is ready.")
            yield RunFinishedEvent(thread_id="test", run_id="run-1")

        with patch.object(adk_agent, "run", side_effect=fake_run):
            with self.client.stream("POST", "/chat", json={"query": "hello"}) as resp:
                self.assertEqual(resp.status_code, 200)
                self.assertIn("text/event-stream", resp.headers["content-type"])
                
                events = []
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        payload = line[len("data:"):].strip()
                        if payload:
                            events.append(json.loads(payload))
                
                event_types = [e.get("type") for e in events]
                self.assertIn(EventType.RUN_STARTED, event_types)
                self.assertIn(EventType.TEXT_MESSAGE_START, event_types)
                self.assertIn(EventType.TEXT_MESSAGE_CONTENT, event_types)
                self.assertIn(EventType.RUN_FINISHED, event_types)
                
                text_content = next(e for e in events if e.get("type") == EventType.TEXT_MESSAGE_CONTENT)
                self.assertEqual(text_content["delta"], "Hello! AIDA is ready.")


if __name__ == "__main__":
    unittest.main()
