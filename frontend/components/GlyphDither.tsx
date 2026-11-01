import { useEffect, useRef } from 'react';

// A slow light field, ordered-dithered into monospace glyphs on canvas:
// a bright horizon that drifts across the panel, with fine horizontal grain.
const glyphs = ' .·:-=+x*#%@';
const bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(value => value / 16 - 0.5);
const smooth = (edge0: number, edge1: number, x: number) => {
  const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
};

function light(x: number, y: number, time: number) {
  const horizon = 0.46 + 0.05 * Math.sin(x * 2.4 + time * 0.21) + 0.02 * Math.sin(x * 6.3 - time * 0.17);
  const band = Math.exp(-(((y - horizon) / 0.15) ** 2));
  const grain = 0.06 * Math.sin(y * 31 + 3 * Math.sin(x * 2.7 + time * 0.4));
  return 0.22 * smooth(0, horizon, y) + 0.8 * band + 0.3 * smooth(horizon, 1.1, y) + grain;
}

export function GlyphDither({ paused }: { paused: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const clock = useRef(40);
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
      context.fillStyle = '#000';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#fff';
      context.font = `${cell + 1}px "Paper Mono", monospace`;
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
          const value = light(column / columns, row / rows, clock.current) + bayer[(row % 4) * 4 + column % 4] * 0.18;
          const level = Math.max(0, Math.min(glyphs.length - 1, Math.round(value * (glyphs.length - 1))));
          if (level) context.fillText(glyphs[level], (column + 0.5) * cell, (row + 0.5) * cell);
        }
      }
    };
    const loop = (now: number) => {
      if (now - last >= 66) draw(now);
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
