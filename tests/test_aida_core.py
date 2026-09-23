import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure root package is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aida.agent import (
    MODEL,
    A2UI_SYSTEM_INSTRUCTION,
    DynamicSkillToolset,
    root_agent,
    run_osquery,
)
from aida.aida_catalog import get_aida_catalog_config

CUSTOM_AIDA_COMPONENTS = [
    "AidaTable",
    "AidaCard",
    "AidaButton",
    "AidaMetricBar",
    "AidaLogViewer",
    "AidaBarChart",
    "AidaPieChart",
    "AidaLineChart",
    "AidaCpuMeter",
    "AidaMemoryGauge",
    "AidaDiskUsage",
    "AidaNetworkThroughput",
    "AidaSingleSelect",
    "AidaMultipleChoice",
    "AidaTextBox",
    "AidaSlider",
    "AidaColorPicker",
]

LAYOUT_COMPONENTS = ["Column", "Row", "Text"]


class TestAidaCore(unittest.TestCase):
    """Core test suite for AIDA agent configuration, system instruction, catalog schema, and execution tools."""

    def test_agent_initialization(self):
        """Verify AIDA root_agent model is gemini-3.8-flash, thinking config is HIGH, and tools are configured."""
        # 1. Model verification
        self.assertEqual(root_agent.model, "gemini-3.8-flash")
        self.assertEqual(MODEL, "gemini-3.8-flash")
        self.assertEqual(root_agent.name, "aida")

        # 2. Thinking config verification (Low thinking)
        content_config = root_agent.generate_content_config
        self.assertIsNotNone(content_config, "generate_content_config should not be None")
        thinking_config = getattr(content_config, "thinking_config", None)
        self.assertIsNotNone(thinking_config, "thinking_config should not be None")
        thinking_level = getattr(thinking_config, "thinking_level", None)
        self.assertIsNotNone(thinking_level, "thinking_level should not be None")
        self.assertIn("LOW", str(thinking_level).upper())

        # 3. Tools verification: DynamicSkillToolset and run_osquery
        self.assertIsNotNone(root_agent.tools)
        has_dynamic_toolset = any(
            isinstance(tool, DynamicSkillToolset) for tool in root_agent.tools
        )
        self.assertTrue(
            has_dynamic_toolset,
            "root_agent.tools must include an instance of DynamicSkillToolset",
        )
        self.assertIn(
            run_osquery,
            root_agent.tools,
            "root_agent.tools must include run_osquery function",
        )

    def test_a2ui_system_instruction(self):
        """Verify the agent instruction contains A2UI tags, catalog specifications, layout rules, and custom components."""
        # A2UI tags verification
        self.assertIn("<a2ui>", A2UI_SYSTEM_INSTRUCTION)
        self.assertIn("</a2ui>", A2UI_SYSTEM_INSTRUCTION)
        self.assertNotIn("<a2ui-json>", A2UI_SYSTEM_INSTRUCTION)

        # Catalog specification
        self.assertIn("aida_custom", A2UI_SYSTEM_INSTRUCTION)

        # Layout and structural rules
        self.assertIn("side-by-side", A2UI_SYSTEM_INSTRUCTION)
        self.assertIn("FLAT COMPONENT TREE STRUCTURE", A2UI_SYSTEM_INSTRUCTION)
        self.assertIn("Column", A2UI_SYSTEM_INSTRUCTION)
        self.assertIn("Row", A2UI_SYSTEM_INSTRUCTION)

        # Custom components referenced in the system instruction
        for component in CUSTOM_AIDA_COMPONENTS:
            with self.subTest(component=component):
                self.assertIn(
                    component,
                    A2UI_SYSTEM_INSTRUCTION,
                    f"Component '{component}' not found in A2UI_SYSTEM_INSTRUCTION",
                )

        # Persona and dialogue protocol checks
        self.assertIn("What is the nature of the diagnostic emergency?", A2UI_SYSTEM_INSTRUCTION)
        self.assertIn("STRICT MARKDOWN PROHIBITION", A2UI_SYSTEM_INSTRUCTION)

    def test_catalog_schema_components(self):
        """Verify get_aida_catalog_config() provider schema contains custom AIDA components and layouts."""
        catalog_config = get_aida_catalog_config()
        self.assertEqual(catalog_config.name, "aida_custom")

        # Load schema via the catalog config provider
        schema = catalog_config.provider.load()
        self.assertIsInstance(schema, dict)
        self.assertIn("components", schema)

        components = schema["components"]

        # Verify all custom AIDA components exist in the catalog schema
        for comp_name in CUSTOM_AIDA_COMPONENTS:
            with self.subTest(component=comp_name):
                self.assertIn(
                    comp_name,
                    components,
                    f"Custom component '{comp_name}' missing from catalog schema",
                )
                self.assertIsInstance(components[comp_name], dict)

        # Verify basic layout components exist in the catalog schema
        for layout_comp in LAYOUT_COMPONENTS:
            with self.subTest(layout_component=layout_comp):
                self.assertIn(
                    layout_comp,
                    components,
                    f"Layout component '{layout_comp}' missing from catalog schema",
                )

        # Verify count of custom AIDA components is at least 16
        custom_found = [c for c in components if c.startswith("Aida")]
        self.assertGreaterEqual(len(custom_found), 16)

    def test_run_osquery_success(self):
        """Verify run_osquery parses successful JSON query execution."""
        mock_output = '[{"pid": 1, "name": "launchd"}]'
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            result = run_osquery("SELECT pid, name FROM processes WHERE pid = 1")
            self.assertEqual(result, mock_output)
            mock_run.assert_called_once_with(
                ["osqueryi", "--json", "SELECT pid, name FROM processes WHERE pid = 1"],
                capture_output=True,
                text=True,
                timeout=60,
            )

    def test_run_osquery_empty_output(self):
        """Verify run_osquery handles empty output by returning empty JSON array."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = run_osquery("SELECT * FROM processes WHERE pid = 999999")
            self.assertEqual(result, "[]")

    def test_run_osquery_error(self):
        """Verify run_osquery captures and reports execution errors."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Error: near 'SELEC': syntax error"
            )
            result = run_osquery("SELEC * FROM processes")
            self.assertIn("Error running osquery", result)
            self.assertIn("syntax error", result)

    def test_run_osquery_timeout(self):
        """Verify run_osquery handles subprocess TimeoutExpired exception."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="osqueryi", timeout=60)):
            result = run_osquery("SELECT * FROM slow_table")
            self.assertIn("timed out after 60 seconds", result)

    def test_run_osquery_executable_not_found(self):
        """Verify run_osquery handles missing osqueryi binary."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            result = run_osquery("SELECT 1")
            self.assertIn("'osqueryi' executable not found", result)


if __name__ == "__main__":
    unittest.main()
