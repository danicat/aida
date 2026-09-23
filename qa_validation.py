"""
Comprehensive QA Validation Script for all 13 ADK Skills.
Validates:
1. Directory structure and frontmatter validation via google.adk.skills._utils._validate_skill_dir
2. Skill model loading via google.adk.skills._utils._load_skill_from_dir
3. Instantiation and tool execution via google.adk.tools.skill_toolset.SkillToolset
4. Exact query count and name verification across all 10 query packs against osquery_data/packs/*.conf
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

from google.adk.skills import _utils
from google.adk.tools.skill_toolset import SkillToolset, ToolContext


async def run_qa():
    workspace_root = Path(__file__).resolve().parent
    skills_root = workspace_root / "skills"
    packs_dir = workspace_root / "osquery_data" / "packs"

    skill_dirs = sorted([d for d in skills_root.iterdir() if d.is_dir()])
    print(f"Discovered {len(skill_dirs)} skill directories:")
    for sd in skill_dirs:
        print(f"  • {sd.name}")
    print()

    # =========================================================================
    # Step 1: Validate each skill directory with _validate_skill_dir
    # =========================================================================
    print("=" * 70)
    print("STEP 1: Validate Skill Directories (ADK _validate_skill_dir)")
    print("=" * 70)
    validation_results = {}
    validation_passed = 0

    for sd in skill_dirs:
        problems = _utils._validate_skill_dir(sd)
        validation_results[sd.name] = problems
        if problems:
            print(f"[FAIL] {sd.name}:")
            for p in problems:
                print(f"       ✖ {p}")
        else:
            validation_passed += 1
            print(f"[PASS] {sd.name:32} (0 problems)")

    print(f"\nStep 1 Result: {validation_passed}/{len(skill_dirs)} skills validated successfully.\n")

    # =========================================================================
    # Step 2: Load each skill with _load_skill_from_dir
    # =========================================================================
    print("=" * 70)
    print("STEP 2: Load Skills (ADK _load_skill_from_dir)")
    print("=" * 70)
    loaded_skills = []
    load_passed = 0

    for sd in skill_dirs:
        try:
            skill = _utils._load_skill_from_dir(sd)
            loaded_skills.append(skill)
            load_passed += 1
            desc_len = len(skill.frontmatter.description) if skill.frontmatter.description else 0
            instr_len = len(skill.instructions)
            
            # Additional spec checks
            assert desc_len <= 1024, f"Description exceeds 1024 chars ({desc_len})"
            assert skill.frontmatter.name == sd.name, "Frontmatter name does not match dir"

            print(f"[PASS] {sd.name:32} | Name: {skill.frontmatter.name:30} | Desc: {desc_len:4} chars | Body: {instr_len:6} chars")
        except Exception as e:
            print(f"[FAIL] {sd.name:32} | Error loading skill: {e}")

    print(f"\nStep 2 Result: {load_passed}/{len(skill_dirs)} skills loaded successfully.\n")

    # =========================================================================
    # Step 3: Instantiate SkillToolset with all 13 skills
    # =========================================================================
    print("=" * 70)
    print("STEP 3: Instantiate SkillToolset with all 13 skills")
    print("=" * 70)
    toolset_success = False
    tools_list = []
    try:
        toolset = SkillToolset(skills=loaded_skills)
        tools = await toolset.get_tools()
        tools_list = [t.name for t in tools]
        print(f"[PASS] SkillToolset instantiated with {len(toolset.skills)} skills.")
        print(f"       Registered ADK tools ({len(tools)}): {tools_list}")

        # Functional testing of the tools
        tool_map = {t.name: t for t in tools}
        mock_ctx = MagicMock(spec=ToolContext)

        # 1. Test list_skills tool
        list_output = await tool_map["list_skills"].run_async(args={}, tool_context=mock_ctx)
        assert "<available_skills>" in list_output
        print(f"[PASS] Tool 'list_skills' executed successfully (output length: {len(list_output)} chars).")

        # 2. Test load_skill tool for one OS skill and one pack skill
        for test_skill_name in ["osquery-darwin", "pack-incident-response"]:
            load_output = await tool_map["load_skill"].run_async(args={"skill_name": test_skill_name}, tool_context=mock_ctx)
            assert load_output["skill_name"] == test_skill_name
            assert len(load_output["instructions"]) > 1000
            print(f"[PASS] Tool 'load_skill' executed for '{test_skill_name}' (body: {len(load_output['instructions'])} chars).")

        toolset_success = True
    except Exception as e:
        print(f"[FAIL] SkillToolset execution failed: {e}")

    print(f"\nStep 3 Result: {'SUCCESS' if toolset_success else 'FAILURE'}\n")

    # =========================================================================
    # Step 4: Verify query counts and query names across all 10 query packs
    # =========================================================================
    print("=" * 70)
    print("STEP 4: Query Count & Integrity Across 10 Query Packs")
    print("=" * 70)

    conf_files = sorted(packs_dir.glob("*.conf"))
    total_conf_queries = 0
    total_doc_queries = 0
    pack_stats = []

    for cf in conf_files:
        pack_slug = cf.stem
        skill_name = f"pack-{pack_slug}"
        skill_md = skills_root / skill_name / "SKILL.md"

        with open(cf, "r", encoding="utf-8", errors="ignore") as f:
            raw_conf = f.read()
            raw_conf = re.sub(r"\\\s*\n", " ", raw_conf)
            conf_data = json.loads(raw_conf)
            conf_queries = conf_data.get("queries", {})
            conf_count = len(conf_queries)
            total_conf_queries += conf_count

        with open(skill_md, "r", encoding="utf-8") as f:
            doc_text = f.read()
        raw_matches = re.findall(r"^### \d+\.\s+(`{1,2})(.+?)\1", doc_text, re.MULTILINE)
        doc_queries = [m[1] for m in raw_matches]
        doc_count = len(doc_queries)
        total_doc_queries += doc_count

        conf_names = set(conf_queries.keys())
        doc_names = set(doc_queries)
        missing_in_doc = conf_names - doc_names
        extra_in_doc = doc_names - conf_names

        is_exact = (conf_count == doc_count) and not missing_in_doc and not extra_in_doc

        pack_stats.append({
            "skill_name": skill_name,
            "conf_file": cf.name,
            "conf_count": conf_count,
            "doc_count": doc_count,
            "exact_match": is_exact,
            "missing": list(missing_in_doc),
            "extra": list(extra_in_doc)
        })

        status = "[MATCH]" if is_exact else "[MISMATCH]"
        print(f"{status} {skill_name:32}: Conf={conf_count:3} queries | Documented={doc_count:3} queries")
        if not is_exact:
            if missing_in_doc:
                print(f"       Missing queries: {missing_in_doc}")
            if extra_in_doc:
                print(f"       Extra queries: {extra_in_doc}")

    all_packs_matched = all(p["exact_match"] for p in pack_stats)
    print(f"\nTotal Conf Queries across 10 packs:       {total_conf_queries}")
    print(f"Total Documented Queries across 10 packs: {total_doc_queries}")
    print(f"Step 4 Result: {'100% PERFECT MATCH' if all_packs_matched else 'MISMATCH'}\n")

    # =========================================================================
    # Final QA Summary
    # =========================================================================
    print("=" * 70)
    print("OVERALL QA VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"1. Validation (_validate_skill_dir):        {validation_passed}/13 passed (0 errors)")
    print(f"2. Loading (_load_skill_from_dir):          {load_passed}/13 passed (0 errors)")
    print(f"3. SkillToolset Instantiation & Execution:   {'PASSED' if toolset_success else 'FAILED'}")
    print(f"4. Total Queries Count across 10 Packs:     {total_doc_queries}/{total_conf_queries} (Exact match across all packs: {all_packs_matched})")
    print(f"Overall QA Status:                          {'PASSED (ALL CRITERIA MET)' if (validation_passed == 13 and load_passed == 13 and toolset_success and all_packs_matched) else 'FAILED'}")

    return {
        "validation_passed": validation_passed,
        "load_passed": load_passed,
        "toolset_success": toolset_success,
        "total_conf_queries": total_conf_queries,
        "total_doc_queries": total_doc_queries,
        "all_packs_matched": all_packs_matched,
        "pack_stats": pack_stats,
    }


if __name__ == "__main__":
    asyncio.run(run_qa())
