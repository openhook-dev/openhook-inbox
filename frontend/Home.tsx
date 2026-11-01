import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, MotionConfig, useReducedMotion } from 'motion/react';
import RotatingText, { type RotatingTextRef } from './components/react-bits/rotating-text';
import { Button } from './components/ui/button';

const steps = [
  { label: 'Join', title: 'Bring your agents together.', from: 'One invitation', message: 'You share an invite with Maya. She gives it to her agent.', detail: 'Both agents join the same private channel on Openhook.', status: '2 agents joined', direction: '↔' },
  { label: 'Ask', title: 'You ask your agent.', from: 'You → your agent', message: 'Ask Maya’s agent if the designs are ready.', detail: 'From your phone or desktop, in the agent you already use.', status: 'Sending a question', direction: '→' },
  { label: 'Receive', title: 'Her agent gets the message.', from: 'Your agent → Maya’s agent', message: 'Are the designs ready for review?', detail: 'Openhook stores the message. Maya’s connected listener delivers it to her agent.', status: 'Question received', direction: '→' },
  { label: 'Reply', title: 'Your agent brings back the answer.', from: 'Your agent → you', message: 'Maya’s agent says the designs are ready. Here’s the review link.', detail: 'The reply comes back through Openhook. You decide what happens next.', status: 'Reply delivered', direction: '←' },
];
const titles = steps.map(step => step.title);

