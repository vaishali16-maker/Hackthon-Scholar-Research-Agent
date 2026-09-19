import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def score_relevance(query, papers, max_retries=2):
    if not papers:
        return [], []
    listing = ""
    for i, p in enumerate(papers, 1):
        listing += f"{i}. {p.get('title', '')} — {p.get('snippet', '')}\n"
    prompt = f"""You are judging research relevance for a literature-review tool. Topic: "{query}"Papers found:{listing}
              Classify each paper into one of two groups:
            - DIRECT: the paper substantively discusses the core topic — even if it focuses on one specific mechanism, sub-population, or related outcome.
              Only exclude a paper from DIRECT if the topic is barely mentioned in passing or the paper is really about something else entirely.
            - ADJACENT: the paper shares a keyword or general subject area, but is not meaningfully about this topic.
              Be generous with DIRECT — when in doubt, include it as DIRECT rather than ADJACENT.
              Respond ONLY with JSON in this exact shape, using paper numbers:
            {{"direct": [1,3], "adjacent": [2,5]}}
            If a group is empty, use an empty array. No explanation."""
    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content.strip()
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            result = json.loads(raw[start:end])
            direct = [papers[i - 1] for i in result.get("direct", []) if 1 <= i <= len(papers)]
            adjacent = [papers[i - 1] for i in result.get("adjacent", []) if 1 <= i <= len(papers)]
            return direct, adjacent
        except (ValueError, json.JSONDecodeError) as e:
            print(f"RELEVANCE PARSING FAILED (attempt {attempt + 1}/{max_retries})")
            print("Raw AI response was:", raw)
            print("Error:", e)
    print("All relevance parsing attempts failed — falling back to empty result")
    return [], []