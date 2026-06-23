# What to Keep vs. What to Cut

A reference for compressing spoken transcripts into agent-ready packs.
The goal is **maximum information density** with **zero meaning loss**.

---

## ✅ KEEP — Always Preserve

### Core Content
- **Central arguments and claims** — the actual point the speaker is making
- **Supporting evidence** — data, statistics, research citations, examples
  that back up claims
- **Logical structure** — cause → effect, problem → solution, premise →
  conclusion chains
- **Novel insights** — ideas the speaker presents as new, contrarian, or
  surprising

### Specifics
- **Proper nouns** — people, companies, products, places, titles (exact
  spelling)
- **Numbers and dates** — statistics, dollar amounts, percentages, years,
  durations
- **Technical terms** — jargon, acronyms, domain-specific vocabulary
  (preserve exactly, don't "simplify")
- **URLs and references** — any resource the speaker explicitly mentions

### Quotes
- **Memorable phrasing** — lines that are clearly crafted, funny,
  provocative, or tweetable
- **Self-attributions** — "I always say…", "My rule is…", "The way I
  think about it…"
- **Definitions** — when the speaker explicitly defines a term or concept
- **Disagreements** — when the speaker pushes back on a common view

### Structure
- **Timestamps** — preserve all original timestamp markers
- **Speaker labels** — who is talking (interviewer vs. guest, etc.)
- **Topic transitions** — moments where the conversation shifts subjects

---

## ❌ CUT — Safe to Remove

### Filler Words (remove on sight)
```
um, uh, ah, er, eh, hmm, mm, mhm, uh-huh, mm-hmm,
like (non-comparative), you know, you know what I mean,
I mean, sort of, kind of, basically, literally, actually,
right?, yeah?, okay?, so (sentence-initial hedge),
honestly, frankly, obviously, clearly (when not adding meaning),
just (when filler), really (when filler), very (when filler),
pretty much, more or less, in a way, at the end of the day,
to be honest, if you will, as it were, if that makes sense,
let me think, how do I say this, what's the word
```

### False Starts
- Abandoned sentence beginnings: "I was going to — actually what I mean is…"
  → keep only the completed thought
- Self-corrections: "It was Tuesday — no, Wednesday" → "It was Wednesday"
- Stuttered restarts: "The the the important thing" → "The important thing"

### Redundant Repetition
- **Restatements** — when the same idea is said 2–3 ways in a row, keep
  the clearest version
  - *Before:* "It's really fast. I mean, it's incredibly quick. The speed
    is just unbelievable."
  - *After:* "It's incredibly fast."
- **Echo responses** — "Yeah, totally, absolutely, right, exactly" from
  the non-speaking participant
- **Conversational scaffolding** — "That's a great question",
  "Thanks for having me", "Let me unpack that"

### Phatic / Social Speech
- Greetings, sign-offs, sponsor reads, ad breaks
- "Before we get into it…" warm-up chatter (unless it contains
  real content)
- Laughter notations `[laughs]` — drop unless the laugh signals irony
  or sarcasm that changes meaning

### Procedural Meta-talk
- "As I mentioned earlier…" — just state the point again (or don't if
  it's truly repeated)
- "We'll get to that later…" — remove; the structure of the pack handles
  ordering
- "If you're watching on YouTube…" — platform-specific asides

---

## ⚠️ JUDGMENT CALLS — Context Decides

| Situation | Default | Override when… |
|---|---|---|
| Anecdotes / stories | Keep (compressed) | The story is pure padding with no takeaway |
| Humor / jokes | Keep if the joke *is* the point | Drop if it's just social lubrication |
| Analogies | Keep the best one | Speaker uses 4 analogies for one idea — keep 1–2 |
| Hedging language ("I think", "maybe") | Cut | The uncertainty is itself important information |
| Crosstalk / interruptions | Cut | The interruption changes the argument |
| Audience Q&A | Keep (compressed) | The question is inaudible or the answer is redundant |
| Self-promotion | Cut | The self-reference is evidence for a claim |

---

## Compression Heuristics

1. **The tweet test** — if a chapter can be summarised in a tweet-length
   sentence without losing its core claim, the chapter is well-compressed.
2. **The "so what?" test** — for any sentence you're unsure about, ask
   "does removing this change what another agent would conclude?" If no,
   cut it.
3. **The quote test** — if no one would ever highlight or screenshot a
   sentence, it's probably scaffolding, not content.
4. **Target ratio** — aim for **40–60% token reduction** on well-spoken
   content, **60–80%** on rambling content.
