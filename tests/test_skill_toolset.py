import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure root package is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google.adk.skills import Skill
from google.adk.tools.skill_toolset import SkillToolset
from aida.agent import DynamicSkillToolset, SKILLS_DIR

EXPECTED_SKILL_NAMES = {
    "osquery-darwin",
    "osquery-linux",
    "osquery-windows",
    "pack-hardware-monitoring",
    "pack-incident-response",
    "pack-it-compliance",
    "pack-osquery-monitoring",
    "pack-ossec-rootkit",
    "pack-osx-attacks",
    "pack-unwanted-chrome-extensions",
    "pack-vuln-management",
    "pack-windows-attacks",
    "pack-windows-hardening",
}


class TestSkillToolset(unittest.IsolatedAsyncioTestCase):
    """Tests DynamicSkillToolset and SkillToolset integration."""

    def test_initialization_default(self):
        """Verify default initialization loads skills from default SKILLS_DIR."""
        toolset = DynamicSkillToolset()
        self.assertIsInstance(toolset, SkillToolset)
        self.assertIsInstance(toolset, DynamicSkillToolset)
        self.assertEqual(toolset.skills_dir, SKILLS_DIR.resolve())
        self.assertEqual(
            toolset.tool_filter,
            ["list_skills", "load_skill", "load_skill_resource"],
        )
        self.assertEqual(len(toolset._skills), 13)

    def test_initialization_custom_empty_dir(self):
        """Verify initialization with an empty directory loads 0 skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            toolset = DynamicSkillToolset(skills_dir=tmpdir)
            self.assertEqual(len(toolset._skills), 0)
            self.assertEqual(toolset._list_skills(), [])

    def test_initialization_nonexistent_dir(self):
        """Verify initialization with a non-existent directory handles gracefully."""
        nonexistent = PROJECT_ROOT / "nonexistent_skills_dir_xyz"
        toolset = DynamicSkillToolset(skills_dir=nonexistent)
        self.assertEqual(len(toolset._skills), 0)
        self.assertEqual(toolset._load_from_disk(), [])

    def test_load_from_disk(self):
        """Verify _load_from_disk loads all 13 Skill instances from disk."""
        toolset = DynamicSkillToolset()
        skills = toolset._load_from_disk()
        self.assertIsInstance(skills, list)
        self.assertEqual(len(skills), 13)
        for s in skills:
            self.assertIsInstance(s, Skill)
        loaded_names = {s.name for s in skills}
        self.assertEqual(loaded_names, EXPECTED_SKILL_NAMES)

    async def test_tool_listing(self):
        """Verify get_tools returns the filtered JIT discovery tools: list_skills, load_skill, load_skill_resource."""
        toolset = DynamicSkillToolset()
        tools = await toolset.get_tools()
        self.assertEqual(len(tools), 3)
        tool_names = {t.name for t in tools}
        self.assertEqual(
            tool_names,
            {"list_skills", "load_skill", "load_skill_resource"},
        )

    def test_list_skills(self):
        """Verify _list_skills returns all loaded skills."""
        toolset = DynamicSkillToolset()
        skills = toolset._list_skills()
        self.assertEqual(len(skills), 13)
        skill_names = {s.name for s in skills}
        self.assertEqual(skill_names, EXPECTED_SKILL_NAMES)

    def test_get_skill_existing(self):
        """Verify _get_skill retrieves an existing skill by name."""
        toolset = DynamicSkillToolset()
        skill = toolset._get_skill("osquery-darwin")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.name, "osquery-darwin")

        pack_skill = toolset._get_skill("pack-incident-response")
        self.assertIsNotNone(pack_skill)
        self.assertEqual(pack_skill.name, "pack-incident-response")

    def test_get_skill_nonexistent(self):
        """Verify _get_skill returns None when the skill does not exist."""
        toolset = DynamicSkillToolset()
        skill = toolset._get_skill("nonexistent-skill-name")
        self.assertIsNone(skill)

    def test_dynamic_synchronization(self):
        """Verify DynamicSkillToolset dynamically synchronizes when skills are added to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            toolset = DynamicSkillToolset(skills_dir=tmppath)
            self.assertEqual(len(toolset._list_skills()), 0)
            self.assertIsNone(toolset._get_skill("dynamic-test-skill"))

            # Dynamically add a new skill to the directory
            new_skill_dir = tmppath / "dynamic-test-skill"
            new_skill_dir.mkdir()
            skill_md_content = """---
name: dynamic-test-skill
description: Dynamically loaded diagnostic skill for testing.
---
# Instructions
Run diagnostic commands dynamically.
"""
            (new_skill_dir / "SKILL.md").write_text(skill_md_content)

            # Re-querying should dynamically discover the new skill
            updated_skills = toolset._list_skills()
            self.assertEqual(len(updated_skills), 1)
            self.assertEqual(updated_skills[0].name, "dynamic-test-skill")

            fetched = toolset._get_skill("dynamic-test-skill")
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.name, "dynamic-test-skill")
            self.assertIn("Dynamically loaded", fetched.description)


if __name__ == "__main__":
    unittest.main()
