# ✍️ MD — Markdown Editor

**Live:** [bunlongheng.github.io/tools/md](https://bunlongheng.github.io/tools/md/)
**Source:** [/md/index.html](../md/index.html)

---

## What it does

A minimal, distraction-free markdown editor that renders your text live as you type. Inspired by StackEdit. No install, no build step — just open the URL.

## Features

| Feature | Detail |
|---------|--------|
| Live preview | Preview updates on every keystroke |
| Dark / light theme | Toggle with ☀/🌙, preference saved to localStorage |
| Draggable split pane | Drag the centre bar to resize editor and preview |
| Load local file | Open any `.md` file from your computer |
| Load from URL | Paste any raw GitHub URL to load remote markdown |
| ARCHITECTURE.md shortcut | One-click load of the meeting processor docs |
| Scroll sync | Editor scroll position mirrors the preview |
| Tab support | Tab inserts 2 spaces instead of jumping focus |
| Syntax highlighting | Code blocks auto-highlighted via highlight.js |
| Word / char / line count | Live stats in the status bar |

## Tech

- **marked.js** — markdown → HTML rendering
- **highlight.js** — code block syntax highlighting
- **Google Fonts** — Inter (UI) + JetBrains Mono (editor)
- No framework, no build step

## Use it

1. Go to [bunlongheng.github.io/tools/md](https://bunlongheng.github.io/tools/md/)
2. Start typing in the left pane — preview appears on the right
3. Click **Load File** to open a local `.md` file
4. Click **🌙** to toggle dark/light mode

---

[← Back to all tools](../README.md)
