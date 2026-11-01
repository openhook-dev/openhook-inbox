import { useEffect, useRef } from 'react';

// Two soft lights, one per agent, joined by a faint channel. Every few seconds a
// pulse carries a question across and an answer back. The light field is
// ordered-dithered into Paper Mono glyphs, brighter glyphs drawn more opaque.
const glyphs = ' .·:-=+x*#%@';
const bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(value => value / 16 - 0.5);
const cycle = 9; // seconds for one question and its answer

function light(x: number, y: number, time: number, aspect: number) {
  const a = { x: 0.3 + 0.03 * Math.sin(time * 0.23), y: 0.28 + 0.02 * Math.cos(time * 0.19) };
  const b = { x: 0.7 + 0.03 * Math.cos(time * 0.21), y: 0.72 + 0.02 * Math.sin(time * 0.17) };
  const dx = b.x - a.x, dy = (b.y - a.y) / aspect;
  const px = x - a.x, py = (y - a.y) / aspect;
  const along = Math.max(0, Math.min(1, (px * dx + py * dy) / (dx * dx + dy * dy)));
  const across = Math.hypot(px - along * dx, py - along * dy);
  const phase = (time % cycle) / cycle;
  // Out from a for 40% of the cycle, rest at b, back from b, rest at a.
  const travel = phase < 0.4 ? phase / 0.4 : phase < 0.5 ? 1 : phase < 0.9 ? 1 - (phase - 0.5) / 0.4 : 0;
  const ease = travel * travel * (3 - 2 * travel);
  const moving = phase < 0.4 || (phase >= 0.5 && phase < 0.9) ? 1 : 0;
  const glow = (p: { x: number; y: number }, size: number) => Math.exp(-((x - p.x) ** 2 + ((y - p.y) / aspect) ** 2) / size);
  // A ring spreads from whichever light just received the pulse.
  const ripple = (p: { x: number; y: number }, at: number) => {
    const age = phase - at;
    if (age < 0 || age > 0.12) return 0;
    const r = Math.hypot(x - p.x, (y - p.y) / aspect);
    return (1 - age / 0.12) * Math.exp(-(((r - 0.04 - age * 2.2) / 0.025) ** 2));
  };
  const field = 0.2 + 0.1 * Math.sin(x * 4.1 + y * 2.3 + time * 0.25) + 0.06 * Math.sin(y * 7.7 - x * 1.9 - time * 0.18);
  return field * (0.55 + 0.45 * Math.sin(Math.PI * y))
    + 0.55 * (glow(a, 0.004) + glow(b, 0.004)) + 0.45 * (glow(a, 0.03) + glow(b, 0.03)) + 0.2 * (glow(a, 0.12) + glow(b, 0.12))
    + 0.3 * Math.exp(-((across / 0.022) ** 2))
    + 0.9 * moving * Math.exp(-(((along - ease) / 0.09) ** 2) - (across / 0.05) ** 2)
    + 0.55 * (ripple(b, 0.4) + ripple(a, 0.9));
}

export function GlyphDither({ paused }: { paused: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const clock = useRef(cycle * 0.15);
  useEffect(() => {
    const element = canvas.current;
    const context = element?.getContext('2d');
    if (!element || !context) return;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const still = () => paused || reduced.matches || document.hidden;
    let width = 0, height = 0, frame = 0, last = 0;
    const draw = (now: number) => {
      if (last && !still()) clock.current += Math.min(now - last, 100) / 1000;
      last = now;
      const cell = width < 120 ? 6 : 8;
      const columns = Math.ceil(width / cell), rows = Math.ceil(height / cell);
      const aspect = width / Math.max(height, 1);
      const levels: number[][] = glyphs.split('').map(() => []);
      for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
          const value = light(column / columns, row / rows, clock.current, aspect) + bayer[(row % 4) * 4 + column % 4] * 0.16;
          const level = Math.max(0, Math.min(glyphs.length - 1, Math.round(value * (glyphs.length - 1))));
          if (level) levels[level].push(column, row);
        }
      }
      context.fillStyle = '#000';
      context.fillRect(0, 0, width, height);
      context.font = `${cell + 1}px "Paper Mono", monospace`;
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      levels.forEach((cells, level) => {
        context.fillStyle = `rgba(255,255,255,${0.35 + 0.65 * level / (glyphs.length - 1)})`;
        for (let i = 0; i < cells.length; i += 2) context.fillText(glyphs[level], (cells[i] + 0.5) * cell, (cells[i + 1] + 0.5) * cell);
      });
    };
    const loop = (now: number) => {
      if (now - last >= 50) draw(now);
      frame = still() ? 0 : requestAnimationFrame(loop);
    };
    const restart = () => {
      cancelAnimationFrame(frame);
      last = 0;
      frame = requestAnimationFrame(now => { draw(now); if (!still()) frame = requestAnimationFrame(loop); });
    };
    const observer = new ResizeObserver(([entry]) => {
      width = entry.contentRect.width; height = entry.contentRect.height;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      element.width = Math.round(width * ratio); element.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      restart();
    });
    observer.observe(element);
    document.fonts.load('10px "Paper Mono"').then(restart, () => {});
    reduced.addEventListener('change', restart);
    document.addEventListener('visibilitychange', restart);
    return () => {
      cancelAnimationFrame(frame); observer.disconnect();
      reduced.removeEventListener('change', restart); document.removeEventListener('visibilitychange', restart);
    };
  }, [paused]);
  return <canvas ref={canvas} className="block h-full w-full" aria-hidden="true" />;
}
