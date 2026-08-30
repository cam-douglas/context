import os
import signal
import subprocess
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run-sidecar.sh"


class SidecarLaunchTests(unittest.TestCase):
    def test_launch_script_serves_health(self):
        self.assertTrue(SCRIPT.is_file())
        port = "8767"
        env = os.environ.copy()
        env["CONTEXT_SIDECAR_PORT"] = port
        proc = subprocess.Popen(["/bin/bash", str(SCRIPT)], env=env, start_new_session=True)
        try:
            body = ""
            for _ in range(40):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=0.4) as response:
                        body = response.read().decode()
                        break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(0.1)
            self.assertIn('"ok"', body)
        finally:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
