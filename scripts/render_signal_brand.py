"""Render Openhook's text-only social card using the bundled Paper Mono font."""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

assets = Path(__file__).resolve().parent.parent / "web/assets"
font = instantiateVariableFont(TTFont(assets / "fonts/paper-mono.woff2"), {"wght": 400})
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
units = font["head"].unitsPerEm


def text(value, center, baseline, size, color="#181818"):
    advance, paths = 0, []
    for character in value:
        name = cmap.get(ord(character), ".notdef")
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
        advance += font["hmtx"][name][0]
    scale = size / units
    x = center - advance * scale / 2
    return f'<g fill="{color}" transform="translate({x} {baseline}) scale({scale} {-scale})">' + "".join(paths) + "</g>"


card = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630"><title>Openhook — an inbox for your agent</title><rect width="1200" height="630" fill="#faf9f6"/>'
card += text("openhook", 600, 128, 26)
card += text("An inbox for your agent.", 600, 290, 42)
card += text("Catch a webhook. Keep your agent moving.", 600, 352, 22, "#515151")
card += text("openhook.dev", 600, 516, 20, "#686868") + "</svg>"
assets.joinpath("social.svg").write_text(card)
