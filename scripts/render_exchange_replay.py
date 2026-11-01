"""Render captured events as a readable replay, not a raw terminal recording.

Requires Pillow and ffmpeg. No model calls or private CLI logs are used.
Run: python3 scripts/render_exchange_replay.py
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from examples.claude_codex_exchange import reject_capabilities


def render():
    receipt = json.loads((ROOT / 'web/assets/claude-codex-exchange-20261101.json').read_text())
    reject_capabilities(receipt)
    messages = receipt['messages']
    scenes = [
        ('Your agent. Their agent.', 'One private channel.',
         'Claude Code gets the business brief.\nCodex gets the technical brief.\n\n'
         'They ask and answer through Openhook.\nEach keeps its own context and key.',
         'INTERNAL TEST / SYNTHETIC PROJECT', 10),
        ('Claude Code asks', messages[0]['created_at'][11:19] + ' UTC / MCP send',
         messages[0]['text'], 'CAPTURED MESSAGE / NO SCRIPTED REPLY', 20),
        ('Codex answers', messages[1]['created_at'][11:19] + ' UTC / MCP send',
         messages[1]['text'], 'FETCHED BY CLAUDE CODE / MCP READ', 20),
        ('The answer comes back.', 'Claude → its human',
         '“' + receipt['processing_evidence']['claude']['final_response'].split('\n')[0] + '”\n\n'
         'Both screens work locally.\nStaging needs a database update.\nPayments can wait.\n'
         'Thursday is still a target.', 'EXCERPT + SUMMARY OF CLAUDE’S FINAL RESPONSE', 14),
        ('Try it with your partner.', 'openhook.dev',
         'MIT licensed. Self-hostable.\nMCP or HTTP. Separate member keys.\n\n'
         'Keep both agents listening.\nMessages are server-readable,\nnot end-to-end encrypted.',
         'GUIDE / PROMPTS / REPRODUCIBLE RUNNER', 10),
    ]
    font = str(ROOT / 'web/assets/fonts/paper-mono.woff2')
    body = ImageFont.truetype(font, 32)
    title = ImageFont.truetype(font, 50)
    small = ImageFont.truetype(font, 23)
    with tempfile.TemporaryDirectory(prefix='openhook-exchange-video-') as temporary:
        frames = Path(temporary)
        for index, (heading, label, text, footnote, _) in enumerate(scenes):
            frame = Image.new('RGB', (1080, 1350), 'white')
            draw = ImageDraw.Draw(frame)
            draw.text((70, 65), 'openhook', font=body, fill='black')
            draw.line((70, 130, 1010, 130), fill='black')
            draw.text((70, 185), heading, font=title, fill='black')
            draw.text((70, 275), label, font=small, fill='black')
            y = 365
            for paragraph in text.split('\n'):
                for line in textwrap.wrap(paragraph, width=44) or ['']:
                    draw.text((70, y), line, font=body, fill='black')
                    y += 47
            if y > 1060:
                raise ValueError('Message does not fit; split it into readable scenes')
            draw.line((70, 1110, 1010, 1110), fill='black')
            draw.text((70, 1145), footnote, font=small, fill='black')
            draw.text((70, 1200), 'Sanitized event replay / reading pauses added', font=small, fill='black')
            draw.text((70, 1240), 'Two local CLI processes / live Openhook MCP', font=small, fill='black')
            frame.save(frames / f'{index}.png')
            if index == 0:
                frame.save(ROOT / 'web/assets/claude-codex-exchange-poster.png')
        manifest = ''.join(f"file '{frames / str(index)}.png'\nduration {scene[-1]}\n"
                           for index, scene in enumerate(scenes))
        manifest += f"file '{frames / str(len(scenes) - 1)}.png'\n"
        (frames / 'frames.txt').write_text(manifest)
        duration = sum(scene[-1] for scene in scenes)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-f', 'concat', '-safe', '0', '-i', str(frames / 'frames.txt'),
                        '-vf', 'fps=24,format=yuv420p', '-t', str(duration),
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-movflags', '+faststart',
                        str(ROOT / 'web/assets/claude-codex-exchange-replay.mp4')], check=True)
        print(f'Rendered {duration}-second sanitized replay with Paper Mono.')


if __name__ == '__main__':
    render()
