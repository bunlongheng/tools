# 🎙️ Meeting Processor

**Live page:** [bunlongheng.github.io/tools/meeting-processor](https://bunlongheng.github.io/tools/meeting-processor/)
**Source:** [/meeting-processor/](../meeting-processor/)
**Type:** Local macOS automation (not a web app)

---

## What it does

A macOS background service that watches a folder for new video files. When a video is added, it automatically runs a 3-step pipeline and saves structured AI meeting notes as a markdown file.

```
Drop video → ffmpeg (audio) → Whisper (transcript) → Claude API (notes)
```

## Pipeline

| Step | Tool | Output | Cost |
|------|------|--------|------|
| 1 | ffmpeg | `.mp3` audio | Free |
| 2 | OpenAI Whisper | `.txt` transcript | Free — runs locally |
| 3 | Claude API | `-notes.md` meeting notes | ~$0.02 per meeting |

## Notes output

Each meeting note contains 6 sections:

1. **Meeting Summary** — 2–3 sentence overview
2. **Action Items** — checkbox list with owners and deadlines
3. **Key Decisions** — concrete decisions made
4. **Open Questions** — unresolved items
5. **Next Steps** — follow-ups and next meetings
6. **Notable Insights** — risks, ideas, blockers

## Requirements

- macOS
- [Homebrew](https://brew.sh): `brew install ffmpeg fswatch`
- Python 3.13: `brew install python@3.13`
- Anthropic API key: [console.anthropic.com](https://console.anthropic.com)

## Quick setup

```bash
# 1. Install tools
brew install ffmpeg fswatch

# 2. Create folders
mkdir -p ~/Desktop/Videos ~/Documents/MeetingNotes ~/meeting-processor

# 3. Python environment
python3.13 -m venv ~/meeting-processor/venv
source ~/meeting-processor/venv/bin/activate
pip install openai-whisper anthropic

# 4. Load the LaunchAgent (auto-starts on login)
launchctl load ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist
```

Full setup guide → [meeting-processor/index.html](https://bunlongheng.github.io/tools/meeting-processor/)
Full architecture → [ARCHITECTURE.md](../meeting-processor/ARCHITECTURE.md)

---

[← Back to all tools](../README.md)
