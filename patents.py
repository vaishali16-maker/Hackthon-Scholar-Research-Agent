import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
load_dotenv()

def check_patent_activity(query, low_activity_threshold=20):
    params = {
        "engine": "google_patents",
        "q": query,  
        "api_key": os.getenv("SERPAPI_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    total_results = results.get("search_information", {}).get("total_results", 0)
    top_patents = results.get("organic_results", [])[:3]
    return {
        "query": query,
        "total_patents": total_results,
        "is_low_activity": total_results < low_activity_threshold,
        "sample_patents": [
            {
                "title": p.get("title"),
                "link": p.get("patent_link"),
                "assignee": p.get("assignee"),
                "publication_date": p.get("publication_date")
            } for p in top_patents
        ]
    }

if __name__ == "__main__":
    result = check_patent_activity("RAG hallucination reduction techniques")
    print(f"Total patents: {result['total_patents']}")
    print(f"Low activity: {result['is_low_activity']}")
    for p in result['sample_patents']:
        print("-", p['title'])