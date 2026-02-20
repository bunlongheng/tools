#!/usr/bin/env python3
"""
summarize.py — takes a transcript .txt file and returns a structured meeting
summary using the Claude API.

Usage:
    python3 summarize.py <path/to/transcript.txt>

Output:
    Markdown to stdout (redirected to .md file by watch.sh)
"""

import sys
import anthropic
from pathlib import Path
from datetime import datetime


PROMPT_TEMPLATE = """You are a meeting assistant. Analyze the transcript below and extract the following sections. Be specific, use real names from the transcript where possible, and keep each section concise.

## 1. Meeting Summary
2–3 sentences covering the main topic and outcome.

## 2. Action Items
Each item as a checkbox with owner and deadline if mentioned.
Format: `- [ ] Task description — @Owner (due: date or "no date")`

## 3. Key Decisions
Bullet list of concrete decisions made during the meeting.

## 4. Open Questions
Unresolved questions or items still being debated.

## 5. Next Steps
What happens after this meeting — follow-ups, next meetings, deliverables.

## 6. Notable Insights
Any interesting ideas, risks, or blockers surfaced during discussion.

---TRANSCRIPT---
{transcript}
"""


def summarize(transcript_path: str) -> str:
    path = Path(transcript_path)
    if not path.exists():
        print(f"ERROR: transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    transcript = path.read_text(encoding="utf-8").strip()
    if not transcript:
        print("ERROR: transcript file is empty", file=sys.stderr)
        sys.exit(1)

    filename = path.stem
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(transcript=transcript),
            }
        ],
    )

    summary_body = message.content[0].text

    output = f"""# Meeting Notes: {filename}

> **Processed:** {date_str}
> **Source transcript:** `{transcript_path}`

---

{summary_body}
"""
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: summarize.py <transcript.txt>", file=sys.stderr)
        sys.exit(1)

    result = summarize(sys.argv[1])
    print(result)
