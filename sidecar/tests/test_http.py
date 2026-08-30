import json
import os
import threading
import unittest

os.environ.setdefault("CONTEXT_GENERATOR", "pedalboard")
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from context_sidecar.http import BIND_HOST, handle_intent, health_payload, make_server, ready_payload
from context_sidecar.intent import empty_intent


class HttpUnitTests(unittest.TestCase):
    def test_health_payload(self):
        self.assertEqual(health_payload()["ok"], True)
        ready = ready_payload()
        self.assertTrue(ready["ok"])
        self.assertIn("id", ready["generator"])

    def test_intent_echo_and_preview(self):
        status, payload = handle_intent(empty_intent(prompt="add a bridge"))
        self.assertEqual(status, 200)
        self.assertEqual(payload["intent"]["prompt"], "add a bridge")
        self.assertIn("sections", payload["preview"])

    def test_empty_prompt_is_400(self):
        intent = empty_intent()
        intent["prompt"] = ""
        status, payload = handle_intent(intent)
        self.assertEqual(status, 400)
        self.assertIn("prompt", payload["error"])

    def test_drop_in_wrong_mode_is_400(self):
        intent = empty_intent()
        intent["drop_in"] = {"file_path": "/tmp/loop.wav"}
        status, _payload = handle_intent(intent)
        self.assertEqual(status, 400)


class HttpServerTests(unittest.TestCase):
    def setUp(self):
        os.environ["CONTEXT_COMPOSE_ON_INTENT"] = "0"
        self.server = make_server(0)
        self.port = self.server.server_address[1]
        self.assertEqual(self.server.server_address[0], BIND_HOST)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _url(self, path: str) -> str:
        return f"http://{BIND_HOST}:{self.port}{path}"

    def test_get_health(self):
        with urlopen(self._url("/health")) as response:
            body = json.loads(response.read().decode("utf-8"))
        self.assertEqual(response.status, 200)
        self.assertTrue(body["ok"])

    def test_get_progress(self):
        with urlopen(self._url("/progress")) as response:
            body = json.loads(response.read().decode("utf-8"))
        self.assertEqual(response.status, 200)
        self.assertIn("active", body)
        self.assertIn("eta_sec", body)
        self.assertIn("preview_ready", body)

    def test_post_intent(self):
        payload = json.dumps(empty_intent(prompt="expand on this riff")).encode("utf-8")
        request = Request(self._url("/intent"), data=payload, method="POST")
        request.add_header("Content-Type", "application/json")
        with urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
        self.assertTrue(body["ok"])
        self.assertEqual(body["intent"]["prompt"], "expand on this riff")
        self.assertNotIn("compose", body)

    def test_post_export_writes_als(self):
        import tempfile
        from pathlib import Path

        fixtures = Path(__file__).resolve().parents[2] / "fixtures"
        with tempfile.TemporaryDirectory() as dest:
            payload = json.dumps(
                {
                    "dest_dir": dest,
                    "midi_path": str(fixtures / "empty.mid"),
                    "stem_paths": [str(fixtures / "silence.wav")],
                    "slug": "HttpExport",
                }
            ).encode("utf-8")
            request = Request(self._url("/export"), data=payload, method="POST")
            request.add_header("Content-Type", "application/json")
            with urlopen(request) as response:
                body = json.loads(response.read().decode("utf-8"))
            self.assertTrue(body["wrote_als"], body)
            self.assertTrue(Path(body["session"]["als_path"]).is_file())

    def test_post_empty_prompt_http_400(self):
        intent = empty_intent()
        intent["prompt"] = "  "
        request = Request(
            self._url("/intent"),
            data=json.dumps(intent).encode("utf-8"),
            method="POST",
        )
        request.add_header("Content-Type", "application/json")
        with self.assertRaises(HTTPError) as raised:
            urlopen(request)
        self.assertEqual(raised.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
