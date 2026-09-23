import os
import sys
import unittest
from pathlib import Path

# Ensure root package is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import google.adk.skills._utils as skill_utils

SKILLS_DIR = PROJECT_ROOT / "skills"

EXPECTED_SKILLS = {
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


class TestSkills(unittest.TestCase):
    """Validates all 13 ADK skills in skills/ directory."""

    def test_all_13_skills_exist(self):
        """Verify that all 13 expected skill directories exist under skills/."""
        self.assertTrue(SKILLS_DIR.is_dir(), f"Skills directory not found: {SKILLS_DIR}")
        found_skills = {
            d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
        }
        self.assertEqual(
            found_skills,
            EXPECTED_SKILLS,
            f"Skill directories do not match expected set. Missing: {EXPECTED_SKILLS - found_skills}, Unexpected: {found_skills - EXPECTED_SKILLS}",
        )
        self.assertEqual(len(found_skills), 13)

    def test_skills_validation_with_adk_utils(self):
        """Use google.adk.skills._utils._validate_skill_dir to verify each skill directory."""
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_dir = SKILLS_DIR / skill_name
            with self.subTest(skill=skill_name):
                errors = skill_utils._validate_skill_dir(skill_dir)
                self.assertEqual(
                    errors,
                    [],
                    f"Validation errors for skill '{skill_name}': {errors}",
                )

    def test_skills_loading_and_frontmatter(self):
        """Use google.adk.skills._utils._load_skill_from_dir to verify YAML frontmatter, name, and description."""
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_dir = SKILLS_DIR / skill_name
            with self.subTest(skill=skill_name):
                skill = skill_utils._load_skill_from_dir(skill_dir)
                self.assertIsNotNone(skill, f"Failed to load skill: {skill_name}")
                self.assertEqual(skill.name, skill_name)

                # Frontmatter checks
                self.assertIsNotNone(skill.frontmatter, f"Frontmatter missing for skill: {skill_name}")
                self.assertEqual(skill.frontmatter.name, skill_name)

                # Description checks: non-empty string with meaningful length
                self.assertIsInstance(skill.description, str)
                self.assertGreater(
                    len(skill.description.strip()),
                    20,
                    f"Description is too short or empty for skill '{skill_name}'",
                )

                # Instructions checks: non-empty string with meaningful length
                self.assertIsInstance(skill.instructions, str)
                self.assertGreater(
                    len(skill.instructions.strip()),
                    100,
                    f"Instructions are too short or empty for skill '{skill_name}'",
                )

    def test_skills_contain_schemas(self):
        """Verify that every skill includes osquery schema definitions in its instructions."""
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_dir = SKILLS_DIR / skill_name
            with self.subTest(skill=skill_name):
                skill = skill_utils._load_skill_from_dir(skill_dir)
                instructions_lower = skill.instructions.lower()
                self.assertIn(
                    "schema",
                    instructions_lower,
                    f"Skill '{skill_name}' instructions do not reference schemas",
                )

    def test_os_specific_skills_contain_core_schemas(self):
        """Verify that OS-specific skills contain their platform core table schemas."""
        os_checks = {
            "osquery-darwin": ["launchd", "plist", "alf", "sip_config"],
            "osquery-linux": ["systemd_units", "iptables", "deb_packages", "rpm_packages"],
            "osquery-windows": ["registry", "services", "ntfs_journal_events", "wmi_filter_consumer_binding"],
        }
        for skill_name, expected_tables in os_checks.items():
            skill_dir = SKILLS_DIR / skill_name
            with self.subTest(skill=skill_name):
                skill = skill_utils._load_skill_from_dir(skill_dir)
                for table in expected_tables:
                    self.assertIn(
                        table,
                        skill.instructions,
                        f"Expected table '{table}' not found in {skill_name} instructions",
                    )

    def test_pack_skills_contain_query_catalog(self):
        """Verify that pack skills contain a query catalog and referenced table schemas."""
        pack_skills = [s for s in EXPECTED_SKILLS if s.startswith("pack-")]
        for skill_name in sorted(pack_skills):
            skill_dir = SKILLS_DIR / skill_name
            with self.subTest(skill=skill_name):
                skill = skill_utils._load_skill_from_dir(skill_dir)
                self.assertIn(
                    "Complete Query Catalog",
                    skill.instructions,
                    f"Pack skill '{skill_name}' missing Complete Query Catalog section",
                )
                self.assertIn(
                    "Referenced Table Schemas",
                    skill.instructions,
                    f"Pack skill '{skill_name}' missing Referenced Table Schemas section",
                )


if __name__ == "__main__":
    unittest.main()
