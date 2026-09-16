import os
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

def synthesize(query, papers):
    context = build_context(papers)
    prompt = f"""You are a research assistant. Below are {len(papers)} research snippets on the topic: "{query}"
    {context}
    Based ONLY on the snippets above, write:
    1. Established Findings — what most sources agree on (cite sources like [Source 1])
    2. Where Researchers Disagree — any conflicting or mixed findings
    3. Open Gaps — angles not covered by these sources
    Do not use outside knowledge. If the snippets don't cover something, say so plainly instead of guessing."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    query = "intermittent fasting insulin resistance"
    papers = search_scholar(query)
    brief = synthesize(query, papers)
    print(brief)