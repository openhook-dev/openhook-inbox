"""Outline original Openhook wordmarks using a locally installed font."""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

font = TTFont("/System/Library/Fonts/Supplemental/Arial.ttf")
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
units = font["head"].unitsPerEm
mark = '<path d="M23 5.5A12 12 0 1 0 28 16H19" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'


def text(value, x, y, size, color="currentColor"):
    advance = 0
    paths = []
    for character in value:
        name = cmap.get(ord(character), ".notdef")
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
        advance += font["hmtx"][name][0]
    scale = size / units
    return f'<g fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">' + "".join(paths) + "</g>"


assets = Path(__file__).resolve().parent.parent / "web/assets"
wordmark = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 222 44" role="img" aria-labelledby="title"><title id="title">Openhook</title><g transform="translate(3 6)">' + mark + "</g>" + text("openhook", 48, 32, 32) + "</svg>"
assets.joinpath("wordmark.svg").write_text(wordmark)
social = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" color="#ededed" role="img" aria-labelledby="title"><title id="title">Openhook - an inbox for your agent</title><rect width="1200" height="630" fill="#0d0d0d"/><rect x="32" y="32" width="1136" height="566" fill="none" stroke="#262626"/><g transform="translate(70 72) scale(1.4)">' + mark + "</g>"
social += text("openhook", 132, 111, 46)
social += text("The world sends events.", 72, 275, 54)
social += text("Your agent gets them.", 72, 346, 54)
social += text("HTTP  /  email  /  DNS", 74, 409, 23, "#9b9b9b")
social += '<g transform="translate(888 234) scale(6.5)" opacity="0.3">' + mark + '</g><path d="M72 508H1128" stroke="#262626"/><circle cx="82" cy="551" r="5" fill="#acd9c5"/>'
social += text("openhook.dev", 102, 559, 22) + "</svg>"
assets.joinpath("social.svg").write_text(social)
