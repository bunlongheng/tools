# Meeting Processor — Complete Reference

> Drop a video into `~/Desktop/Videos/` → get structured AI meeting notes automatically.

---

## Cost

| Tool | Cost | Notes |
|---|---|---|
| ffmpeg | Free | Open source video tool |
| fswatch | Free | Open source file watcher |
| OpenAI Whisper | **Free** | Runs locally on your Mac, no internet needed |
| Claude API | **~$0.01–$0.05 per meeting** | Only Step 3 costs money. A 1-hour meeting ≈ $0.02 |

You only pay for the Claude API call. Everything else is free.
Get your API key at: https://console.anthropic.com

---

## Requirements

### macOS tools (via Homebrew)
```bash
brew install ffmpeg fswatch
```

### Python (use the Homebrew version, not Apple's system Python)
```bash
brew install python@3.13        # if not already installed
which python3.13                # should return /opt/homebrew/bin/python3.13
```

### Python virtual environment + packages
```bash
python3.13 -m venv ~/meeting-processor/venv
source ~/meeting-processor/venv/bin/activate
pip install openai-whisper anthropic
```

---

## Directory Structure

```
~/meeting-processor/                    ← all scripts
│   ├── watch.sh                        ← pipeline orchestrator
│   ├── summarize.py                    ← Claude API summarizer
│   ├── processor.log                   ← auto-created, rolling log
│   ├── ARCHITECTURE.md                 ← this file
│   └── venv/                           ← Python environment
│
~/Desktop/Videos/                       ← DROP VIDEOS HERE
~/Documents/MeetingNotes/               ← OUTPUT APPEARS HERE
│   ├── meeting-name.mp3                ← extracted audio
│   ├── meeting-name.txt                ← raw transcript
│   └── meeting-name-notes.md          ← AI meeting notes (auto-opens)
│
~/Library/LaunchAgents/
│   └── com.hengb01.meeting-processor.plist  ← auto-start on login
```

---

## Architecture Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        macOS LaunchAgent                                 │
│              ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist  │
│                   Starts watch.sh automatically at login                 │
│                   Restarts it automatically if it crashes                │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ runs
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           watch.sh                                       │
│                                                                          │
│   fswatch --event Created ~/Desktop/Videos/                              │
│        │                                                                 │
│        │   new .mp4 / .mov / .avi / .mkv / .webm detected               │
│        │   sleep 3s  (wait for file to finish writing)                   │
│        ▼                                                                 │
│   ┌──────────┐      ┌──────────────┐      ┌────────────────────────┐    │
│   │ STEP 1   │      │   STEP 2     │      │       STEP 3           │    │
│   │          │      │              │      │                        │    │
│   │  ffmpeg  │─────▶│   Whisper    │─────▶│    Claude API          │    │
│   │          │      │  (local AI)  │      │   (summarize.py)       │    │
│   │ video    │      │              │      │                        │    │
│   │   →      │      │ audio → text │      │ transcript →           │    │
│   │  .mp3    │      │  .txt file   │      │ structured .md notes   │    │
│   │          │      │              │      │                        │    │
│   │ FREE     │      │ FREE         │      │ ~$0.01–$0.05/meeting   │    │
│   └──────────┘      └──────────────┘      └────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
                                                      │
                                                      ▼
                                    ~/Documents/MeetingNotes/
                                    ├── name.mp3
                                    ├── name.txt
                                    └── name-notes.md  ← auto-opens
                                                      │
                                                      ▼
                                    macOS notification fires
```

---

## Step-by-Step Detail

```
User drops video.mp4 into
~/Desktop/Videos/
         │
         │  fswatch fires "--event Created"
         ▼
    [watch.sh starts]
         │
         │  sleep 3s — waits for file to fully write to disk
         │  (prevents reading a half-downloaded file)
         │
         ▼
┌─────────────────────────────────────┐
│  STEP 1 — ffmpeg                    │
│                                     │
│  ffmpeg -i video.mp4                │
│    -vn            (strip video)     │
│    -acodec mp3    (encode as MP3)   │
│    -ab 128k       (128kbps quality) │
│    -y             (overwrite ok)    │
│    video.mp3                        │
│                                     │
│  Output: video.mp3                  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  STEP 2 — OpenAI Whisper            │
│                                     │
│  whisper video.mp3                  │
│    --model base     (see table)     │
│    --output_dir MeetingNotes/       │
│    --output_format txt              │
│    --language en                    │
│                                     │
│  Runs 100% locally on your Mac      │
│  No data sent to the internet       │
│                                     │
│  Output: video.txt                  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  STEP 3 — Claude API                │
│                                     │
│  python3 summarize.py video.txt     │
│                                     │
│  Reads transcript text              │
│  Sends to Claude API (Sonnet 4.6)   │
│  Gets back structured notes         │
│                                     │
│  Sections extracted:                │
│  1. Meeting Summary                 │
│  2. Action Items (checkboxes)       │
│  3. Key Decisions                   │
│  4. Open Questions                  │
│  5. Next Steps                      │
│  6. Notable Insights                │
│                                     │
│  Output: video-notes.md             │
│  + macOS notification fires         │
│  + file auto-opens on your Mac      │
└─────────────────────────────────────┘
```

---

## Whisper Model Comparison

Change `WHISPER_MODEL` in `watch.sh` line 14:

| Model | Size | Speed | Accuracy | Best for |
|-------|------|-------|----------|----------|
| `tiny` | 75MB | fastest | basic | quick tests |
| `base` | 145MB | fast | good | clear audio ✓ default |
| `small` | 465MB | moderate | better | accented speech |
| `medium` | 1.5GB | slow | great | noisy background |
| `large` | 3GB | slowest | best | multiple speakers |

---

## Full Script: watch.sh

```bash
#!/bin/zsh
# watch.sh — watches ~/Desktop/Videos/ for new video files and runs the
# full processing pipeline: video → audio → transcript → AI meeting notes

