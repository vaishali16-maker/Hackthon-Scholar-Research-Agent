import os
import json
from dotenv import load_dotenv
from groq import Groq
from test_scholar import search_scholar_combined as search_scholar

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_context(papers):
    context = ""
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "")
        snippet = paper.get("snippet", "")
        pub_info = paper.get("publication_info", {}).get("summary", "")
        context += f"\n[Source {i}] {title} ({pub_info})\n{snippet}\n"
    return context

def synthesize(query, papers, max_retries=2):
    context = build_context(papers)
    prompt = f"""You are a research assistant. Below are {len(papers)} research snippets on the topic: "{query}"{context}
             Based ONLY on the snippets above, write:
             1. Established Findings — what most sources agree on (cite sources like [Source 1])
             2. Where Researchers Disagree — any conflicting or mixed findings
             3. Open Gaps — angles not covered by these sources
             Keep each section reasonably concise so the full response fits. Do not use outside knowledge. 
             If the snippets don't cover something, say so plainly instead of guessing."""
    for attempt in range(max_retries):
        print(f"Generating brief... (attempt {attempt + 1}/{max_retries})")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3500,
            timeout=60
        )
        content = response.choices[0].message.content.strip()
        finish_reason = response.choices[0].finish_reason
        if not content:
            print(f"SYNTHESIS: empty response (attempt {attempt + 1}/{max_retries})")
            continue
        if finish_reason == "length":
            print(f"SYNTHESIS: response was cut off (hit token limit) on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                continue
        print("Brief generation complete.")
        return content
    print("All synthesis attempts failed or were truncated — returning last content anyway")
    return content
    print("All synthesis attempts failed — returning empty string")
    return ""

def extract_gap_phrases(brief, max_retries=2):
    gaps_section = brief
    for marker in ["3. Open Gaps", "**3. Open Gaps", "Open Gaps"]:
        idx = brief.find(marker)
        if idx != -1:
            gaps_section = brief[idx:]
            break
    prompt =f"""Below is the "Open Gaps" section of a research brief.
            Extract each distinct gap as a SHORT phrase (4-7 words) suitable for searching a patent database.
            Rules:
                - NEVER use abbreviations (write "intermittent fasting" in full, not "IF")
                - Always keep the core topic of the brief in the phrase, not just the gap detail alone
                - Be specific enough that the phrase wouldn't match unrelated fields
            Examples of good phrases: "intermittent fasting protocol comparison", "intermittent fasting drug interaction risk", 
            "intermittent fasting long-term adherence"
            Examples of BAD phrases: "IF protocol comparison" (abbreviation), "age group effects" (too generic, lost the topic)
            Respond ONLY with a JSON array of strings, e.g. ["gap phrase one", "gap phrase two"].
            If there are no gaps, respond with exactly: []
            Text:{gaps_section}"""
    for attempt in range(max_retries):
        print(f"Extracting gap phrases... (attempt {attempt + 1}/{max_retries})")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=60
        )
        raw = response.choices[0].message.content.strip()
        if not raw:
            print(f"GAP EXTRACTION: empty response (attempt {attempt + 1}/{max_retries})")
            continue
        try:
            start = raw.index("[")
            end = raw.rindex("]") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            print(f"GAP EXTRACTION PARSING FAILED (attempt {attempt + 1}/{max_retries})")
            print("Raw AI response was:", raw)
            print("Error:", e)
    print("All gap extraction attempts failed — returning empty list")
    return []


if __name__ == "__main__":
    from patents import check_patent_activity
    query = "intermittent fasting insulin resistance"
    papers = search_scholar(query)
    brief = synthesize(query, papers)
    print(brief)
    gaps = extract_gap_phrases(brief)
    print("\n--- Extracted Gap Phrases ---")
    for g in gaps:
        print("-", g)
    patent_results = []
    for gap in gaps:
        result = check_patent_activity(gap)
        patent_results.append(result)
    patent_results.sort(key=lambda r: r["total_patents"])
    print("\n--- Patent Activity Check (ranked, lowest activity first) ---")
    for r in patent_results:
        print(f"\nGap: {r['query']}")
        print(f"  Total patents: {r['total_patents']}")