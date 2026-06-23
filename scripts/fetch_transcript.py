#!/usr/bin/env python3
"""
fetch_transcript.py — Pull a transcript from a YouTube video.

Usage:
    python fetch_transcript.py <YOUTUBE_URL_OR_ID> [--output FILE] [--lang LANG]

Dependencies:
    pip install youtube-transcript-api

Outputs the transcript as timestamped plain text, one segment per line:
    [00:00:12] Hello and welcome to the show...
    [00:00:18] Today we're going to talk about...
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print(
        "ERROR: youtube-transcript-api is not installed.\n"
        "Run:  pip install youtube-transcript-api",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_video_id(url_or_id: str) -> str:
    """Extract the 11-char YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for pat in patterns:
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_transcript(segments: list[dict]) -> str:
    """Format transcript segments into timestamped lines."""
    lines = []
    for seg in segments:
        ts = seconds_to_timestamp(seg["start"])
        text = seg["text"].strip().replace("\n", " ")
        lines.append(f"[{ts}] {text}")
    return "\n".join(lines)


def estimate_tokens(text: str) -> int:
    """Estimate token count. Uses tiktoken if available, else char/4."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))
    except (ImportError, Exception):
        return len(text) // 4


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fetch(video_id: str, lang: str = "en") -> list[dict]:
    """Fetch transcript segments for a video."""
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript = ytt_api.fetch(video_id, languages=[lang])
    except Exception:
        # Fallback: try fetching any available language
        try:
            transcript_list = ytt_api.list(video_id)
            transcript = transcript_list.find_transcript([lang]).fetch()
        except Exception as e:
            raise RuntimeError(
                f"Could not fetch transcript for video {video_id}: {e}"
            ) from e

    # Convert FetchedTranscript/Snippet objects to plain dicts
    segments = []
    for item in transcript:
        segments.append({
            "start": getattr(item, "start", None) or item.get("start", 0),
            "text": getattr(item, "text", None) or item.get("text", ""),
            "duration": getattr(item, "duration", None) or item.get("duration", 0),
        })
    return segments


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a YouTube transcript."
    )
    parser.add_argument(
        "url",
        help="YouTube URL or video ID",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write transcript to this file (default: stdout)",
        default=None,
    )
    parser.add_argument(
        "--lang", "-l",
        help="Preferred language code (default: en)",
        default="en",
    )
    parser.add_argument(
        "--json",
        help="Output raw JSON segments instead of formatted text",
        action="store_true",
    )
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    print(f"Fetching transcript for video: {video_id}", file=sys.stderr)

    segments = fetch(video_id, lang=args.lang)

    if args.json:
        output = json.dumps(segments, indent=2, ensure_ascii=False)
    else:
        output = format_transcript(segments)

    tokens = estimate_tokens(output)
    print(f"Fetched {len(segments)} segments (~{tokens:,} tokens)", file=sys.stderr)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
