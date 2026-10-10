// Version assets from leaf imports upward so returning browsers load one release.
// The text interface needs no frontend framework or compilation.
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
await update("web/assets/app.js", [
  [/\.\/home\.js(?:\?v=[^'"]+)?/, "./home.js?v=" + await version("web/assets/home.js")],
]);
const replacements: Array<[RegExp, string]> = [];
for (const asset of ["app.js", "style.css", "theme.js", "fonts/paper-mono.woff2", "favicon.svg", "social.png"]) {
  const escaped = asset.replaceAll(".", "\\.");
  replacements.push([
    new RegExp("/assets/" + escaped + "(?:\\?v=[^\\\"]+)?", "g"),
    "/assets/" + asset + "?v=" + await version("web/assets/" + asset),
  ]);
}
await update("web/index.html", replacements);
