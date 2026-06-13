import { createServer } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const host = process.env.FRONTEND_HOST || "127.0.0.1";
const port = Number(process.env.FRONTEND_PORT || 5173);
const backend = process.env.BACKEND_URL || "http://127.0.0.1:8000";

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
};

function serveFile(response, path) {
  response.writeHead(200, {
    "Content-Type": mime[extname(path)] || "application/octet-stream",
    "Cache-Control": "no-store",
  });
  createReadStream(path).pipe(response);
}

function proxyHeaders(upstream) {
  const headers = Object.fromEntries(upstream.headers.entries());
  delete headers["content-encoding"];
  delete headers["content-length"];
  delete headers["connection"];
  delete headers["transfer-encoding"];
  return headers;
}

async function proxy(request, response) {
  const target = new URL(request.url, backend);
  const headers = new Headers(request.headers);
  headers.delete("host");

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method || "GET") ? undefined : request,
      duplex: "half",
    });

    response.writeHead(upstream.status, proxyHeaders(upstream));
    if (upstream.body) {
      for await (const chunk of upstream.body) response.write(chunk);
    }
    response.end();
  } catch (error) {
    response.writeHead(502, { "Content-Type": "application/json; charset=utf-8" });
    response.end(JSON.stringify({ detail: `Backendga ulanishda xatolik: ${error.message}` }));
  }
}

createServer((request, response) => {
  if (request.url?.startsWith("/User/")) {
    proxy(request, response);
    return;
  }

  const url = new URL(request.url || "/", `http://127.0.0.1:${port}`);
  const safePath = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, "");
  const requested = join(root, safePath === "/" ? "index.html" : safePath);
  const path = existsSync(requested) && statSync(requested).isFile() ? requested : join(root, "index.html");
  serveFile(response, path);
}).listen(port, host, () => {
  console.log(`Frontend: http://${host}:${port}`);
  console.log(`Backend proxy: ${backend}`);
});
