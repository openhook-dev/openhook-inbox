const result = await Bun.build({
  entrypoints: ["frontend/event-relay.jsx"],
  outdir: "web/assets/iso",
  naming: "figure.[ext]",
  target: "browser",
  format: "esm",
  minify: true,
  define: { "process.env.NODE_ENV": JSON.stringify("production") },
});
if (!result.success) throw new Error(result.logs.join("\n"));
const notices = [
  "react-isokit/LICENSE",
  "react-isokit/NOTICE.md",
  "react/LICENSE",
  "react-dom/LICENSE",
];
await Bun.write(
  "web/assets/iso/THIRD_PARTY_NOTICES.txt",
  (
    await Promise.all(
      notices.map(
        async (name) =>
          `${name}\n\n${await Bun.file(`node_modules/${name}`).text()}`,
      ),
    )
  ).join("\n\n"),
);

// Version local imports from the leaf assets upward so returning browsers
// receive a consistent release, even when their old assets are cached.
async function version(path: string) {
  return new Bun.CryptoHasher("sha256")
    .update(await Bun.file(path).arrayBuffer())
    .digest("hex")
    .slice(0, 12);
}
async function update(file: string, replacements: Array<[RegExp, string]>) {
  let source = await Bun.file(file).text();
  for (const [pattern, value] of replacements)
    source = source.replace(pattern, value);
  await Bun.write(file, source);
}
await update("web/assets/dither.js", [
  [
    /\.\/dither-gl\.js(?:\?v=[^'"]+)?/,
    `./dither-gl.js?v=${await version("web/assets/dither-gl.js")}`,
  ],
]);
await update("web/assets/home.js", [
  [
    /\.\/dither\.js(?:\?v=[^'"]+)?/,
    `./dither.js?v=${await version("web/assets/dither.js")}`,
  ],
  [
    /\/assets\/iso\/figure\.js(?:\?v=[^'"]+)?/,
    `/assets/iso/figure.js?v=${await version("web/assets/iso/figure.js")}`,
  ],
]);
await update("web/assets/app.js", [
  [
    /\.\/home\.js(?:\?v=[^'"]+)?/,
    `./home.js?v=${await version("web/assets/home.js")}`,
  ],
]);
const indexReplacements: Array<[RegExp, string]> = [];
for (const asset of [
  "app.js",
  "brand.css",
  "iso/figure.css",
  "relay.css",
  "motion.css",
  "logo.svg",
  "favicon.svg",
  "social.png",
]) {
  const escaped = asset.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  indexReplacements.push([
    new RegExp(`/assets/${escaped}(?:\\?v=[^\"]+)?`),
    `/assets/${asset}?v=${await version(`web/assets/${asset}`)}`,
  ]);
}
await update("web/index.html", indexReplacements);
