#!/usr/bin/env bun

const DEFAULT_API_URL = process.env.CLAW_API_URL || "https://claw.ai.vn";

function printUsage() {
  console.error(
    "Usage: bun url-to-markdown.js <url> [--method auto|fast|slow] [--retain-images] [--disable-cache] [--json] [--api-url URL] [--api-key KEY]",
  );
}

function parseArgs(argv) {
  if (argv.length === 0) {
    printUsage();
    process.exit(1);
  }

  const opts = {
    url: "",
    method: "auto",
    retainImages: false,
    disableCache: false,
    json: false,
    apiUrl: DEFAULT_API_URL,
    apiKey: process.env.CLAW_API_KEY || "",
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!opts.url && !arg.startsWith("-")) {
      opts.url = arg;
      continue;
    }
    if (arg === "--method") {
      opts.method = argv[++i] || "auto";
      continue;
    }
    if (arg === "--retain-images") {
      opts.retainImages = true;
      continue;
    }
    if (arg === "--disable-cache") {
      opts.disableCache = true;
      continue;
    }
    if (arg === "--json") {
      opts.json = true;
      continue;
    }
    if (arg === "--api-url") {
      opts.apiUrl = argv[++i] || DEFAULT_API_URL;
      continue;
    }
    if (arg === "--api-key") {
      opts.apiKey = argv[++i] || "";
      continue;
    }
    console.error(`Unknown argument: ${arg}`);
    printUsage();
    process.exit(1);
  }

  if (!opts.url) {
    printUsage();
    process.exit(1);
  }
  if (!opts.apiKey) {
    console.error("CLAW_API_KEY is required. Set env var or pass --api-key.");
    process.exit(1);
  }

  return opts;
}

function renderText(result) {
  const meta = result.meta || {};
  const lines = [];
  lines.push(`Title: ${meta.title || ""}`);
  lines.push(`Source: ${meta.source || result.url}`);
  if (meta.tokens) {
    lines.push(`Tokens: ~${meta.tokens}`);
  }
  if (typeof meta.totalDurationMs === "number") {
    lines.push(`Duration: ${meta.totalDurationMs}ms`);
  }
  if (meta.cacheStatus) {
    lines.push(`Cache: ${meta.cacheStatus}`);
  }
  if (meta.upstreamMethod) {
    lines.push(`Route: ${meta.upstreamMethod}`);
  }
  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push(result.markdown || "");
  return lines.join("\n");
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const response = await fetch(`${opts.apiUrl.replace(/\/+$/, "")}/api/v1/markdown`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": opts.apiKey,
    },
    body: JSON.stringify({
      url: opts.url,
      method: opts.method,
      retain_images: opts.retainImages ? "true" : "false",
      disable_cache: opts.disableCache ? "true" : "false",
    }),
  });

  const bodyText = await response.text();
  let payload;
  try {
    payload = JSON.parse(bodyText);
  } catch {
    payload = bodyText;
  }

  if (!response.ok) {
    const message =
      payload && typeof payload === "object" && "message" in payload
        ? payload.message
        : String(payload);
    console.error(`API error ${response.status}: ${message}`);
    process.exit(1);
  }

  if (opts.json) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.log(renderText(payload));
}

await main();
