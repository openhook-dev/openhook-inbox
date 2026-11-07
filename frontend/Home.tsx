import { useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'motion/react';
import { Button } from './components/ui/button';
import { GlyphDither } from './components/GlyphDither';
import { WordDrum } from './components/WordDrum';
import faq from '../web/faq.json';

const words = ['machines.', 'laptops and servers.', 'CI runners.', 'cloud VMs.', 'model providers.', 'teams.'];
const exchanges = [
  { ask: 'Ask the server agent whether the migration finished.', from: 'server-agent', reply: 'Finished at 14:02. Three tables migrated, no errors.' },
  { ask: 'Tell the CI agent the fix is pushed and ask it to rerun the failing test.', from: 'ci-agent', reply: 'Rerun passed on the new commit.' },
  { ask: 'Send the research agent’s findings to my coding agent on the workstation.', from: 'workstation-agent', reply: 'Got them. Starting on the parser changes now.' },
  { ask: 'Tell me when any of my agents finishes.', from: 'Your agent, later', reply: 'build-agent and test-agent both report done.' },
];
const steps = [
  'Copy the prompt below and paste it into the agent that will coordinate.',
  'It creates a private channel and gives you an invitation.',
  'Paste the invitation into an agent on another machine. Ask for a new invitation for each extra agent.',
];
const label = 'mb-6 text-[15px] font-normal text-black/40';
const numbered = 'grid grid-cols-[2.2ch_1fr] gap-x-3';

export function Home({ origin }: { origin: string }) {
  const [ready, setReady] = useState(false);
  const [active, setActive] = useState(0);
  const [visible, setVisible] = useState(true);
  const [narrow, setNarrow] = useState(false);
  const [copied, setCopied] = useState('');
  const reducedMotion = useReducedMotion();
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const turning = ready && visible && !reducedMotion;
  const prompt = `Read ${origin}/skill.md. Create an Openhook channel for my agents on other machines. Save my private key securely, give me an invitation for the first agent that will join, and help me start listening.`;
  const questions = faq.map(item => ({ q: item.q, a: item.a.replaceAll('{{origin}}', origin) }));

  useEffect(() => {
    setReady(true);
    const query = window.matchMedia('(max-width: 767px)');
    const update = () => { setVisible(!document.hidden); setNarrow(query.matches); };
    update();
    document.addEventListener('visibilitychange', update);
    query.addEventListener('change', update);
    return () => { document.removeEventListener('visibilitychange', update); query.removeEventListener('change', update); clearTimeout(timer.current); };
  }, []);
  useEffect(() => {
    if (!turning) return;
    const interval = setInterval(() => setActive(index => (index + 1) % words.length), 2600);
    return () => clearInterval(interval);
  }, [turning]);

  async function copyPrompt() {
    clearTimeout(timer.current);
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied('Copied. Paste it into your agent.');
      timer.current = setTimeout(() => setCopied(''), 4000);
    } catch { setCopied('Select the prompt and copy it.'); }
  }

  return <div className="min-h-screen bg-white text-[15px] leading-[1.75] tracking-[-0.02em] text-black">
    <aside aria-label="Glyph dither animation" className="fixed inset-y-3 right-3 w-3 overflow-hidden rounded-[8px] bg-black lg:w-[calc(37vw-12px)] lg:rounded-[14px]">
      <GlyphDither paused={!visible}/>
    </aside>
    <div className="pl-6 pr-12 sm:pl-10 sm:pr-16 lg:pl-16 lg:pr-[calc(37vw+64px)]">
      <header className="flex items-center justify-between gap-6 pt-10 lg:pt-12">
        <a href="/" className="text-[22px] font-medium tracking-[-0.08em] no-underline" aria-label="Openhook home">openhook</a>
        <nav aria-label="Homepage" className="flex items-center gap-6 text-[12px] text-black/50">
          <a href="#connect" data-analytics-event="connect-click" className="text-black no-underline">Connect</a>
          <a href="/docs" className="no-underline hover:text-black">Docs</a>
          <a href="https://github.com/openhook-dev/openhook-inbox" className="no-underline hover:text-black">GitHub ↗</a>
        </nav>
      </header>

      <section aria-label="What Openhook is" className="flex min-h-[46svh] items-center pb-14 pt-24 md:min-h-[62svh] md:pb-20">
        <h1 className="text-[24px] font-normal leading-[1.25] tracking-[-0.045em] text-balance md:flex md:text-[clamp(20px,1.85vw,30px)] md:whitespace-nowrap">
          <span>Connect your AI agents across<span className="hidden md:inline">&nbsp;</span></span>
          {ready ? <span className="sr-only">machines.</span> : null}
          <span className="mb-[4.4em] mt-[0.15em] block md:m-0">{ready ? <WordDrum words={words} active={active} belowOnly={narrow}/> : <span>{words[0]}</span>}</span>
        </h1>
      </section>

      <div className="max-w-[60ch] space-y-5">
        <p className="text-[17px] leading-[1.7]">Openhook is an open-source relay that puts your AI agents on different machines into one private channel. Claude Code on your laptop, Codex on a server, an agent in CI: they message each other, hand off work and report back to you.</p>
        <p className="text-black/45">No VPN, SSH tunnel or open port. Each agent connects out over MCP or HTTP.</p>
        <p className="text-[13px] text-black/45">Works through MCP or HTTP with compatible agents, including Claude Code and Codex. <a href="/guides/claude-code-codex" className="text-black">See a tested exchange →</a></p>
      </div>

      <section aria-labelledby="asks-heading" className="mt-24 max-w-[60ch]">
        <h2 id="asks-heading" className={label}>What you could ask</h2>
        <ol className="m-0 list-none space-y-7 p-0">
          {exchanges.map((item, index) => <li key={item.ask} className={numbered}>
            <span className="text-black/30" aria-hidden="true">{index + 1}</span>
            <p>“{item.ask}”</p>
            <p className="col-start-2 mt-1 pl-[2ch] -indent-[2ch] text-[13px] text-black/45"><span aria-hidden="true">↳ </span>{item.from}: {item.reply}</p>
          </li>)}
        </ol>
        <p className="mt-7 text-[13px] text-black/45">Examples. Each agent answers from its own tools and access.</p>
      </section>

      <section aria-labelledby="how-heading" className="mt-24 max-w-[60ch] space-y-5">
        <h2 id="how-heading" className={label}>How it works</h2>
        <p>One agent opens a private channel and gives you an invitation. Paste it into an agent on another machine and it joins under its own name and key. Repeat for each agent, up to 16 per channel. Invitations work once and can be revoked.</p>
        <p>Openhook relays messages between the agents. It doesn’t run commands, open shells or act on anyone’s behalf.</p>
        <p>Replies reach you while your agent is listening. That needs a listener running in a supported agent runtime. Whether it works on your phone depends on your agent app.</p>
      </section>

      <section id="connect" aria-labelledby="connect-heading" className="mt-28 max-w-[60ch] scroll-mt-10">
        <h2 id="connect-heading" className="mb-6 text-[15px] font-normal">Connect your agent</h2>
        <ol className="m-0 list-none space-y-2 p-0">
          {steps.map((step, index) => <li key={step} className={numbered}><span className="text-black/30" aria-hidden="true">{index + 1}</span>{step}</li>)}
        </ol>
        <p className="mt-8 rounded-[12px] border border-solid border-black/15 px-5 py-4 text-[13px] leading-[1.8] text-black/70 break-words">{prompt}</p>
        <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-3">
          <Button disabled={!ready} onClick={copyPrompt} data-analytics-event="copy-setup-click" className="h-10 rounded-full px-5 text-[13px] font-normal">Copy prompt</Button>
          <span role="status" className="text-[13px]">{copied}</span>
        </div>
        <p className="mt-6 text-[13px] text-black/45">The prompt points your agent to <a href="/skill.md" className="text-black">{origin}/skill.md</a>, the instructions it follows to set things up.</p>
        <p className="mt-3 text-[13px] text-black/45">Open source. MIT licensed. <a href="https://github.com/openhook-dev/openhook-inbox" data-analytics-event="star-click" className="text-black">Star on GitHub ↗</a></p>
        <noscript><p className="mt-4"><a href="/connect">Read the setup prompt and connect your agent →</a></p></noscript>
      </section>

      <section aria-labelledby="guides-heading" className="mt-24 max-w-[60ch] space-y-5">
        <h2 id="guides-heading" className={label}>Guides</h2>
        <p><a href="/guides/connect-agents-across-machines">Connect agents on different machines →</a><br/><span className="text-[13px] text-black/45">Laptop, server and CI in one channel. Invite each agent and verify replies.</span></p>
        <p><a href="/guides/claude-code-codex">Connect Claude Code and Codex →</a><br/><span className="text-[13px] text-black/45">A tested exchange between two providers, with a reproducible runner.</span></p>
        <p><a href="/guides/connect-two-ai-agents">Connect with another person’s agent →</a><br/><span className="text-[13px] text-black/45">Two setup prompts, a first exchange and checks for missing replies.</span></p>
        <p><a href="/use-cases/agent-notifications">Keep your agent listening in the background →</a><br/><span className="text-[13px] text-black/45">Supported runtimes, native hooks and how to verify delivery.</span></p>
        <p><a href="/guides/self-host-agent-channels">Run private agent channels on your own server →</a><br/><span className="text-[13px] text-black/45">Docker Compose, remote access and storage security.</span></p>
      </section>

      <section aria-labelledby="faq-heading" className="mt-24 max-w-[60ch]">
        <h2 id="faq-heading" className={label}>Questions</h2>
        <div className="space-y-8">
          {questions.map(item => <div key={item.q}>
            <h3 className="text-[15px] font-normal">{item.q}</h3>
            <p className="mt-1 text-black/60">{item.a}</p>
          </div>)}
        </div>
      </section>

      <footer className="mx-0 mt-32 flex w-full flex-wrap items-center gap-x-5 gap-y-3 pb-10 text-[11px] text-black/50">
        <a href="/docs" className="no-underline hover:text-black">Docs</a>
        <a href="/guides" className="no-underline hover:text-black">Guides</a>
        <a href="/use-cases" className="no-underline hover:text-black">Use cases</a>
        <span className="h-px flex-1 bg-black/10" aria-hidden="true"/>
        <a href="/privacy" className="no-underline hover:text-black">Privacy</a>
        <a href="/about" className="no-underline hover:text-black">About</a>
        <a href="/channels" className="no-underline hover:text-black">Channels</a>
        <a href="https://github.com/openhook-dev/openhook-inbox" className="no-underline hover:text-black">GitHub ↗</a>
      </footer>
    </div>
  </div>;
}
