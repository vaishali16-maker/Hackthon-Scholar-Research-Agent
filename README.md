# Scholar Research Assistant

An AI research agent that turns a topic into a citation-grounded research brief — and goes one step further by checking whether the gaps in the literature are also gaps in the patent landscape.

Built for the **SerpApi India Hackathon 2026** — AI Agents track.

---

## What it does

Give it a research topic. It:

1. **Searches Google Scholar** (via SerpApi) for both highly-cited foundational papers and recent publications on the topic.
2. **Filters for genuine relevance** — a second AI pass separates papers that are directly about the topic from ones that only share a keyword, so an unstudied or obscure topic gets an honest "not much research exists" answer instead of a forced summary.
3. **Synthesizes a structured brief** with three sections:
   - **Established Findings** — what most sources agree on, with citations
   - **Where Researchers Disagree** — genuine contradictions between sources
   - **Open Gaps** — angles the literature hasn't covered
4. **Cross-references the Open Gaps against Google Patents** (via SerpApi) and ranks them by relative patent activity — surfacing which gaps are not just academically unstudied, but also comparatively unexplored commercially.

## Who it helps

Researchers, students, and founders doing early-stage literature review — anyone who currently has to manually read and cross-reference a dozen papers to answer "what's already known, what's disputed, and what's actually open?" This automates that first pass, with real citations attached so nothing is taken on faith.

## How it uses SerpApi

SerpApi is not a bolt-on feature here — it's the entire data backbone:

- **Google Scholar engine**: fetches both relevance-ranked and recency-filtered results per query, which are then filtered, cited, and synthesized into the brief. Without this, the tool has no content to work with.
- **Google Patents engine**: powers the differentiator feature — checking each identified research gap against real patent data to see whether it's also commercially unexplored, not just academically unstudied.

## Architecture

```
User query
   │
   ▼
test_scholar.py  →  SerpApi Google Scholar (established + recent results)
   │
   ▼
relevance.py     →  filters direct vs. adjacent papers (AI relevance pass)
   │
   ▼
synthesize.py    →  writes the 3-part brief (AI synthesis pass)
   │
   ▼
synthesize.py    →  extracts short gap phrases from "Open Gaps"
   │
   ▼
patents.py       →  SerpApi Google Patents (per gap phrase, ranked)
   │
   ▼
main.py (FastAPI) →  /research endpoint returns everything as JSON
   │
   ▼
frontend.html    →  tabbed brief, source sidebar, patent activity panel
```

## Tech stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI**: Groq (openai/gpt-oss-20b) for relevance filtering, synthesis, and gap extraction
- **Search**: SerpApi (Google Scholar + Google Patents engines)
- **Frontend**: Plain HTML/CSS/JS with Tailwind (CDN) and marked.js for Markdown rendering — no framework, no build step

## Running it locally

**1. Clone and install dependencies:**
```bash
git clone https://github.com/vaishali16-maker/Hackthon-Scholar-Research-Agent.git
cd Hackthon-Scholar-Research-Agent
pip install -r requirements.txt
```

**2. Add your API keys** — create a `.env` file in the project root:
```
SERPAPI_KEY=your_serpapi_key_here
GROQ_API_KEY=your_groq_key_here
```

**3. Start the backend:**
```bash
uvicorn main:app --reload
```

**4. Open the frontend:**
Open `frontend.html` directly in your browser (no server needed for the frontend itself).

**5. Search:**
Type a research topic, hit Research. Check "Also check patent activity for open gaps" to see the patent cross-reference feature — this adds 1-2 minutes since it runs several additional searches.

## Known limitations

- The patent cross-check uses relative ranking (lowest activity among the identified gaps) rather than an absolute "zero activity" claim — Google Patents' full-text search returns large counts even for narrow phrases, so relative comparison is the more honest signal.
- Relevance filtering and synthesis occasionally retry due to LLM response variability; this adds a few seconds but improves reliability.
- Currently single-query, no conversation memory between searches.

## What's next

- Persist past briefs so users can revisit or compare searches
- Let users upload their own PDF alongside the Scholar search, for a hybrid personal + public literature review
- Expand the patent cross-check to also flag *which* gaps have nearby but not exact patent activity, for a fuller picture of adjacent commercial interest

---

Built with [SerpApi](https://serpapi.com) for the India Hackathon 2026.