from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from test_scholar import search_scholar_combined
from synthesize import synthesize, extract_gap_phrases
from relevance import score_relevance
from patents import check_patent_activity

app = FastAPI(title="Scholar Research Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str
    check_patents: Optional[bool] = False

@app.get("/")
def root():
    return {"status": "Scholar Research Assistant is running"}

@app.post("/research")
def research(request: ResearchRequest):
    try:
        all_papers = search_scholar_combined(request.query)
    except Exception as e:
        print("SEARCH ERROR:", e)
        raise HTTPException(status_code=503,detail="Unable to reach the research search service right now. Please try again in a moment.")
    try:
        direct, adjacent = score_relevance(request.query, all_papers)
    except Exception as e:
        print("RELEVANCE ERROR:", e)
        raise HTTPException(status_code=503,detail="Unable to analyze the search results right now. Please try again.")

    def format_papers(papers):
        return [
            {
                "title": p.get("title"),
                "link": p.get("link"),
                "year_type": p.get("_source_type"),
                "cited_by": p.get("inline_links", {}).get("cited_by", {}).get("total")
            } for p in papers
        ]

    if not direct:
        return {
            "query": request.query,
            "papers_found": 0,
            "papers": [],
            "adjacent_papers": format_papers(adjacent),
            "brief": (
                f"No published research was found on \"{request.query}\" specifically — this exact topic doesn't appear to have been studied yet. "
                + (f"I found {len(adjacent)} related papers that touch on adjacent concepts, if that would help — see below."
                   if adjacent else "No closely related research was found either.")
            ),
            "patent_activity": None
        }

    try:
        brief = synthesize(request.query, direct)
    except Exception as e:
        print("SYNTHESIS ERROR:", e)
        raise HTTPException( status_code=503,detail="Found relevant papers but couldn't generate the summary right now. Please try again.")
    patent_activity = None
    if request.check_patents:
        try:
            gaps = extract_gap_phrases(brief)
            patent_results = []
            for gap in gaps:
                result = check_patent_activity(gap)
                patent_results.append(result)
            patent_results.sort(key=lambda r: r["total_patents"])
            patent_activity = patent_results
        except Exception as e:
            print("PATENT CHECK ERROR:", e)
            patent_activity = []

    return {
        "query": request.query,
        "papers_found": len(direct),
        "papers": format_papers(direct),
        "adjacent_papers": format_papers(adjacent),
        "brief": brief,
        "patent_activity": patent_activity
    }