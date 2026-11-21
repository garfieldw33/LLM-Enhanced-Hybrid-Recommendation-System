# API Contract

## Base URL

```text
http://127.0.0.1:8000
```

---

# GET /health

Health check endpoint.

Response

```json
{
  "status": "ok"
}
```

---

# POST /search

Description

Hybrid free-text retrieval.

Request

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10
}
```

Response

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10,
  "results": [
    {
      "item_id": 123,
      "name": "...",
      "summary": "...",
      "tags": {},
      "score": 0.031
    }
  ]
}
```

---

# POST /similar

Description

Hybrid item similarity retrieval.

Supports either:

```json
{
  "item_id": 227300,
  "top_n": 10
}
```

or

```json
{
  "name": "Euro Truck Simulator 2",
  "top_n": 10
}
```

Response

```json
{
  "item_id": 227300,
  "seed_name": "Euro Truck Simulator 2",
  "top_n": 10,
  "results": [
    {
      "item_id": 873840,
      "name": "Truck & Logistics Simulator",
      "summary": "...",
      "tags": {},
      "score": 0.031
    }
  ]
}
```

---

# GET /resolve

Description

Game name autocomplete and resolution.

Request

```text
/resolve?q=stardew&limit=8
```

Response

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

# POST /explain/query

Description

Generate explanation for the top hybrid retrieval result from a free-text query.

Request

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10
}
```

Response

```json
{
  "query": "...",
  "game": "...",
  "explanation": "..."
}
```

---

# POST /explain/similar

Description

Generate explanation for the top hybrid recommendation.

Supports either:

```json
{
  "item_id": 227300,
  "top_n": 10
}
```

or

```json
{
  "name": "Euro Truck Simulator 2",
  "top_n": 10
}
```

Response

```json
{
  "item_id": 227300,
  "seed_name": "Euro Truck Simulator 2",
  "recommended_game": "Truck & Logistics Simulator",
  "explanation": "..."
}
```

---

# Name Resolution Logic

When `name` is supplied:

1. Exact case-insensitive title match.
2. If no exact match, fallback to substring match.
3. If still no match:

```json
{
  "detail": "no game matched \"<name>\""
}
```

with:

```http
404 Not Found
```

---

# Notes

- `/search` performs hybrid retrieval using PostgreSQL FTS + vector retrieval + RRF.
- `/similar` performs hybrid item similarity using keyword similarity + vector similarity + RRF.
- `/explain/query` and `/explain/similar` currently execute retrieval again before generating explanations.
- `item_id` lookup remains fully backward compatible.