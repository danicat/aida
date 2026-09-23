import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aida.agent import run_osquery


class TestOSQueryLiveIntegration(unittest.TestCase):
    """Integration and resilience tests for aida.agent.run_osquery."""

    def test_system_info(self):
        """Test system_info query: hostname, cpu_brand, physical_memory."""
        query = "SELECT hostname, cpu_brand, physical_memory FROM system_info;"
        raw_res = run_osquery(query)
        self.assertIsInstance(raw_res, str)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertIn("hostname", row)
        self.assertIn("cpu_brand", row)
        self.assertIn("physical_memory", row)
        self.assertTrue(len(row["hostname"]) > 0)
        self.assertTrue(len(row["cpu_brand"]) > 0)
        self.assertTrue(int(row["physical_memory"]) > 0)

    def test_os_version(self):
        """Test os_version query: name, version, build."""
        query = "SELECT name, version, build FROM os_version;"
        raw_res = run_osquery(query)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertIn("name", row)
        self.assertIn("version", row)
        self.assertIn("build", row)
        self.assertTrue(len(row["name"]) > 0)
        self.assertTrue(len(row["version"]) > 0)
        self.assertTrue(len(row["build"]) > 0)

    def test_uptime(self):
        """Test uptime query: total_seconds."""
        query = "SELECT total_seconds FROM uptime;"
        raw_res = run_osquery(query)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertIn("total_seconds", row)
        self.assertGreater(int(row["total_seconds"]), 0)

    def test_processes(self):
        """Test processes query for PID 1 (launchd on macOS / systemd on Linux)."""
        query = "SELECT pid, name, path FROM processes WHERE pid = 1;"
        raw_res = run_osquery(query)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        row = data[0]
        self.assertEqual(row["pid"], "1")
        self.assertIn("name", row)
        self.assertIn("path", row)
        self.assertTrue(len(row["name"]) > 0)

    def test_mounts(self):
        """Test mounts query: path, type, blocks, blocks_available LIMIT 3."""
        query = "SELECT path, type, blocks, blocks_available FROM mounts LIMIT 3;"
        raw_res = run_osquery(query)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        for row in data:
            self.assertIn("path", row)
            self.assertIn("type", row)
            self.assertIn("blocks", row)
            self.assertIn("blocks_available", row)

    def test_invalid_table_error_handling(self):
        """Test error handling for non-existent table / column."""
        query = "SELECT foo_bar_invalid FROM invalid_table;"
        raw_res = run_osquery(query)
        self.assertTrue(raw_res.startswith("Error running osquery:"))
        self.assertIn("no such table: invalid_table", raw_res)

    def test_malformed_sql_error_handling(self):
        """Test error handling for malformed SQL syntax."""
        query = "SELECT * FROM ;"
        raw_res = run_osquery(query)
        self.assertTrue(raw_res.startswith("Error running osquery:"))
        self.assertIn("syntax error", raw_res)

    def test_empty_result_set(self):
        """Test empty result set returns parseable empty JSON list."""
        query = "SELECT * FROM processes WHERE pid = 99999999;"
        raw_res = run_osquery(query)
        data = json.loads(raw_res)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_timeout_resilience_mock(self):
        """Test that subprocess.TimeoutExpired is handled gracefully."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="osqueryi", timeout=60)):
            res = run_osquery("SELECT * FROM processes;")
            self.assertEqual(
                res,
                "Error: Query timed out after 60 seconds (table might be too slow or locked)."
            )

    def test_timeout_resilience_live_subprocess(self):
        """Test real OS subprocess timeout by wrapping subprocess.run with micro-timeout."""
        orig_run = subprocess.run

        def run_fast_timeout(*args, **kwargs):
            kwargs["timeout"] = 0.00001
            return orig_run(*args, **kwargs)

        with patch("subprocess.run", side_effect=run_fast_timeout):
            res = run_osquery("SELECT * FROM processes;")
            self.assertEqual(
                res,
                "Error: Query timed out after 60 seconds (table might be too slow or locked)."
            )

    def test_missing_executable_resilience(self):
        """Test that FileNotFoundError when osqueryi is missing is handled cleanly."""
        with patch("subprocess.run", side_effect=FileNotFoundError("Executable not found")):
            res = run_osquery("SELECT 1;")
            self.assertEqual(
                res,
                "Error: 'osqueryi' executable not found. Is it installed and in your PATH?"
            )

    def test_unexpected_exception_resilience(self):
        """Test generic unexpected exceptions are trapped without crashing."""
        with patch("subprocess.run", side_effect=OSError("Process spawning error")):
            res = run_osquery("SELECT 1;")
            self.assertEqual(res, "Unexpected error running osquery: Process spawning error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
