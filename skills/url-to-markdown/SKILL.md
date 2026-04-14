---
name: url-to-markdown
version: "1.0.0"
description: "Convert any web page URL to clean Markdown text using the claw.ai.vn Markdown API. Use when the user wants to read, summarize, extract, or process content from a known URL as Markdown. Supports three modes: auto (smart routing), fast (speed-first), and slow (browser rendering for JS-heavy pages)."
read_when:
  - User gives a specific URL and wants page content as Markdown.
  - User wants to summarize or extract content from an article, docs page, or blog post.
  - User needs browser-rendered Markdown for a JS-heavy page without using Firecrawl.
  - User wants a fast markdown conversion pipeline backed by claw.ai.vn API.
metadata:
  openclaw:
    homepage: https://claw.ai.vn/
    emoji: "📝"
    requires:
      bins: [bun]
      env: [CLAW_API_KEY]
    primaryEnv: CLAW_API_KEY
    install:
      - id: bun-brew
        kind: brew
        formula: oven-sh/bun/bun
        bins: [bun]
        label: Install bun (brew)
---

# URL to Markdown

Convert web pages to clean, structured Markdown via the claw.ai.vn API.

## Commands

### Basic conversion

```bash
bun {baseDir}/scripts/url-to-markdown.js https://docs.svelte.dev/svelte/overview
```

### JSON output

```bash
bun {baseDir}/scripts/url-to-markdown.js https://example.com/article --json
```

### JS-heavy page

```bash
bun {baseDir}/scripts/url-to-markdown.js https://app.example.com/dashboard --method slow
```

### Keep images

```bash
bun {baseDir}/scripts/url-to-markdown.js https://blog.example.com/post --retain-images
```

## Environment

- `CLAW_API_KEY`: required API key. Get one from `https://claw.ai.vn/markdown-for-agents`
- `CLAW_API_URL`: optional base URL, default `https://claw.ai.vn`

## Response

Default output prints a metadata header followed by Markdown body:

```text
Title: Page Title
Source: https://example.com/page
Tokens: ~2450
Duration: 1230ms
Cache: HIT

---

# Page content as Markdown...
```

Use `--json` when downstream parsing matters.

## Notes

- This skill uses the API directly through the local Bun script.
- Modes:
  - `auto`: best default
  - `fast`: speed-first for docs and text-heavy pages
  - `slow`: browser-rendering for JS-heavy pages
- The API blocks Facebook, X/Twitter, and Threads URLs.
