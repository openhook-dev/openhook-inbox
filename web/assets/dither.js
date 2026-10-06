import { createDitherRenderer } from "./dither-gl.js?v=29381ef9a50f";
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];

// Shade a moving folded ring, then quantize it on a fixed Bayer pixel grid.
export function animateDither(canvas) {
  let renderer;
  try {
    renderer = createDitherRenderer(canvas);
  } catch {
    const replacement = canvas.cloneNode();
    canvas.replaceWith(replacement);
    canvas = replacement;
  }
  const context = renderer ? null : canvas.getContext("2d");
  if (!renderer && !context) return { pause() {} };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  let visible = false,
    paused = false,
    frame,
    last = 0,
    time = 0;
  let ink = getComputedStyle(canvas).color;
  const size = 96;
  if (!renderer) {
    canvas.width = size;
    canvas.height = size;
  }

  function draw() {
    if (renderer) {
      renderer.draw(time, ink);
      return;
    }
    context.clearRect(0, 0, size, size);
    context.fillStyle = ink;
    const angle = time * 0.13;
    const cos = Math.cos(angle),
      sin = Math.sin(angle);
    for (let y = 0; y < size; y++)
      for (let x = 0; x < size; x++) {
        const u = (x - size / 2) / (size * 0.46),
          v = (y - size / 2) / (size * 0.46);
        const rx = u * cos - v * sin,
          ry = u * sin + v * cos;
        const a = Math.atan2(ry, rx),
          radius = Math.hypot(rx, ry * 1.14);
        const fold = 0.075 * Math.sin(a * 3 + time * 0.42);
        const rim = 0.68 + fold;
        const width = 0.19 + 0.065 * Math.sin(a * 2 - time * 0.28);
        const distance = Math.abs(radius - rim) / width;
        if (distance > 1.1) continue;
        const surface = Math.sqrt(Math.max(0, 1 - distance * distance));
        const light = 0.22 + 0.5 * surface + 0.24 * Math.sin(a + time * 0.18);
        const threshold = (BAYER[(y % 4) * 4 + (x % 4)] + 0.5) / 16;
        const fade = Math.max(0, Math.min(1, (1.1 - distance) * 4));
        if (light * fade > threshold) context.fillRect(x, y, 1, 1);
      }
  }
  function tick(now) {
    if (now - last > 40) {
      time += Math.min((now - last) / 1000, 0.12);
      last = now;
      draw();
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame);
    if (visible && !paused && !document.hidden && !reduced.matches) {
      last = performance.now();
      frame = requestAnimationFrame(tick);
    } else draw();
  }
  new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    sync();
  }).observe(canvas);
  new MutationObserver(() => {
    ink = getComputedStyle(canvas).color;
    draw();
  }).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
  document.addEventListener("visibilitychange", sync);
  reduced.addEventListener("change", sync);
  draw();
  return {
    pause(value) {
      paused = value;
      sync();
    },
  };
}

export function wipeDither(canvas) {
  const context = canvas.getContext("2d");
  if (!context || matchMedia("(prefers-reduced-motion: reduce)").matches)
    return;
  const start = performance.now(),
    ink = getComputedStyle(canvas).color;
  canvas.width = 96;
  canvas.height = 64;
  function frame(now) {
    const progress = Math.min(1, (now - start) / 650);
    context.clearRect(0, 0, 96, 64);
    context.fillStyle = ink;
    for (let y = 0; y < 64; y++)
      for (let x = 0; x < 96; x++) {
        const position = x / 96;
        const density = Math.max(
          0,
          1 - Math.abs(position - progress * 1.8 + 0.4) * 4,
        );
        if (density > (BAYER[(y % 4) * 4 + (x % 4)] + 0.5) / 16)
          context.fillRect(x, y, 1, 1);
      }
    if (progress < 1) requestAnimationFrame(frame);
    else context.clearRect(0, 0, 96, 64);
  }
  requestAnimationFrame(frame);
}
