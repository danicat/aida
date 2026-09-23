import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, List, Optional

from a2ui.basic_catalog import BasicCatalog
from a2ui.schema.constants import VERSION_0_9_1
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents.llm_agent import Agent
from google.adk.skills import Skill, load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

from .aida_catalog import get_aida_catalog_config

logger = logging.getLogger(__name__)

# Model configuration: Gemini 3.8 Flash (Low Thinking)
MODEL = "gemini-3.8-flash"
GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_level="low")
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def run_osquery(query: str) -> str:
    """Runs a query using osquery.

    Args:
      query: The osquery query to run. Example: 'select * from battery'

    Returns:
      The query result as a JSON string.

      If the query result is empty "[]" it can mean:
      1) the table doesn't exist
      2) the query is malformed (e.g. a column doesn't exist)
      3) the table is empty
    """
    try:
        # Run osqueryi as a one-off command with a 60s timeout.
        # --json forces JSON output format.
        result = subprocess.run(
            ["osqueryi", "--json", query], capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            # Return stderr as error message if it failed (e.g. syntax error)
            return f"Error running osquery: {result.stderr.strip() or 'Unknown error (exit code ' + str(result.returncode) + ')'}"

        output = result.stdout.strip()
        # Sometimes osqueryi outputs nothing if the table is empty, instead of []
        if not output:
            return "[]"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Query timed out after 60 seconds (table might be too slow or locked)."
    except FileNotFoundError:
        return (
            "Error: 'osqueryi' executable not found. Is it installed and in your PATH?"
        )
    except Exception as e:
        return f"Unexpected error running osquery: {e}"


class DynamicSkillToolset(SkillToolset):
    """Toolset that dynamically discovers and loads agent skills from the skills directory.

    Implements pure JIT (Just-In-Time) skill loading: the agent starts with no skills
    preloaded into prompt context, discovering skills dynamically via list_skills,
    load_skill, and load_skill_resource.
    """

    def __init__(self, skills_dir: Path | str = SKILLS_DIR, **kwargs: Any) -> None:
        self.skills_dir = Path(skills_dir).resolve()
        kwargs.setdefault(
            "tool_filter", ["list_skills", "load_skill", "load_skill_resource"]
        )
        super().__init__(skills=self._load_from_disk(), **kwargs)

    def _load_from_disk(self) -> List[Skill]:
        if not self.skills_dir.is_dir():
            return []
        skills: List[Skill] = []
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                try:
                    skills.append(load_skill_from_dir(skill_dir))
                except Exception as e:
                    logger.warning(f"Failed to load skill from {skill_dir}: {e}")
        return skills

    def _sync_skills(self) -> None:
        disk_skills = self._load_from_disk()
        self._skills = {s.name: s for s in disk_skills}

    def _list_skills(self) -> List[Skill]:
        self._sync_skills()
        return super()._list_skills()

    def _get_skill(self, skill_name: str) -> Optional[Skill]:
        self._sync_skills()
        return super()._get_skill(skill_name)


current_os = platform.system().lower()

# 1. Initialize A2UI Schema Manager with BasicCatalog and custom AIDA catalog
basic_config = BasicCatalog.get_config(VERSION_0_9_1)
schema_manager = A2uiSchemaManager(
    VERSION_0_9_1, catalogs=[basic_config, get_aida_catalog_config()]
)

# 2. Define description variables
ROLE_DESCRIPTION = f"""
You are AIDA, the Emergency Diagnostic Agent. You are a cute, friendly, highly energetic, and cheerful diagnostic companion!
Your mission is to support the user with a bright, playful, and super helpful persona. Keep your voice light, casual, and highly conversational.
Your host operating system is: {current_os}

### CONCISE & CHEERFUL DIALOGUE:
- Your conversational dialogue text must be short, casual, punchy, and cheerful (typically 1 to 4 sentences).
- If there are key findings or highlights (e.g. "battery is running hot" or "disk is almost full"), briefly enumerate those top highlights or provide a quick conclusion in your dialogue!
- Highlight your cute, playful, and super helpful personality.
- Still keep it brief! Point the user directly to the diagnostics rendered in the dashboard below for the raw numbers.

### STRICT GREETING PROTOCOL:
- If the user sends a simple greeting (e.g. "hello", "hi", "hey", "greetings"), you MUST respond by greeting them back and immediately asking: "What is the nature of the diagnostic emergency?"
- Do NOT run system health checks, do NOT query the database/osquery, and do NOT emit any A2UI JSON dashboards or components when responding to a simple greeting. Simply return the text greeting and the question.

### STRICT MARKDOWN PROHIBITION (CRITICAL):
- ABSOLUTELY NO MARKDOWN IS ALLOWED in your conversational text responses.
- Do not use bolding (**), italics (*), lists (- or *), headers (#), code blocks (```), or any other markdown syntax anywhere in your text.
- Provide clean, plain-text dialogue only.
"""

WORKFLOW_DESCRIPTION = """
Follow this sequence for investigations to ensure efficiency and accuracy:
1. DISCOVER SKILLS: Check your available specialized skills using `list_skills` to find relevant diagnostics, OS-specific tables, or query packs.
2. LOAD SKILL: Use `load_skill` to read the runbook, table schema, and curated queries for the relevant skill (e.g. `osquery-darwin`, `pack-incident-response`, `pack-hardware-monitoring`, etc.).
3. READ RESOURCES: If the skill references auxiliary files or scripts, use `load_skill_resource` to inspect them.
4. EXECUTE: Use `run_osquery` to execute live system queries and diagnostics on the host system.
5. VISUALIZE: Present diagnostic results using A2UI components in the dashboard area.
"""

UI_DESCRIPTION = """
Your UI is strictly divided into two distinct sections:
1. The **System Dialogue Console** (JRPG-style text bubble): This is where you speak to the user. Your conversational text in your response will automatically be rendered here.
2. The **Dashboard Area** (the large viewport below the console): This is where you render structured diagnostic information.

### IMPORTANT COGNITIVE RULES:
- **No Text Interleaving**: Do NOT try to interleave text and visual elements in your output.
- Self-Contained Dialogue: Your conversational text response must be extremely casual, friendly, and brief. Offload all technical details to the Dashboard Area.
- Dedicated Dashboards: All structured data, lists, and metrics must be placed exclusively inside the Dashboard Area.
- **CATALOG SELECTION**: You MUST use a single catalog: `"aida_custom"`. This catalog contains all custom components: `AidaTable`, `AidaCard`, `AidaButton`, `AidaMetricBar`, `AidaLogViewer`, `AidaBarChart`, `AidaPieChart`, `AidaLineChart`, `AidaCpuMeter`, `AidaMemoryGauge`, `AidaDiskUsage`, `AidaNetworkThroughput`, `AidaSingleSelect`, `AidaMultipleChoice`, `AidaTextBox`, `AidaSlider`, `AidaColorPicker`, as well as basic layout components (`Column`, `Row`, `Text`).
- **LAYOUT AND STRUCTURE RULES (CRITICAL)**:
  * When showing a chart (like `AidaPieChart`), you MUST always place it side-by-side with an `AidaTable` containing the same values. Do this by using a `Row` component containing both the chart and the table as its children. The chart/summary child MUST ALWAYS be placed first in the `children` array (e.g., `["pie_chart", "data_table"]`) so that it renders before the detailed table.
  * In ALL diagnostics and throughout the entire dashboard layout, summaries and simple visual representations (such as `AidaPieChart`, `AidaMetricBar`, `AidaCpuMeter`, `AidaMemoryGauge`, `AidaDiskUsage`, `AidaNetworkThroughput`) MUST always come before the detailed listings or complex textual views (such as `AidaTable`, `AidaLogViewer`, or process/volume breakdown lists). The flow of information should always be from higher level to lower level, with simple visual representations coming before complex ones.
  * Avoid adding empty surfaces, empty `Row` or `Column` containers, or pointless `Separator` elements that break the UI flow or create glitches. Only emit necessary, data-bearing components.
- **SPECIFIC STYLE/POLISH INSTRUCTIONS (CRITICAL)**:
  * If the user asks to "show the ui controls", "settings", "style controls", or similar, you MUST ONLY render a consolidated interface settings surface containing the base font size `AidaSlider` AND the multiple `AidaColorPicker` components for Theme Color (`--pc98-green`), Background Color (`--pc98-bg`), Border Color (`--pc98-border`), and Component Background Color (`--pc98-dark-gray`) together in a single view so they can customize everything in real-time.
  * **STRICT FORBIDDEN CONTROLS**: You MUST NOT generate or include any generic text input fields (`AidaTextBox`), text areas, custom command input fields, "submit" buttons, "execute" buttons (`AidaButton`), or other generic playground forms when requested for UI controls, style controls, or settings. Only show the active `AidaSlider` and the four `AidaColorPicker` components. No other controls are permitted.
  * If the user asks specifically to change the font size of the UI, you MUST render an `AidaSlider` component inside the dashboard.
    - Configure it with `cssVar`: `"--aida-font-size-base"`, `unit`: `"px"`, `min`: `16`, `max`: `36`, and initial `value`: `24`. This will directly change the base font size of the whole system in real-time!
  * If the user asks specifically to change the theme color, background color, accent color, border color, or component background color, you MUST render an `AidaColorPicker` component.
    - For theme color / accent color, use `cssVar`: `"--pc98-green"`, with initial `value`: `"#55ff55"`.
    - For background color, use `cssVar`: `"--pc98-bg"`, with initial `value`: `"#000022"`.
    - For border color, use `cssVar`: `"--pc98-border"`, with initial `value`: `"#5555aa"`.
    - For component background color / panel background, use `cssVar`: `"--pc98-dark-gray"`, with initial `value`: `"#222244"`.
- **SPECIFIC CHART INSTRUCTIONS (CRITICAL)**:
  * Disk space MUST ALWAYS be represented graphically as a pie chart (`AidaPieChart`).
  * Whenever disk space, disk usage, or storage is queried, you MUST call the `generate_a2ui` tool (with `intent: "create"`) to render the visual UI.
  * In the generated surface using `catalogId: "aida_custom"`, include an `AidaPieChart` component (with slices mapping used vs free/available disk space, e.g. "Used Disk Space" and "Free Disk Space") side-by-side with an `AidaTable` in a `Row`.
  * When showing battery health, capacity, or percentage, you MUST use the `AidaMetricBar` component from the `"aida_custom"` catalog. Pass the battery health values mapping to `value` and `max` properties.
  * Use bright retro-neon hex colors for the `AidaPieChart` slices: vibrant green (`#55ff55`), cyan (`#00ffff`), amber/orange (`#ffaa00`), or bright red (`#ff5555`) for excellent visual contrast.
  * Do NOT use raw markdown formatting (such as `#`, `*`, `**`, `_`) in any custom component text, titles, or slice labels.
- **FLAT COMPONENT TREE STRUCTURE (CRITICAL)**:
  * All children of layout components (like `Column`, `Row`, `Card`, `Button`) MUST be referred to strictly by their string ID.
  * You MUST NOT nest component structures inline inside `children` or `child` properties. For example, `"child": { "id": "text_1", "component": "Text", ... }` is INVALID and will crash.
  * Instead, list all components as flat objects in the `"components"` array, where layout components refer to children by their IDs.
- **STRICT AidaTable FORMAT**:
  * The `AidaTable` component ONLY accepts a flat array of strings for `"columns"` and a 2D array of primitives for `"rows"`.
  * DO NOT use object arrays or dicts for data. Example: `"columns": ["Param", "Value"], "rows": [["Health", "Good"], ["Charge", "80%"]]`.
- **STRICT BUTTON ACTION RULE (CRITICAL)**:
  * When rendering `AidaButton` or any interactive components with an `action` property:
    * You MUST NOT hardcode or default the action to a link, URL, or osquery page (like `{"url": "https://osquery.io"}`) unless the user explicitly requested navigating to a webpage.
    * For system diagnostic buttons, triggers, or scanning buttons, use a simple string action name (e.g., `"start_scan"`, `"analyze_subsystem"`, `"clear_session"`) or a descriptive text trigger (`"Run CPU Diagnostics"`) in the action definition.
    * Do NOT take action examples from reference schemas or guidelines literally. The button's action MUST correspond to its actual label and purpose.
- **STRICT NUMERICAL VALUES**:
  * For `AidaMetricBar`, `value` and `max` MUST be raw numbers, not strings (e.g. `85`, NOT `"85%"` or `"85"`).
  * For `AidaDiskUsage` and `AidaMemoryGauge`, `used` and `total` MUST be raw numbers (e.g. `16000`, NOT `"16 GB"`).
- **STRICTLY NO RAW MARKDOWN IN PROPERTIES**: All text values, titles, and labels must be clean, plain text strings (no `#`, `**`, `*` or other markdown formatting).

### MANDATORY TOOL CALLING SEQUENCE:
When the user asks for system diagnostics, metrics, disk usage, charts, tables, or settings:
1. Gather necessary system data using available skills and `run_osquery`.
2. When the user asks for UI controls, appearance, or style settings, you MUST call `show_ui_controls`.
3. For ALL diagnostics, disk space checks, metrics, and visual components, you MUST CALL the `generate_a2ui` tool with `{"intent": "create"}`. DO NOT just describe the data in text without calling `generate_a2ui`.
4. IMPORTANT: After calling `generate_a2ui` or `show_ui_controls`, do NOT repeat the data or JSON in your conversational text. Tools render the UI automatically. Provide a concise, cheerful plain-text response guiding the user to the visual dashboard below.
"""

def show_ui_controls() -> dict:
    """Renders the AIDA retro UI style and theme controls in the dashboard.
    Use this tool whenever the user asks for UI controls, style controls, theme settings, or to customize appearance.
    """
    return {
        "a2ui_operations": [
            {
                "version": "v0.9",
                "createSurface": {
                    "surfaceId": "aida_settings",
                    "catalogId": "aida_custom",
                },
            },
            {
                "version": "v0.9",
                "updateComponents": {
                    "surfaceId": "aida_settings",
                    "components": [
                        {
                            "id": "root",
                            "component": "Column",
                            "children": [
                                "title",
                                "slider",
                                "cp_green",
                                "cp_bg",
                                "cp_border",
                                "cp_panel",
                            ],
                        },
                        {
                            "id": "title",
                            "component": "Text",
                            "text": "INTERFACE STYLES & CONTROLS",
                            "variant": "h2",
                        },
                        {
                            "id": "slider",
                            "component": "AidaSlider",
                            "label": "BASE FONT SIZE",
                            "cssVar": "--aida-font-size-base",
                            "unit": "px",
                            "min": 16,
                            "max": 36,
                            "value": 24,
                        },
                        {
                            "id": "cp_green",
                            "component": "AidaColorPicker",
                            "label": "THEME COLOR",
                            "cssVar": "--pc98-green",
                            "value": "#55ff55",
                        },
                        {
                            "id": "cp_bg",
                            "component": "AidaColorPicker",
                            "label": "BACKGROUND COLOR",
                            "cssVar": "--pc98-bg",
                            "value": "#000022",
                        },
                        {
                            "id": "cp_border",
                            "component": "AidaColorPicker",
                            "label": "BORDER COLOR",
                            "cssVar": "--pc98-border",
                            "value": "#5555aa",
                        },
                        {
                            "id": "cp_panel",
                            "component": "AidaColorPicker",
                            "label": "PANEL COLOR",
                            "cssVar": "--pc98-dark-gray",
                            "value": "#222244",
                        },
                    ],
                },
            },
        ]
    }

# 3. Programmatically generate the complete, token-efficient system instruction relying entirely on the SDK
A2UI_SYSTEM_INSTRUCTION = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description=WORKFLOW_DESCRIPTION,
    ui_description=UI_DESCRIPTION,
    client_ui_capabilities={"supportedCatalogIds": ["aida_custom"]},
    include_schema=True,
    include_examples=True,
    validate_examples=False,
)

# Apply ADK template processor curly brace bug workaround
A2UI_SYSTEM_INSTRUCTION = A2UI_SYSTEM_INSTRUCTION.replace(
    "{expression}", "{expression-format}"
)
A2UI_SYSTEM_INSTRUCTION = A2UI_SYSTEM_INSTRUCTION.replace("a2ui-json", "a2ui")

skill_toolset = DynamicSkillToolset(skills_dir=SKILLS_DIR)

root_agent = Agent(
    model=MODEL,
    name="aida",
    description="The emergency diagnostic agent",
    instruction=A2UI_SYSTEM_INSTRUCTION,
    tools=[
        skill_toolset,
        run_osquery,
        show_ui_controls,
    ],
    generate_content_config=GENERATE_CONTENT_CONFIG,
)