WATCH_DIR="$HOME/Desktop/Videos"
OUTPUT_DIR="$HOME/Documents/MeetingNotes"
VENV="$HOME/meeting-processor/venv"
SCRIPT_DIR="$HOME/meeting-processor"
LOG_FILE="$SCRIPT_DIR/processor.log"
WHISPER_MODEL="base"   # tiny | base | small | medium | large

# ── helpers ──────────────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

notify() {
    osascript -e "display notification \"$2\" with title \"Meeting Processor\" subtitle \"$1\""
}

# ── pipeline ─────────────────────────────────────────────────────────────────

process_video() {
    local video_file="$1"
    local name
    name=$(basename "$video_file" | sed 's/\.[^.]*$//')
    local audio_file="$OUTPUT_DIR/${name}.mp3"
    local transcript_file="$OUTPUT_DIR/${name}.txt"
    local summary_file="$OUTPUT_DIR/${name}-notes.md"

    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "▶  New video detected: $name"
    notify "Processing started" "$name"

    # Step 1: video → audio
    log "[1/3] Extracting audio with ffmpeg..."
    ffmpeg -i "$video_file" -vn -acodec mp3 -ab 128k -y "$audio_file" >> "$LOG_FILE" 2>&1
    if [[ $? -ne 0 || ! -f "$audio_file" ]]; then
        log "ERROR: ffmpeg failed"
        notify "Failed at step 1" "ffmpeg audio extraction failed"
        return 1
    fi
    log "    ✓ Audio saved: $audio_file"

    # Step 2: audio → transcript
    log "[2/3] Transcribing with Whisper (model: $WHISPER_MODEL)..."
    source "$VENV/bin/activate"
    whisper "$audio_file" \
        --model "$WHISPER_MODEL" \
        --output_dir "$OUTPUT_DIR" \
        --output_format txt \
        --language en \
        >> "$LOG_FILE" 2>&1
    if [[ $? -ne 0 || ! -f "$transcript_file" ]]; then
        log "ERROR: Whisper transcription failed"
        notify "Failed at step 2" "Whisper transcription failed"
        return 1
    fi
    log "    ✓ Transcript saved: $transcript_file"

    # Step 3: transcript → AI summary
    log "[3/3] Generating AI meeting notes with Claude..."
    python3 "$SCRIPT_DIR/summarize.py" "$transcript_file" > "$summary_file" 2>> "$LOG_FILE"
    if [[ $? -ne 0 || ! -s "$summary_file" ]]; then
        log "ERROR: AI summarization failed (check ANTHROPIC_API_KEY)"
        notify "Failed at step 3" "AI summarization failed — check API key"
        return 1
    fi
    log "    ✓ Notes saved: $summary_file"

    log "✅ Done: $name"
    notify "✅ Done!" "Notes ready → ${name}-notes.md"
    open "$summary_file"
}

# ── main ─────────────────────────────────────────────────────────────────────

log "Meeting Processor started — watching: $WATCH_DIR"

fswatch -0 --event Created "$WATCH_DIR" | while IFS= read -r -d "" event; do
    if [[ "$event" =~ \.(mp4|mov|avi|mkv|webm|m4v|MP4|MOV|AVI|MKV)$ ]]; then
        sleep 3
        process_video "$event"
    fi
done
```

---

## Full Script: summarize.py

```python
#!/usr/bin/env python3
"""
summarize.py — sends a meeting transcript to Claude API
and returns structured meeting notes as Markdown.

Usage:
    python3 summarize.py path/to/transcript.txt

Output:
    Markdown printed to stdout (watch.sh redirects it to a .md file)
"""

import sys
import anthropic
from pathlib import Path
from datetime import datetime


PROMPT_TEMPLATE = """You are a meeting assistant. Analyze the transcript below and extract:

## 1. Meeting Summary
2-3 sentences covering the main topic and outcome.

## 2. Action Items
Each as a checkbox with owner + deadline if mentioned.
Format: `- [ ] Task — @Owner (due: date or "no date")`

## 3. Key Decisions
Concrete decisions made during the meeting.

## 4. Open Questions
Unresolved questions or items still being debated.

## 5. Next Steps
Follow-ups, next meetings, deliverables.

## 6. Notable Insights
Risks, ideas, or blockers surfaced during discussion.

---TRANSCRIPT---
{transcript}
"""


