"""Generate the tool reference and installable skill from their sources."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server import mcp
from openhook.discovery import tools_markdown
from openhook.pages import template


async def main():
    tools = await mcp.list_tools()
    root = Path(__file__).resolve().parent.parent
    outputs = {
        "docs/TOOLS.md": tools_markdown(tools),
        "skills/openhook/SKILL.md": template("skill.md", {"origin": "https://openhook.dev"}),
    }
    for filename, output in outputs.items():
        path = root / filename
        if "--check" in sys.argv:
            if not path.exists() or path.read_text() != output:
                raise SystemExit(f"{filename} is stale: run scripts/generate_docs.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output)


asyncio.run(main())
