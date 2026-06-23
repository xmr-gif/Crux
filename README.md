# ⚡ Crux

> Turn any long video or podcast transcript into a compact, agent-ready bundle — structured, faithful, and small enough to paste straight into another model's context.

Crux is a Claude Skill that accepts a YouTube URL, a file, or raw pasted text, and produces a compressed **crux pack**: title, summary, chapters with timestamps, verbatim key quotes, and a dense outline — all in one Markdown document with an embedded JSON block.

---

## The philosophy (what the video is really saying)

- **Start from a problem, not a solution.** The best small tools fix something people *already complain about*, not something clever you invented.
- **Taste is the moat.** Anyone can prompt an AI. What makes a tool spread is opinionated defaults, a clean experience, and a sharp point of view.
- **Coding agents collapse the gap.** Non-technical builders can now ship real software by describing what they want clearly and iterating.
- **Open source = distribution.** A great README, a demo GIF, and solving one real pain gets you stars, contributors, and reputation — which compounds.
- **Ship the smallest useful version.** A tool that does one thing well beats a half-built platform.

---

## Hard-won lessons from the talk

*The speaker is a humanities major and self-described non-coder who went from never using GitHub to 30,000+ stars in a few months. These are the tactics that actually worked — worth applying to every idea below.*

- **Treat the model as a co-founder, not an assistant.** Describe the *problem* ("all my browser history is here, I hoard tabs — what can we do?"), not a finished spec. Let it propose the idea. Tab Out's best feature (using the new-tab page) was Claude's suggestion.
- **Build around your *real* behavior, not your idealized behavior.** Humans are lazy and forgetful. If a tool needs you to "remember to click a button," you won't — which is why Tab Out lives on the new-tab page you already open constantly.
- **Use it for a week before deciding it works.** Building takes hours; finding the right shape takes a week of actually living with it. He killed many ideas his own behavior didn't support.
- **Cut more than you add.** Models love adding features; the human's job now is subtraction. He *removed* the AI tab-categorizer from Tab Out and it got better.
- **Be opinionated.** "Doing everything means doing nothing; speaking to everybody means speaking to nobody." Generic "all-in-one AI" tools lose — people may as well use Claude directly. A sharp opinion is *why* someone picks your tool.
- **Repurpose underused real estate.** The new-tab page, your phone wallpaper, your social feed — surfaces you already open dozens of times a day — are prime spots to inject the behavior you want (your own "personal ad network").
- **Right model for the job.** Use Claude Code for design and product brainstorming; Codex for execution and bug-fixes once you already know what you want. Default to the best model — cheaper models often cost more in wasted time.
- **Build in public.** Posting Tab Out got ~500k views and an engineer pointed out it didn't even need a Node server — feedback he'd never have gotten in private.
- **Build small, build for fun, build to learn.** "It's hard to compete with somebody who's just there to have fun." Most of these started as non-utilitarian side projects, not businesses.
- **Know and ban AI slop.** Last year's slop = purple gradients; this year's = the "Claude look" (instrument-serif italics). The goalpost keeps moving — name the current slop explicitly and forbid it.

---

## Quick start

### 1. Install dependencies

```bash
pip install youtube-transcript-api tiktoken
```

### 2. Fetch a transcript

```bash
python scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID" -o raw.txt
```

### 3. Auto-compress (first pass)

```bash
python scripts/compress_transcript.py raw.txt -o compressed.txt
```

You'll see a report like:

```
──────────────────────────────────────────────────
  Transcript Compression Report
──────────────────────────────────────────────────
  Method:          tiktoken (cl100k_base)
  Before:            12,847 tokens
  After:              9,231 tokens
  Reduction:          28.1%
  Characters:        51,388 →     36,924
──────────────────────────────────────────────────
  ⚠  This is an automated first pass.
  The agent should further compress by removing
  duplicate ideas and segmenting into chapters.
──────────────────────────────────────────────────
```

### 4. Let the agent finish the job

Provide the raw or auto-compressed transcript to the agent with this skill active. It will:

1. Apply the full cleaning rules from [`references/keep_vs_cut.md`](references/keep_vs_cut.md)
2. Segment into chapters with timestamps
3. Extract the best verbatim quotes
4. Produce the final **Crux Pack** — a single Markdown doc with embedded JSON

---

## What's in the box

```
crux/
├── SKILL.md                          # Agent instructions
├── README.md                         # You are here
├── scripts/
│   ├── fetch_transcript.py           # Pull transcripts from YouTube
│   └── compress_transcript.py        # Automated first-pass compression
└── references/
    └── keep_vs_cut.md                # What to preserve vs. remove
```

---

## Output format

The final transcript pack is a Markdown document containing:

| Section | Purpose |
|---|---|
| **Header** | Title, source, duration, speakers, token reduction stats |
| **Summary** | 2–5 sentence overview |
| **Chapters** | Timestamped sections with compressed text |
| **Key Quotes** | 5–15 verbatim quotes with attribution |
| **Dense Outline** | Hierarchical bullet-point outline |
| **JSON block** | Machine-readable structured data (collapsible) |

The output is designed to be **pasted directly into another agent's context** as compact, faithful source material.

---

## Design decisions

- **Rule-based first pass + agent refinement.** The Python scripts handle mechanical cleanup (filler words, whitespace). The agent handles judgment calls (de-duplication, chapter boundaries, quote selection). Best of both worlds.
- **Verbatim quotes from the original.** Quotes are pulled from the *raw* transcript, not the compressed version, so they're genuinely verbatim.
- **Dual format output.** Markdown for humans, JSON for machines — in the same document.
- **Token counting built in.** Every pack reports its compression ratio. You always know how much context budget you're saving.

---

## Tips

- For videos without auto-captions, paste the transcript manually — the skill handles all three input types.
- The `--json` flag on `fetch_transcript.py` gives you raw segments with start/duration if you want to build your own pipeline.
- The compression script works on **any** transcript, not just YouTube — pipe in podcast transcripts, meeting notes, etc.
