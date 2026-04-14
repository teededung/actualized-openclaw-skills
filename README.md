# Actualized OpenClaw Skills

## Quick Install Prompt

Copy this prompt, replace `{{skill_name}}`, then paste it into an OpenClaw agent:

```text
Please install the OpenClaw skill "{{skill_name}}" from my public skills repository:
https://github.com/teededung/actualized-openclaw-skills

Use the same skill name everywhere it is needed.
Requirements:
- Read the skill's `SKILL.md` and any bundled scripts before installing.
- Copy that skill folder into `~/.openclaw/skills/`
- Preserve executable permissions for scripts if needed.
- Do not run any setup command that needs secrets, API keys, tokens, or account access without asking me first.
- After installing, tell me:
  1. which files were installed
  2. which binaries are required
  3. which environment variables are required
  4. one example command to use the skill
```

Public mirror of selected OpenClaw skills I use in my personal daily workflows.

This collection will grow and be updated over time as the skills evolve in real use. These skills are not published on ClawHub, so review the source before installing or running any scripts.

## Skills

| Skill | Version | Description |
| --- | --- | --- |
| [apple-reminders](skills/apple-reminders/) | 1.1.0 | Use when creating or updating Apple Reminders on macOS that should sync to iPhone and keep audible notification alarms, especially when dates must be interpreted by country or locale. |
| [url-to-markdown](skills/url-to-markdown/) | 1.0.0 | Convert any web page URL to clean Markdown text using the claw.ai.vn Markdown API. Use when the user wants to read, summarize, extract, or process content from a known URL as Markdown. Supports three modes: auto (smart routing), fast (speed-first), and slow (browser rendering for JS-heavy pages). |

## Install Manually

Copy a skill folder into one of the OpenClaw skill locations:

| Scope | Path |
| --- | --- |
| Global | `~/.openclaw/skills/<skill-name>/` |
| Workspace | `<project>/skills/<skill-name>/` |

Workspace skills take priority over local/global skills.

## API Keys

Some skills require external credentials.

- For `url-to-markdown`, get `CLAW_API_KEY` from:
  [https://claw.ai.vn/markdown-for-agents](https://claw.ai.vn/markdown-for-agents)

## Security

This repo borrows the useful install/discovery pattern from Awesome OpenClaw Skills, but it is intentionally smaller and curated. See [SECURITY.md](SECURITY.md) before installing.

## Source

Repository URL:

```text
https://github.com/teededung/actualized-openclaw-skills
```

## Tieng Viet

Day la bo skill OpenClaw minh dang dung hang ngay trong workflow ca nhan.

- Cac skill se duoc cap nhat dan theo thoi gian.
- Neu skill can API key, doc phan huong dan ben tren.
- Rieng `url-to-markdown`, lay `CLAW_API_KEY` tai:
  [https://claw.ai.vn/markdown-for-agents](https://claw.ai.vn/markdown-for-agents)
