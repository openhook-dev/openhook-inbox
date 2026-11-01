import { useEffect, useRef } from 'react';
import { animate, motion, useMotionValue, useTransform, type MotionValue } from 'motion/react';

// Words on a slowly turning cylinder. The front word completes the headline;
// the rest recede above and below it. Pure transforms, mounted after hydration.
const step = 17; // degrees between neighbouring words
const radius = 4.2; // in em, so the drum scales with the headline

function Word({ text, index, count, position, belowOnly }: {
  text: string; index: number; count: number; position: MotionValue<number>; belowOnly: boolean;
}) {
  const offset = useTransform(position, value => ((index - value) % count + count * 1.5) % count - count / 2);
  const transform = useTransform(offset, distance => {
    const angle = distance * step * Math.PI / 180;
    return `translateY(${Math.sin(angle) * radius}em) translateZ(${(Math.cos(angle) - 1) * radius}em) rotateX(${-distance * step}deg)`;
  });
  const opacity = useTransform(offset, distance => {
    if (Math.abs(distance) * step >= 88 || (belowOnly && distance < -0.5)) return 0;
    const front = Math.max(0, 1 - Math.abs(distance) * 2);
    return (0.22 + 0.78 * front) * Math.cos(distance * step * Math.PI / 180);
  });
  return <motion.span className="col-start-1 row-start-1 whitespace-nowrap [backface-visibility:hidden]" style={{ transform, opacity }}>{text}</motion.span>;
}

export function WordDrum({ words, active, belowOnly }: { words: string[]; active: number; belowOnly: boolean }) {
  const position = useMotionValue(active);
  const turns = useRef(active);
  useEffect(() => {
    // Always turn forward, so the drum keeps rolling one way past the last word.
    turns.current += (active - turns.current % words.length + words.length) % words.length;
    const controls = animate(position, turns.current, { type: 'spring', stiffness: 70, damping: 16, mass: 1 });
    return () => controls.stop();
  }, [active]);
  return <span className="grid [perspective:28em] [perspective-origin:0%_50%] [transform-style:preserve-3d]" aria-hidden="true">
    {words.map((text, index) => <Word key={text} text={text} index={index} count={words.length} position={position} belowOnly={belowOnly}/>)}
  </span>;
}
