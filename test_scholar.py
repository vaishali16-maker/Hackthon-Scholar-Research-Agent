import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

def search_scholar(query, num_results=10, recent_years=None):
    params = {
        "engine": "google_scholar",
        "q": query,
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    if recent_years:
        from datetime import datetime
        params["as_ylo"] = str(datetime.now().year - recent_years)
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])


def search_scholar_combined(query, num_established=8, num_recent=5, recent_years=3):
    established = search_scholar(query, num_results=num_established)
    recent = search_scholar(query, num_results=num_recent, recent_years=recent_years)
    seen_titles = set()
    combined = []
    for paper in established:
        title = paper.get("title", "")
        if title not in seen_titles:
            paper["_source_type"] = "established"
            combined.append(paper)
            seen_titles.add(title)
    for paper in recent:
        title = paper.get("title", "")
        if title not in seen_titles:
            paper["_source_type"] = "recent"
            combined.append(paper)
            seen_titles.add(title)
    return combined


if __name__ == "__main__":
    papers = search_scholar_combined("intermittent fasting insulin resistance")
    for i, paper in enumerate(papers, 1):
        tag = paper.get("_source_type", "")
        print(f"\n--- Result {i} [{tag}] ---")
        print("Title:", paper.get("title"))
        print("Publication info:", paper.get("publication_info", {}).get("summary"))