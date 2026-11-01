# Openhook homepage

React + Tailwind + Motion. This is a component implementation, not a landing-page template.

- `Home.tsx` owns the use cases, rotating headline and copyable agent skill.
- The split composition follows the user-supplied Superlogical reference, with
  Openhook branding and original copy.
- `components/GlyphField.tsx` renders an original 3D signal loop as monochrome
  glyphs on canvas. It pauses for reduced motion, hidden tabs and user controls;
  its resize observer and animation frame are cleaned up on unmount.
- `components/react-bits/rotating-text.tsx` is the source from the React Bits
  shadcn registry: https://reactbits.dev/r/RotatingText-TS-TW.json.
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
Registry animation mounts after hydration, preserving the existing CSP without
allowing inline styles or scripts. Motion stops rotating for reduced-motion
preferences, hidden tabs, or the Pause control.