def summarize(transcript_path: str) -> str:
    path = Path(transcript_path)
    transcript = path.read_text(encoding="utf-8").strip()
    filename = path.stem
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Reads ANTHROPIC_API_KEY from environment variable automatically
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(transcript=transcript)
        }]
    )

    summary_body = message.content[0].text

    return f"""# Meeting Notes: {filename}

> **Processed:** {date_str}
> **Source:** `{transcript_path}`

---

{summary_body}
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: summarize.py <transcript.txt>", file=sys.stderr)
        sys.exit(1)
    print(summarize(sys.argv[1]))
```

---

## Full Config: LaunchAgent plist

File location: `~/Library/LaunchAgents/com.hengb01.meeting-processor.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hengb01.meeting-processor</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/Users/hengb01/meeting-processor/watch.sh</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <!-- Replace with your real key from console.anthropic.com -->
        <key>ANTHROPIC_API_KEY</key>
        <string>YOUR_ANTHROPIC_API_KEY_HERE</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>

    <!-- Start automatically when you log in -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Restart automatically if it ever crashes -->
    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/hengb01/meeting-processor/processor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/hengb01/meeting-processor/processor.log</string>
</dict>
</plist>
```

---

## Setup Steps (in order)

```bash
# 1. Install system tools
brew install ffmpeg fswatch

# 2. Create folders
mkdir -p ~/Desktop/Videos ~/Documents/MeetingNotes ~/meeting-processor

# 3. Create Python environment
python3.13 -m venv ~/meeting-processor/venv
source ~/meeting-processor/venv/bin/activate
pip install openai-whisper anthropic

# 4. Copy watch.sh and summarize.py into ~/meeting-processor/
chmod +x ~/meeting-processor/watch.sh ~/meeting-processor/summarize.py

# 5. Add your API key to the plist
nano ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist
# Change: YOUR_ANTHROPIC_API_KEY_HERE → your real key

# 6. Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist

# 7. Verify it's running
launchctl list | grep meeting-processor
```

---

## Day-to-Day Commands

```bash
# Check if the service is running
launchctl list | grep meeting-processor

# Watch the log live (see each step as it runs)
tail -f ~/meeting-processor/processor.log

# Stop the service
launchctl unload ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist

# Start the service
launchctl load ~/Library/LaunchAgents/com.hengb01.meeting-processor.plist

# Run manually in terminal (useful for debugging)
~/meeting-processor/watch.sh

# Test the AI summarizer on an existing transcript
source ~/meeting-processor/venv/bin/activate
python3 ~/meeting-processor/summarize.py ~/Documents/MeetingNotes/some-transcript.txt

# Change Whisper accuracy (edit watch.sh line 14)
# WHISPER_MODEL="small"   ← better for accented or noisy audio
```

---

## What a Finished Output Looks Like

After dropping `standup-feb-20.mp4` into `~/Desktop/Videos/`:

```
~/Documents/MeetingNotes/
├── standup-feb-20.mp3          ← audio (you can delete after)
├── standup-feb-20.txt          ← raw transcript
└── standup-feb-20-notes.md     ← opens automatically
```

`standup-feb-20-notes.md`:

```markdown
# Meeting Notes: standup-feb-20

> **Processed:** 2026-02-20 09:15
> **Source:** `.../standup-feb-20.txt`

---

## 1. Meeting Summary
Team reviewed Q1 roadmap. Auth refactor is priority #1.
March 15 is the hard deadline.

## 2. Action Items
- [ ] Write auth refactor spec — @Sara (due: Wednesday)
- [ ] Get budget approval — @Mark (due: no date)

## 3. Key Decisions
- Auth refactor ships before March 15 release
- New infra decision deferred to next sprint

## 4. Open Questions
- Will new infra be ready before March 15?

## 5. Next Steps
- Next standup: Monday 9am
- Sara shares spec draft by Wednesday

## 6. Notable Insights
- Current auth code is a risk — any delay blocks the entire release
```

---

## How to Push This to GitHub (bheng2026/tools)

When you're ready to add this to your tools repo:

```bash
# 1. Clone your tools repo
git clone https://github.com/bheng2026/tools.git ~/tools

# 2. Copy the meeting processor folder into it
cp -r ~/meeting-processor ~/tools/meeting-processor

# 3. Commit and push
cd ~/tools
git checkout -b feature/meeting-processor
git add meeting-processor/
git commit -m "Add meeting processor automation tool"
git push origin feature/meeting-processor

# 4. Open a PR on GitHub
gh pr create --title "Add meeting processor" --body "Automated pipeline: video → audio → transcript → AI meeting notes"

# 5. Merge it
gh pr merge --squash
```
