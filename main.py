from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from test_scholar import search_scholar_combined
from synthesize import synthesize
from relevance import score_relevance

app = FastAPI(title="Scholar Research Assistant")

# Allows a frontend running on a different port/domain to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"status": "Scholar Research Assistant is running"}

@app.post("/research")
def research(request: ResearchRequest):
    all_papers = search_scholar_combined(request.query)
    direct, adjacent = score_relevance(request.query, all_papers)

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
        )
    }

    brief = synthesize(request.query, direct)
    return {
        "query": request.query,
        "papers_found": len(direct),
        "papers": format_papers(direct),
        "adjacent_papers": format_papers(adjacent),
        "brief": brief
    }