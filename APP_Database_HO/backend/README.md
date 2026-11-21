# CS5481 Data Engineering Project
## LLM-Enhanced Hybrid Recommendation System for Steam Games

### Overview

This project implements an LLM-enhanced hybrid recommendation system for Steam games. The system combines:

- Keyword-based retrieval
- Vector similarity retrieval
- Reciprocal Rank Fusion (RRF)
- LLM-generated explanations

The final system supports:

1. Free-text game discovery
2. Item-to-item recommendation
3. Hybrid ranking using keyword and vector retrieval
4. Natural-language explanations for recommendations
---
# History:
1.1.0: id/game name retrival

---

# System Architecture

```text
Steam Dataset
      │
      ▼
PostgreSQL
├── items
├── item_annotations
├── item_tags
├── item_llm_tags
└── item_embeddings

      │
      ├──────────────┐
      ▼              ▼

Keyword Search   Vector Search
(PostgreSQL)     (pgvector)

      │              │
      └──────┬───────┘
             ▼

   Reciprocal Rank Fusion
            (RRF)

             ▼

    Hybrid Recommendation

             ▼

       Qwen Explanation
```

---

# Dataset

Domain:

```text
Steam Games
```

Dataset Size:

```text
25,899 games
```

Stored Data:

- Base game metadata
- Cleaned descriptions
- LLM-generated summaries
- LLM-generated tags
- Vector embeddings

---

# Database

Database System:

```text
PostgreSQL 17
```

Vector Extension:

```text
pgvector
```

Database Name:

```text
steam
```

Major Tables:

## items

Stores core game information.

Examples:

- item_id
- name
- description_clean
- genres
- native_tags

---

## item_annotations

Stores LLM enrichment.

Fields:

- summary
- tags

Example tag dimensions:

- genre
- theme
- mechanics
- art_style
- mood
- audience
- content_warnings

---

## item_embeddings

Stores vector embeddings.

Fields:

- item_id
- model
- dim
- embedding

Embedding Model:

```text
text-embedding-v4
```

Dimension:

```text
256
```

Record Count:

```text
25,899
```

---

# Retrieval Methods

## 1. Keyword Retrieval

Input:

```text
Free-text query
```

Examples:

```text
truck driving game

A Game About Chopping Trees

relaxing farming game
```

Implementation:

```text
PostgreSQL Full Text Search
```

Search Corpus:

```text
description_clean
+
summary
+
LLM tags
```

Output:

```text
Top-N ranked games
```

```text
Note:

The backend uses PostgreSQL Full Text Search (FTS) rather than a
Python BM25 implementation.

This avoids loading the entire corpus into application memory and
supports scalable database-native retrieval.

```

---

## 2. Vector Retrieval

Input:

```text
Free-text query
```

Process:

```text
Query
    ↓
text-embedding-v4
    ↓
256-dimensional vector
    ↓
pgvector similarity search
```

Output:

```text
Top-N semantically similar games
```

---

## 3. Item Similarity Retrieval

Input:

```text
Game ID
```

Example:

```text
227300
(Euro Truck Simulator 2)
```

Process:

```text
Stored game embedding
        ↓
Cosine similarity
        ↓
Nearest neighbors
```

Output:

```text
Top-N similar games
```

---

# Hybrid Retrieval

Hybrid retrieval combines:

```text
Keyword Search
+
Vector Search
```

into a single ranking.

Two hybrid workflows are implemented.

---

## Hybrid Query Retrieval

Input:

```text
Free-text query
```

Examples:

```text
a relaxing video game with beautiful art but no combat
```

Retrieval Pipeline:

```text
Query
      ↓

Keyword Ranking

      +

Vector Ranking

      ↓

RRF Fusion

      ↓

Final Ranking
```

Output:

```text
Top-N recommended games
```

---

## Hybrid Item Similarity

Input:

```text
Game ID
```

Examples:

```text
227300
(Euro Truck Simulator 2)
```

Retrieval Pipeline:

```text
Keyword Similarity

      +

Vector Similarity

      ↓

RRF Fusion

      ↓

Final Ranking
```

Output:

```text
Top-N similar games
```

---

# Reciprocal Rank Fusion (RRF)

The hybrid ranking strategy uses:

```text
Reciprocal Rank Fusion
```

Formula:

```text
score = 1 / (k + rank)
```

where:

```text
k = 60
```

Final Score:

```text
Keyword RRF Score
+
Vector RRF Score
```

Advantages:

- Robust ranking
- No score normalization required
- Works across different retrieval methods

---

# LLM Explanations

Explanation Model:

```text
qwen3.8-27b
```

Provider:

```text
DashScope
```

Two explanation modes are implemented.

---

## Query Explanation

Input:

```text
Query
+
Top Retrieved Game
```

Output:

```text
Short explanation describing
why the game matches the query.
```

---

## Similarity Explanation

Input:

```text
Source Game
+
Recommended Game
```

Output:

```text
Short explanation describing
why the games are similar.
```

---

# Backend Service

Framework:

```text
FastAPI
```

Documentation:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## GET /health

Health check endpoint.

Response:

```json
{
  "status": "ok"
}
```

---

## POST /search

Hybrid free-text retrieval.

Request:

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10
}
```

Response:

```json
{
  "query": "...",
  "top_n": 10,
  "results": [...]
}
```

---

## POST /similar

Hybrid item similarity retrieval.

Request:

```json
{
  "item_id": 227300,
  "top_n": 10
}
```

Response:

```json
{
  "item_id": 227300,
  "top_n": 10,
  "results": [...]
}
```

---

## POST /explain/query

Query explanation endpoint.

Request:

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10
}
```

Response:

```json
{
  "query": "...",
  "game": "...",
  "explanation": "..."
}
```

---

## POST /explain/similar

Item similarity explanation endpoint.

Request:

```json
{
  "item_id": 227300,
  "top_n": 10
}
```

Response:

```json
{
  "item_id": 227300,
  "recommended_game": "...",
  "explanation": "..."
}
```
---
## GET /resolve

Autocomplete endpoint.

Request:

```text
/resolve?q=stardew&limit=8
```
response:

```json
{
  "query": "stardew",
  "matches": [
    {
      "item_id": 413150,
      "name": "Stardew Valley"
    }
  ]
}

```
---

# Project Structure

```text
backend/
├── app.py
├── config.py
├── retrieval.py
├── llm.py
├── requirements.txt
└── README.md
```

---

# Running the Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Known Limitations

1. Explanation endpoints currently perform retrieval again before generating explanations.
2. PostgreSQL is configured for local development only.
3. Authentication is not implemented.
4. Rate limiting is not implemented.
5. Responses are optimized for research and demonstration rather than production deployment.

---

# Technologies

- Python
- FastAPI
- PostgreSQL 17
- pgvector
- DashScope
- text-embedding-v4
- qwen3.8-27b
- Pandas
- Swagger/OpenAPI
- Reciprocal Rank Fusion (RRF)