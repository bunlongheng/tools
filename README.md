# tools

Personal automation tools by [@bunlongheng](https://github.com/bunlongheng).

Live site: https://bunlongheng.github.io/tools/

---

## Tools

### [MD — Markdown Editor](./index.html)
Minimal split-pane markdown editor with live preview and dark/light theme.
Inspired by StackEdit. No build step — pure HTML/JS.

### [Meeting Processor](./meeting-processor/)
Drop a video → get AI meeting notes automatically.
Pipeline: `video → ffmpeg → Whisper → Claude API → .md notes`

See [ARCHITECTURE.md](./meeting-processor/ARCHITECTURE.md) for full setup docs.
