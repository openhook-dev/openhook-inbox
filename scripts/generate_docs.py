"""Write the tool reference from the running server's schemas."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server import mcp


async def main():
    tools = await mcp.list_tools()
    lines = ["# Openhook tool reference", "", f"{len(tools)} native tools. Generated with `uv run python scripts/generate_docs.py`.",
             "", "Keep private management tokens and provider credentials out of shared documents.", ""]
    for tool in sorted(tools, key=lambda item: item.name):
        lines.extend([f"## {tool.name}", "", tool.description or "", "", "```json",
                      json.dumps(tool.input_schema, indent=2), "```", ""])
    output = "\n".join(lines)
    path = Path(__file__).resolve().parent.parent / "docs/TOOLS.md"
    if "--check" in sys.argv:
        if not path.exists() or path.read_text() != output:
            raise SystemExit("Tool docs are stale: run scripts/generate_docs.py")
    else:
        path.write_text(output)


asyncio.run(main())
