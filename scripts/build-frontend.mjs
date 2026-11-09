import { copyFileSync, mkdirSync, watch, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as sass from "sass";

const root = fileURLToPath(new URL("../", import.meta.url));
const staticRoot = join(root, "space_game/static");
const scssRoot = join(staticRoot, "scss");
const outputRoot = join(staticRoot, "build");

function copy(source, destination) {
  const target = join(outputRoot, destination);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(join(root, "node_modules", source), target);
}

function build() {
  mkdirSync(outputRoot, { recursive: true });
  for (const entry of ["project", "admin", "cms-editor"]) {
    const result = sass.compile(join(scssRoot, `${entry}.scss`), {
      loadPaths: [join(root, "node_modules")],
      style: "compressed",
      sourceMap: false,
      quietDeps: true,
      silenceDeprecations: ["import"],
    });
    writeFileSync(join(outputRoot, `${entry}.css`), result.css);
  }
  copy("bootstrap/dist/js/bootstrap.bundle.min.js", "bootstrap.bundle.min.js");
  copy("bootstrap/dist/js/bootstrap.bundle.min.js.map", "bootstrap.bundle.min.js.map");
  copy("bootstrap/LICENSE", "licenses/bootstrap.txt");
  copy("@fontsource/jetbrains-mono/LICENSE", "licenses/jetbrains-mono.txt");
  for (const weight of [400, 600]) {
    copy(
      `@fontsource/jetbrains-mono/files/jetbrains-mono-latin-${weight}-normal.woff2`,
      `fonts/jetbrains-mono-latin-${weight}-normal.woff2`,
    );
  }
  console.log("Built website, admin and CMS editor styles, Bootstrap JavaScript and local fonts.");
}

build();

if (process.argv.includes("--watch")) {
  let timer;
  watch(scssRoot, { recursive: true }, () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      try {
        build();
      } catch (error) {
        console.error(error.message);
      }
    }, 100);
  });
  console.log("Watching SCSS for changes…");
}
