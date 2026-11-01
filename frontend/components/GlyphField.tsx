import { useEffect, useRef } from 'react';

type Point = { x: number; y: number; z: number; light: number };

// A continuous signal loop, sampled as a tube and rendered as a field of glyphs.
// The same points are reused every frame; no textures, downloads or WebGL needed.
function signalLoop(): Point[] {
  const points: Point[] = [];
  for (let i = 0; i < 420; i++) {
    const t = i / 420 * Math.PI * 2;
    const center = { x: 0.62 * Math.sin(2 * t), y: 1.25 * Math.cos(t), z: 0.46 * Math.sin(t) };
    const tangent = { x: 1.24 * Math.cos(2 * t), y: -1.25 * Math.sin(t), z: 0.46 * Math.cos(t) };
    const length = Math.hypot(tangent.x, tangent.y, tangent.z);
    const tx = tangent.x / length, ty = tangent.y / length, tz = tangent.z / length;
    const sideLength = Math.hypot(tx, ty);
    const nx = -ty / sideLength, ny = tx / sideLength;
    for (let j = 0; j < 38; j++) {
      const a = j / 38 * Math.PI * 2;
      const c = Math.cos(a), s = Math.sin(a), radius = 0.23;
      points.push({
        x: center.x + radius * (nx * c - tz * ny * s),
        y: center.y + radius * (ny * c + tz * nx * s),
        z: center.z + radius * sideLength * s,
        light: (c + s + 2) / 4,
      });
    }
  }
  return points;
}

export function GlyphField({ paused }: { paused: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const element = canvas.current;
    const context = element?.getContext('2d');
    if (!element || !context) return;
    const points = signalLoop();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let width = 0, height = 0, frame = 0, time = 0, last = 0;
    const glyphs = '·:+x*#';
    const draw = (now: number) => {
      frame = 0;
      if (now - last > 50 || last === 0 || paused || reduced.matches) {
        if (!paused && !reduced.matches && last) time += Math.min(now - last, 100) / 1000;
        last = now;
        context.clearRect(0, 0, width, height);
        const cell = width < 360 ? 4 : 4.8;
        const columns = Math.ceil(width / cell), rows = Math.ceil(height / cell);
        const depths = new Float32Array(columns * rows).fill(-Infinity);
        const lights = new Float32Array(columns * rows);
        const angle = Math.sin(time * 0.24) * 0.45 + 0.25;
        const scale = Math.min(width / 2.15, height / 3.55);
        const ca = Math.cos(angle), sa = Math.sin(angle);
        for (const point of points) {
          const x = point.x * ca + point.z * sa;
          const z = point.z * ca - point.x * sa;
          const breath = 1 + 0.025 * Math.sin(time * 0.8 + point.y * 2);
          const column = Math.round((width / 2 + x * scale * breath) / cell);
          const row = Math.round((height / 2 + point.y * scale) / cell);
          if (column < 0 || column >= columns || row < 0 || row >= rows) continue;
          const index = row * columns + column;
          if (z > depths[index]) { depths[index] = z; lights[index] = point.light; }
        }
        context.font = `${cell + 1}px monospace`;
        context.textAlign = 'center';
        for (let row = 0; row < rows; row++) {
          for (let column = 0; column < columns; column++) {
            const index = row * columns + column;
            if (depths[index] === -Infinity) continue;
            const light = lights[index];
            const grain = ((column * 13 + row * 7) % 17) / 17;
            const density = Math.max(0, Math.min(5, Math.floor((light * 0.65 + (depths[index] + 0.8) * 0.3 + grain * 0.12) * 5)));
            context.fillStyle = `rgba(0,0,0,${0.22 + density * 0.14})`;
            context.fillText(glyphs[density], column * cell, row * cell);
          }
        }
      }
      if (!paused && !reduced.matches && !document.hidden) frame = requestAnimationFrame(draw);
    };
    const restart = () => {
      cancelAnimationFrame(frame);
      last = 0;
      if (!document.hidden) frame = requestAnimationFrame(draw);
    };
    const observer = new ResizeObserver(entries => {
      const rect = entries[0].contentRect;
      width = rect.width; height = rect.height;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      element.width = Math.round(width * ratio); element.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      restart();
    });
    observer.observe(element);
    reduced.addEventListener('change', restart);
    document.addEventListener('visibilitychange', restart);
    return () => { cancelAnimationFrame(frame); observer.disconnect(); reduced.removeEventListener('change', restart); document.removeEventListener('visibilitychange', restart); };
  }, [paused]);
  return <canvas ref={canvas} className="block h-full w-full" aria-hidden="true" />;
}
