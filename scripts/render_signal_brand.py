"""Package the approved organization logo, outlined type, and dither artwork."""

import base64
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

assets = Path(__file__).resolve().parent.parent / "web/assets"
font = TTFont(assets / "fonts/barlow-condensed-semibold.woff2")
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
units = font["head"].unitsPerEm
logo = base64.b64encode((assets / "organization-logo.png").read_bytes()).decode()
mark = f'<image width="32" height="32" href="data:image/png;base64,{logo}"/>'


def text(value, x, y, size, color="currentColor"):
    advance, paths = 0, []
    for character in value:
        name = cmap.get(ord(character), ".notdef")
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        if pen.getCommands():
            paths.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
        advance += font["hmtx"][name][0]
    scale = size / units
    return f'<g fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">' + "".join(paths) + "</g>"


for name, color in (("logo", "currentColor"), ("logo-dark", "#fff"), ("logo-light", "#111")):
    assets.joinpath(name + ".svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" color="{color}" role="img" aria-labelledby="title"><title id="title">Openhook</title>{mark}</svg>')
assets.joinpath("favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" color="#fff"><rect width="40" height="40" fill="#000"/><g transform="translate(4 4)">' + mark + '</g></svg>')
assets.joinpath("wordmark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 44" role="img" aria-labelledby="title"><title id="title">Openhook</title><g transform="translate(2 6)">' + mark + '</g>' + text("OPENHOOK", 46, 35, 40) + '</svg>')

# A lit, folded signal ring. Bayer ordering produces sharp pixels without filters.
bayer = ((0,8,2,10),(12,4,14,6),(3,11,1,9),(15,7,13,5))
paths = [[], [], []]
for y in range(0, 900, 6):
    for x in range(0, 1000, 6):
        u, v = (x - 580) / 440, (y - 440) / 330
        radius = math.hypot(u, v)
        angle = math.atan2(v, u)
        ridge = .73 + .12 * math.sin(angle * 3)
        intensity = math.exp(-((radius - ridge) / .16) ** 2) * (.35 + .55 * (math.sin(angle - .8) + 1) / 2)
        threshold = (bayer[(y // 6) % 4][(x // 6) % 4] + .5) / 16
        if intensity > threshold:
            paths[min(2, int(intensity * 3))].append(f'M{x} {y}h5v5h-5z')
field_paths = "".join(f'<path fill="{color}" d="' + "".join(commands) + '"/>' for color, commands in zip(("#242424", "#494949", "#777777"), paths))
assets.joinpath("signal-field.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 900" fill="none">' + field_paths + '</svg>')

social = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" color="#fff" role="img" aria-labelledby="title"><title id="title">Openhook — an inbox for your AI agent</title><rect width="1200" height="630" fill="#000"/><g transform="translate(500 -110)">' + field_paths + '</g><g transform="translate(68 64) scale(1.25)">' + mark + '</g>'
social += text("OPENHOOK", 124, 102, 43)
social += text("AN INBOX FOR", 68, 290, 89)
social += text("YOUR AI AGENT.", 68, 379, 89)
social += text("HTTP / EMAIL / DNS", 72, 447, 27, "#999")
social += '<path d="M68 511H1132" stroke="#303030"/><rect x="72" y="553" width="7" height="7" fill="#fff"/>'
social += text("OPENHOOK.DEV", 95, 567, 25) + '</svg>'
assets.joinpath("social.svg").write_text(social)
