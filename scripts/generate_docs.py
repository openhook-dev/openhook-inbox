"""Write the tool reference from the running server's schemas."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server import mcp
from openhook.discovery import tools_markdown


async def main():
    tools = await mcp.list_tools()
    output = tools_markdown(tools)
    path = Path(__file__).resolve().parent.parent / "docs/TOOLS.md"
    if "--check" in sys.argv:
        if not path.exists() or path.read_text() != output:
            raise SystemExit("Tool docs are stale: run scripts/generate_docs.py")
    else:
        path.write_text(output)


asyncio.run(main())