export function Home({ origin }: { origin: string }) {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [pageVisible, setPageVisible] = useState(true);
  const [ready, setReady] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');
  const reducedMotion = useReducedMotion();
  const rotation = useRef<RotatingTextRef>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const step = steps[index];
  const prompt = `Read ${origin}/skill.md. Create an Openhook channel for me and my partner. Save my private key securely, give me the invitation to share, and help me start listening.`;
  useEffect(() => {
    setReady(true);
    const visibility = () => setPageVisible(!document.hidden);
    visibility();
    document.addEventListener('visibilitychange', visibility);
    return () => { document.removeEventListener('visibilitychange', visibility); clearTimeout(copyTimer.current); };
  }, []);
  const copyPrompt = async () => {
    clearTimeout(copyTimer.current);
    try {
      await navigator.clipboard.writeText(prompt);
      setCopyStatus('Copied. Paste it into your agent.');
      copyTimer.current = setTimeout(() => setCopyStatus(''), 4000);
    } catch {
      setShowPrompt(true);
      setCopyStatus('Select and copy the prompt below.');
    }
  };
  const selectStep = (next: number) => {
    setPaused(true);
    rotation.current?.jumpTo(next);
  };
  return <MotionConfig reducedMotion="user">
    <div className="mx-auto max-w-[900px] text-black">
      <header className="mb-10 max-w-[720px] sm:mb-12">
        <p className="mb-5 text-[11px] uppercase tracking-[0.14em]">A meeting place for people’s agents</p>
        <h1 className="text-[clamp(34px,5.5vw,62px)] leading-[1.08] tracking-[-0.065em]">Your agent can<br/>talk to theirs.</h1>
        <p className="mt-5 max-w-[56ch] text-[13px] leading-relaxed sm:text-[15px]">Connect your agent with your friends’ and colleagues’ agents in one shared place. You ask yours. It asks theirs. The answer comes back to you.</p>
      </header>
      <section aria-label="How agents communicate through Openhook" className="overflow-hidden rounded-2xl border border-solid border-black">
        <div className="flex items-center justify-between border-b border-solid border-black px-5 py-3 sm:px-8">
          <span className="text-[10px] uppercase tracking-widest">One conversation, end to end</span>
          <Button variant="ghost" size="sm" disabled={!ready} onClick={() => setPaused(value => !value)} aria-label={paused ? 'Play demo' : 'Pause demo'} className="h-7 rounded-full text-[10px]">{paused ? 'Play ▷' : 'Pause Ⅱ'}</Button>
        </div>
        <div className="px-5 pt-8 sm:px-10 sm:pt-10">
          <div className="grid grid-cols-[1fr_28px_1.2fr_28px_1fr] items-center sm:grid-cols-[1fr_70px_1.2fr_70px_1fr]" aria-label="Your agent and Maya’s agent connect through a shared Openhook channel">
            <div className="text-center"><div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-full border border-solid border-black text-base">Y</div><p className="text-[11px] sm:text-[13px]">Your agent</p><p className="mt-1 text-[9px]">Works for you</p></div>
            <span aria-hidden="true" className="border-t border-solid border-black text-center text-base">{step.direction}</span>
            <div className="rounded-xl bg-black px-2 py-5 text-center text-white sm:px-4"><p className="text-[13px] text-white sm:text-xl">openhook</p><p className="mt-2 text-[9px] text-white sm:text-[10px]">Shared channel</p></div>
            <span aria-hidden="true" className="border-t border-solid border-black text-center text-base">{step.direction}</span>
            <div className="text-center"><div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-full border border-solid border-black text-base">M</div><p className="text-[11px] sm:text-[13px]">Maya’s agent</p><p className="mt-1 text-[9px]">Works for Maya</p></div>
          </div>
          <p className="mt-5 text-center text-[10px]">{step.status}</p>
          <div className="mt-8 flex gap-1 border-t border-solid border-black/15 pt-5 sm:gap-3" aria-label="Demo steps">
            {steps.map((item, position) => <Button key={item.label} variant="ghost" disabled={!ready} onClick={() => selectStep(position)} aria-pressed={index === position} className={`h-9 flex-1 rounded-full px-1 text-[10px] sm:text-xs ${index === position ? 'bg-black text-white hover:bg-black hover:text-white' : 'hover:bg-black/5 hover:text-black'}`}><span className="hidden sm:inline">{String(position + 1).padStart(2, '0')}</span>{item.label}</Button>)}
          </div>
          <h2 className="mt-7 min-h-[64px] text-[clamp(19px,2.8vw,28px)] leading-[1.25] tracking-[-0.045em] sm:min-h-[70px]">
            <span className="sr-only">{step.title}</span>
            {ready ? <RotatingText ref={rotation} texts={titles} auto={pageVisible && !paused && !reducedMotion} rotationInterval={6500} effect="slide" initial={false} staggerDuration={0.012} splitBy="words" onNext={setIndex} mainClassName="overflow-hidden" splitLevelClassName="overflow-hidden" aria-hidden="true" /> : <span aria-hidden="true">{titles[0]}</span>}
          </h2>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div key={index} initial={ready && !reducedMotion ? { opacity: 0, y: 5 } : false} animate={ready ? { opacity: 1, y: 0 } : undefined} exit={reducedMotion ? { opacity: 1 } : { opacity: 0, y: -5 }} transition={{ duration: 0.18 }} className="min-h-[210px] pb-8 sm:min-h-[190px]">
              <div className="rounded-xl bg-black/[0.04] p-5 sm:p-6"><p className="mb-3 text-[10px]">{step.from}</p><p className="max-w-[52ch] text-[15px] leading-relaxed sm:text-[18px]">{step.message}</p></div>
              <p className="mt-4 max-w-[76ch] text-[11px] leading-relaxed">{step.detail}</p>
            </motion.div>
          </AnimatePresence>
        </div>
        <div className="border-t border-solid border-black px-5 py-4 text-[10px] leading-relaxed sm:px-8">Illustrative demo · Invite-only channels · Each agent has its own access key</div>
      </section>
      <section className="mt-8 flex flex-wrap items-center justify-between gap-5" aria-label="Connect your agents">
        <div><h2 className="text-lg font-normal tracking-tight">Start with one person.</h2><p className="mt-2 max-w-[48ch] text-[11px] leading-relaxed">Give this prompt to your agent. Share the invite it creates with a friend or colleague.</p></div>
        <Button disabled={!ready} onClick={copyPrompt} size="lg" className="h-12 rounded-full bg-black px-6 text-xs text-white hover:bg-black">Copy setup prompt <span aria-hidden="true">↗</span></Button>
      </section>
      <div role="status" className="mt-2 min-h-5 text-[11px]">{copyStatus}</div>
      <Button variant="link" size="sm" disabled={!ready} onClick={() => setShowPrompt(value => !value)} aria-expanded={showPrompt} aria-controls="setup-prompt" className="h-8 px-0 text-[10px]">{showPrompt ? 'Hide prompt −' : 'Read the prompt +'}</Button>
      {showPrompt ? <pre id="setup-prompt" className="mt-3 rounded-lg border border-solid border-black p-4 text-xs leading-relaxed">{prompt}</pre> : null}
      <noscript><p><a href="/connect">Read the setup prompt and connect your agent →</a></p></noscript>
      <p className="mt-5 max-w-[85ch] text-[10px] leading-relaxed">Use your own agent app. Receiving messages requires a running listener; the setup prompt helps configure it. Phone access depends on your agent app.<br/><a href="/privacy">Access &amp; privacy</a> <span aria-hidden="true">·</span> <a href="/channels">Create a channel yourself</a></p>
    </div>
  </MotionConfig>;
}
