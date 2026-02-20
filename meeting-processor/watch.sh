#!/bin/zsh
# watch.sh — watches ~/Desktop/Videos/ for new video files and runs the
# full processing pipeline: video → audio → transcript → AI meeting notes

WATCH_DIR="$HOME/Desktop/Videos"
OUTPUT_DIR="$HOME/Documents/MeetingNotes"
VENV="$HOME/meeting-processor/venv"
SCRIPT_DIR="$HOME/meeting-processor"
LOG_FILE="$SCRIPT_DIR/processor.log"

# Whisper model: tiny | base | small | medium | large
# base = good balance of speed and accuracy for meetings
WHISPER_MODEL="base"

# ── helpers ──────────────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

notify() {
    # macOS notification
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

    # ── Step 1: video → audio ────────────────────────────────────────────────
    log "[1/3] Extracting audio with ffmpeg..."
    ffmpeg -i "$video_file" \
        -vn \
        -acodec mp3 \
        -ab 128k \
        -y \
        "$audio_file" \
        >> "$LOG_FILE" 2>&1

    if [[ $? -ne 0 || ! -f "$audio_file" ]]; then
        log "ERROR: ffmpeg failed for $video_file"
        notify "Failed at step 1" "ffmpeg audio extraction failed"
        return 1
    fi
    log "    ✓ Audio saved: $audio_file"

    # ── Step 2: audio → transcript ───────────────────────────────────────────
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

    # ── Step 3: transcript → AI summary ─────────────────────────────────────
    log "[3/3] Generating AI meeting notes with Claude..."

    python3 "$SCRIPT_DIR/summarize.py" "$transcript_file" > "$summary_file" 2>> "$LOG_FILE"

    if [[ $? -ne 0 || ! -s "$summary_file" ]]; then
        log "ERROR: AI summarization failed (check ANTHROPIC_API_KEY)"
        notify "Failed at step 3" "AI summarization failed — check API key"
        return 1
    fi
    log "    ✓ Notes saved: $summary_file"

    # ── Done ─────────────────────────────────────────────────────────────────
    log "✅ Done processing: $name"
    notify "✅ Done!" "Notes ready → $name-notes.md"

    # Open the summary in the default markdown viewer
    open "$summary_file"
}

# ── main ─────────────────────────────────────────────────────────────────────

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Meeting Processor started"
log "Watching: $WATCH_DIR"
log "Output:   $OUTPUT_DIR"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --event Created catches new files (also catches copies/downloads finishing)
fswatch -0 --event Created "$WATCH_DIR" | while IFS= read -r -d "" event; do
    if [[ "$event" =~ \.(mp4|mov|avi|mkv|webm|m4v|MP4|MOV|AVI|MKV)$ ]]; then
        sleep 3   # brief pause to let the file finish writing to disk
        process_video "$event"
    fi
done
