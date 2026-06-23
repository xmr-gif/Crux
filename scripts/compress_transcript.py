#!/usr/bin/env python3
"""
compress_transcript.py — Automated first-pass transcript compression.

Usage:
    python compress_transcript.py <INPUT_FILE> [--output FILE]
    cat transcript.txt | python compress_transcript.py - [--output FILE]

What it does (rule-based, no LLM needed):
  1. Strips filler words and verbal tics
  2. Collapses redundant whitespace and empty lines
  3. Removes common phatic phrases and meta-talk
  4. Normalises punctuation
  5. Reports before / after token counts

This is a FIRST PASS. The agent should review and further compress
the output using judgment (de-duplication, chapter segmentation, etc.).
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Filler patterns
# ---------------------------------------------------------------------------

# Single filler words — matched as whole words, case-insensitive
FILLER_WORDS = [
    r"um", r"uh", r"ah", r"er", r"eh", r"hmm", r"mm",
    r"mhm", r"uh-huh", r"uh huh", r"mm-hmm", r"mm hmm",
    r"like",
]

# Filler phrases — matched as whole phrases
FILLER_PHRASES = [
    r"you know what I mean",
    r"you know what i mean",
    r"what I mean is",
    r"what i mean is",
    r"if that makes sense",
    r"at the end of the day",
    r"to be honest",
    r"to be fair",
    r"if you will",
    r"as it were",
    r"let me think",
    r"how do I say this",
    r"how do i say this",
    r"what's the word",
    r"more or less",
    r"pretty much",
    r"sort of",
    r"kind of",
    r"you know",
    r"I mean",
    r"i mean",
]

# Adverb fillers — these are stripped everywhere (sentence-start AND
# mid-sentence after commas) because in transcripts they're almost
# always verbal tics rather than meaningful modifiers.
ADVERB_FILLERS = [
    r"basically",
    r"literally",
    r"actually",
    r"honestly",
    r"frankly",
    r"obviously",
    r"clearly",
]

# Words to remove only when used as fillers (start of sentence or
# standalone, not when they carry meaning in context)
SENTENCE_START_FILLERS = [
    r"basically",
    r"literally",
    r"actually",
    r"honestly",
    r"frankly",
    r"obviously",
    r"clearly",
    r"so,?",
    r"well,?",
    r"right,?",
    r"okay,?",
    r"yeah,?",
]

# Phatic / meta phrases to strip entirely
PHATIC_PHRASES = [
    r"that's a great question",
    r"that's a really great question",
    r"that's a good question",
    r"thanks for having me",
    r"thank you for having me",
    r"thanks for joining us",
    r"before we get into it",
    r"without further ado",
    r"let's dive right in",
    r"let's jump right in",
    r"let's get into it",
    r"as I mentioned earlier",
    r"as i mentioned earlier",
    r"like I said before",
    r"like i said before",
    r"we'll get to that later",
    r"if you're watching on youtube",
    r"if you're listening on",
    r"make sure to subscribe",
    r"hit the like button",
    r"smash that like button",
    r"don't forget to subscribe",
    r"leave a comment below",
]

# Audience interaction markers to strip
BRACKETS_TO_STRIP = [
    r"\[laughs?\]",
    r"\[laughter\]",
    r"\[chuckles?\]",
    r"\[applause\]",
    r"\[music\]",
    r"\[inaudible\]",
    r"\[crosstalk\]",
]


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------

def _compile_patterns():
    """Pre-compile all regex patterns for performance."""
    patterns = []

    # Bracket annotations
    for pat in BRACKETS_TO_STRIP:
        patterns.append((re.compile(pat, re.IGNORECASE), ""))

    # Phatic phrases (longest first to match greedily)
    for phrase in sorted(PHATIC_PHRASES, key=len, reverse=True):
        patterns.append((
            re.compile(r"\b" + phrase + r"[.,;!?]?\s*", re.IGNORECASE),
            "",
        ))

    # Filler phrases (longest first)
    for phrase in sorted(FILLER_PHRASES, key=len, reverse=True):
        patterns.append((
            re.compile(r",?\s*\b" + phrase + r"\b,?\s*", re.IGNORECASE),
            " ",
        ))

    # Adverb fillers — strip anywhere (after comma, at start, etc.)
    for word in ADVERB_FILLERS:
        patterns.append((
            re.compile(r",?\s*\b" + word + r"\b,?\s*", re.IGNORECASE),
            " ",
        ))

    # Sentence-start fillers (so, well, right, okay, yeah)
    for word in SENTENCE_START_FILLERS:
        patterns.append((
            re.compile(r"(?:^|(?<=\.\s))" + word + r"\s+", re.IGNORECASE | re.MULTILINE),
            "",
        ))

    # Single filler words
    for word in FILLER_WORDS:
        patterns.append((
            re.compile(r"\b" + word + r"\b[,.]?\s*", re.IGNORECASE),
            " ",
        ))

    return patterns


PATTERNS = _compile_patterns()


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------

def strip_fillers(text: str) -> str:
    """Apply all filler/phatic removal patterns."""
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def cleanup_artifacts(text: str) -> str:
    """Fix punctuation artifacts left behind after filler removal."""
    # Remove dangling commas: ", ," → ","
    text = re.sub(r",\s*,", ",", text)
    # Remove orphan commas at start of clause: "is, the" after filler removed
    text = re.sub(r"(\w)\s*,\s*,\s*", r"\1, ", text)
    # Comma-space-period or period-space-comma
    text = re.sub(r",\s*\.", ".", text)
    text = re.sub(r"\.\s*,", ".", text)
    # Double periods
    text = re.sub(r"\.{2,}", ".", text)
    # Period followed by question/exclamation: ".?" → "?"
    text = re.sub(r"\.\s*([?!])", r"\1", text)
    # Double em-dashes with space: "— —" → "—"
    text = re.sub(r"—\s*—", "—", text)
    text = re.sub(r"--\s*--", "--", text)
    # Dangling comma after "]": "] , the" → "] the"
    text = re.sub(r"(\])\s*,\s+", r"\1 ", text)
    # Leading comma after timestamp: "[00:12] , so" → "[00:12] so"
    text = re.sub(r"(\])\s+,\s*", r"\1 ", text)
    # Orphan punctuation at line start
    text = re.sub(r"^\s*[,;]\s*", "", text, flags=re.MULTILINE)
    # Spaces before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    # Multiple spaces
    text = re.sub(r"  +", " ", text)
    return text


def normalise_whitespace(text: str) -> str:
    """Collapse runs of whitespace; trim blank lines."""
    # Multiple spaces → single space
    text = re.sub(r"[ \t]+", " ", text)
    # Multiple newlines → double newline (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim each line
    lines = [line.strip() for line in text.split("\n")]
    # Drop fully empty lines that aren't paragraph breaks
    cleaned = []
    prev_empty = False
    for line in lines:
        if line == "":
            if not prev_empty:
                cleaned.append("")
                prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    return "\n".join(cleaned).strip()


def normalise_punctuation(text: str) -> str:
    """Fix common punctuation artifacts from transcription."""
    # Double periods
    text = re.sub(r"\.{2,}", ".", text)
    # Space before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    # Missing space after punctuation
    text = re.sub(r"([.,;:!?])([A-Za-z])", r"\1 \2", text)
    return text


def compress(text: str) -> str:
    """Run the full compression pipeline."""
    text = strip_fillers(text)
    text = cleanup_artifacts(text)
    text = normalise_punctuation(text)
    text = normalise_whitespace(text)
    return text


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> tuple[int, str]:
    """
    Count tokens. Returns (count, method).
    Uses tiktoken if available, otherwise chars/4.
    """
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text)), "tiktoken (cl100k_base)"
    except ImportError:
        return len(text) // 4, "estimate (chars/4)"
    except Exception:
        return len(text) // 4, "estimate (chars/4)"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="First-pass transcript compression."
    )
    parser.add_argument(
        "input",
        help="Input transcript file (use '-' for stdin)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write compressed transcript to this file (default: stdout)",
        default=None,
    )
    args = parser.parse_args()

    # Read input
    if args.input == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text(encoding="utf-8")

    # Compress
    compressed = compress(raw)

    # Token counts
    before_tokens, method = count_tokens(raw)
    after_tokens, _ = count_tokens(compressed)
    if before_tokens > 0:
        reduction = (1 - after_tokens / before_tokens) * 100
    else:
        reduction = 0

    # Report
    report = (
        f"{'─' * 50}\n"
        f"  Transcript Compression Report\n"
        f"{'─' * 50}\n"
        f"  Method:          {method}\n"
        f"  Before:          {before_tokens:>8,} tokens\n"
        f"  After:           {after_tokens:>8,} tokens\n"
        f"  Reduction:       {reduction:>7.1f}%\n"
        f"  Characters:      {len(raw):>8,} → {len(compressed):>8,}\n"
        f"{'─' * 50}\n"
        f"  ⚠  This is an automated first pass.\n"
        f"  The agent should further compress by removing\n"
        f"  duplicate ideas and segmenting into chapters.\n"
        f"{'─' * 50}"
    )
    print(report, file=sys.stderr)

    # Output
    if args.output:
        Path(args.output).write_text(compressed, encoding="utf-8")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(compressed)


if __name__ == "__main__":
    main()
