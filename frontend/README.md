# Openhook homepage

React + Tailwind + Motion. This is a component implementation, not a landing-page template.

- `Home.tsx` owns the homepage: the use-case drum headline, example asks with
  the replies that come back, and "Connect your agent" with the copyable prompt.
  The prompt and the skill.md link use the server's `OPENHOOK_ORIGIN`; hosted
  deployments set it to https://openhook.dev. For a local preview on another
  port, set it to that port so the prompt points at the server you are viewing.
- The split composition follows the user-supplied Superlogical reference
  (text column left, a tall stationary panel right, a thin strip on phones),
  with Openhook branding and original copy.
- `components/WordDrum.tsx` turns the headline's last words on a 3D cylinder
  with Motion. It mounts after hydration; server HTML shows the first phrase.
- `components/GlyphDither.tsx` draws two lights, one per agent, joined by a
  channel; a pulse carries a question across and an answer back. The light is
  ordered-dithered into Paper Mono glyphs on canvas, batched by glyph level.
- `components/ui/button.tsx` comes from the shadcn new-york-v4 registry.
  Its imports use the local `cn` helper and the standalone Radix Slot package.
- `components.json` registers React Bits for future shadcn CLI additions.
- Full licenses ship in `web/assets/licenses/`; see `THIRD_PARTY_NOTICES.md`.

Run `bun install --frozen-lockfile`, `bun run typecheck`, and `bun run build`.
Node.js is needed at build time for React's server renderer and Tailwind CLI.
The Python runtime needs neither Node nor Bun: it serves the committed bundle
and pre-rendered HTML. CI rebuilds them and rejects stale generated assets.
Edit `frontend/Home.tsx`, not the generated `web/pages/home.html`.

Only `/` loads the React bundle and Tailwind stylesheet. Private channel screens
retain their independent runtime and privacy boundary. The demo has no API
calls. Initial HTML contains readable content and a no-JavaScript setup link.
Animation mounts after hydration, preserving the existing CSP without
allowing inline styles or scripts. Both the drum and the dither stop for reduced-motion
preferences, hidden tabs, or the Pause motion control.
