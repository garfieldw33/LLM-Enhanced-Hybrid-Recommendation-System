from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from retrieval import (
    hybrid_search,
    hybrid_similar_db,
    resolve_seed_game,
    resolve_search
)

from llm import (
    explain_query_match,
    explain_item_similarity
)

app = FastAPI(
    title="CS5481 Hybrid Recommendation API",
    version="1.1.0"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class SearchRequest(BaseModel):
    query: str
    top_n: int = 10


class SimilarRequest(BaseModel):
    item_id: Optional[int] = None
    name: Optional[str] = None
    top_n: int = 10


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# AUTOCOMPLETE
# ============================================================

@app.get("/resolve")
def resolve(
    q: str,
    limit: int = 8
):

    return {
        "query": q,
        "matches": resolve_search(
            q,
            limit=limit
        )
    }


# ============================================================
# HYBRID QUERY SEARCH
# ============================================================

@app.post("/search")
def search(req: SearchRequest):

    results = hybrid_search(
        req.query,
        top_k=req.top_n
    )

    output = []

    for game, score in results:

        output.append(
            {
                "item_id": game["item_id"],
                "name": game["name"],
                "summary": game["summary"],
                "tags": game["tags"],
                "score": round(score, 6)
            }
        )

    return {
        "query": req.query,
        "top_n": req.top_n,
        "results": output
    }


# ============================================================
# HYBRID ITEM SIMILARITY
# ============================================================

@app.post("/similar")
def similar(req: SimilarRequest):

    seed = resolve_seed_game(
        item_id=req.item_id,
        name=req.name
    )

    if seed is None:

        if req.name:
            raise HTTPException(
                status_code=404,
                detail=(
                    f'no game matched "{req.name}"'
                )
            )

        raise HTTPException(
            status_code=404,
            detail="game not found"
        )

    results = hybrid_similar_db(
        seed["item_id"],
        top_k=req.top_n
    )

    output = []

    for game, score in results:

        output.append(
            {
                "item_id": game["item_id"],
                "name": game["name"],
                "summary": game["summary"],
                "tags": game["tags"],
                "score": round(score, 6)
            }
        )

    return {
        "item_id": seed["item_id"],
        "seed_name": seed["name"],
        "top_n": req.top_n,
        "results": output
    }


# ============================================================
# QUERY EXPLANATION
# ============================================================

@app.post("/explain/query")
def explain_query(req: SearchRequest):

    results = hybrid_search(
        req.query,
        top_k=1
    )

    top_game = results[0][0]

    explanation = explain_query_match(
        req.query,
        top_game
    )

    return {
        "query": req.query,
        "game": top_game["name"],
        "explanation": explanation
    }


# ============================================================
# ITEM EXPLANATION
# ============================================================

@app.post("/explain/similar")
def explain_similar(req: SimilarRequest):

    seed = resolve_seed_game(
        item_id=req.item_id,
        name=req.name
    )

    if seed is None:

        if req.name:
            raise HTTPException(
                status_code=404,
                detail=(
                    f'no game matched "{req.name}"'
                )
            )

        raise HTTPException(
            status_code=404,
            detail="game not found"
        )

    results = hybrid_similar_db(
        seed["item_id"],
        top_k=1
    )

    recommended_game = results[0][0]

    source_game = {
        "name": seed["name"],
        "summary": "",
        "tags": {}
    }

    explanation = explain_item_similarity(
        source_game,
        recommended_game
    )

    return {
        "item_id": seed["item_id"],
        "seed_name": seed["name"],
        "recommended_game": recommended_game["name"],
        "explanation": explanation
    }