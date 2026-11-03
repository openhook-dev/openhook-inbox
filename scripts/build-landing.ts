// Version assets from leaf imports upward so returning browsers load one release.
// Render the React homepage at build time; Python serves its HTML without Node.
import { rm } from "node:fs/promises";
process.env.NODE_ENV = "production";
const server = await Bun.build({
  entrypoints: ["frontend/render.tsx"], outdir: ".frontend-build", naming: "render.mjs",
  target: "node", packages: "external", minify: true,
  define: { "process.env.NODE_ENV": '\"production\"' }, jsx: { development: false },
});
if (!server.success) throw new AggregateError(server.logs, "Frontend HTML build failed");
try {
  const render = Bun.spawn(["node", ".frontend-build/render.mjs"], { env: { ...process.env, NODE_ENV: "production" }, stdout: "inherit", stderr: "inherit" });
  if (await render.exited !== 0) throw new Error("Frontend HTML render failed");
} finally { await rm(".frontend-build", { recursive: true, force: true }); }
const bundle = await Bun.build({
  entrypoints: ["frontend/client.tsx"], outdir: "web/assets", naming: "home.js",
  target: "browser", minify: true, jsx: { development: false }, define: { "process.env.NODE_ENV": '\"production\"' },
});
if (!bundle.success) throw new AggregateError(bundle.logs, "Frontend bundle failed");
const css = Bun.spawn(["node", "node_modules/.bin/tailwindcss", "-i", "frontend/styles.css", "-o", "web/assets/home.css", "--minify"], { stdout: "inherit", stderr: "inherit" });
if (await css.exited !== 0) throw new Error("Tailwind build failed");


// Preserve notices for dependencies included in the browser bundle.
const notices = [];
for (const name of ["react", "react-dom", "scheduler", "motion", "framer-motion", "motion-dom", "motion-utils", "class-variance-authority", "clsx", "tailwind-merge", "@radix-ui/react-slot", "@radix-ui/react-compose-refs", "tailwindcss"]) {
  let license;
  for (const file of ["LICENSE", "LICENSE.md", "LICENSE.txt", "license"]) {
    const candidate = Bun.file(`node_modules/${name}/${file}`);
    if (await candidate.exists()) { license = await candidate.text(); break; }
  }
  if (!license) throw new Error(`Missing license for ${name}`);
  notices.push(`${name}\n${license}`);
}
await Bun.write("web/assets/licenses/frontend-dependencies.txt", notices.join("\n\n"));

async function version(path: string) {
  return new Bun.CryptoHasher("sha256")
    .update(await Bun.file(path).arrayBuffer()).digest("hex").slice(0, 12);
}
async function update(file: string, replacements: Array<[RegExp, string]>) {
  let source = await Bun.file(file).text();
  for (const [pattern, value] of replacements) source = source.replace(pattern, value);
  await Bun.write(file, source);
}
await update("web/assets/style.css", [
  [/\/assets\/fonts\/paper-mono\.woff2(?:\?v=[^'"]+)?/,
    "/assets/fonts/paper-mono.woff2?v=" + await version("web/assets/fonts/paper-mono.woff2")],
]);
for (const file of ["web/assets/sessions.js", "web/assets/app.js"]) await update(file, [
  [/\.\/webmcp\.js(?:\?v=[^'"]+)?/, "./webmcp.js?v=" + await version("web/assets/webmcp.js")],
]);
await update("web/assets/app.js", [
  [/\.\/sessions\.js(?:\?v=[^'"]+)?/, "./sessions.js?v=" + await version("web/assets/sessions.js")],
]);
const replacements: Array<[RegExp, string]> = [];
for (const asset of ["app.js", "style.css", "fonts/paper-mono.woff2", "favicon.svg"]) {
  const escaped = asset.replaceAll(".", "\\.");
  replacements.push([
    new RegExp("/assets/" + escaped + "(?:\\?v=[^\\\"]+)?", "g"),
    "/assets/" + asset + "?v=" + await version("web/assets/" + asset),
  ]);
}
await update("web/index.html", replacements);

await Bun.write("web/pages/home-assets.html",
  `<link rel="stylesheet" href="/assets/home.css?v=${await version("web/assets/home.css")}">\n` +
  `<script type="module" src="/assets/home.js?v=${await version("web/assets/home.js")}"></script>\n`);
