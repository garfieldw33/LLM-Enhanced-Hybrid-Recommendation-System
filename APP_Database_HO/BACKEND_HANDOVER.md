# Backend Handover

## What This Project Is

This backend provides:

1. Free-text hybrid game search
2. Similar-game recommendation
3. LLM-generated explanations

The backend depends on:

```text
PostgreSQL
+
pgvector
+
DashScope
+
FastAPI
```



---
# Before everything else: DashScope Setup

The backend requires DashScope for:

1. Query embeddings
2. LLM explanations

WARNING

The API key is not included in this handover package.

Each developer **must** create their own DashScope account and configure their own API key locally.

---

## Step 1. Create an Alibaba Cloud Account

Register:

https://www.alibabacloud.com/

---

## Step 2. Open DashScope

Visit:

https://dashscope.console.aliyun.com/

---

## Step 3. Activate Model Service

Open:

```text
Model Studio
```

Enable:

```text
text-embedding-v4
```

and

```text
Qwen
```

models.

---

## Step 4. Obtain API Key

Navigate:

```text
DashScope
→ API Keys
```

Create a new key.

Example:

```text
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 5. Set Environment Variable

macOS / Linux

```bash
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

Verify:

```bash
echo $DASHSCOPE_API_KEY
```

Expected:

```text
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 6. Test Connectivity

Start backend:

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

```text
POST /search
```

with:

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 3
}
```

A successful response indicates:

- PostgreSQL works
- DashScope Embedding works
- Hybrid Retrieval works

---

## Notes

Current Models:

```text
Embedding:
text-embedding-v4

LLM:
qwen3.8-27b
```

Configured in:

```text
backend/config.py
```

To switch models:

```python
EMBEDDING_MODEL = "..."
LLM_MODEL = "..."
```
---

# Quick Start (5 Minutes)
---

## Step 1. Install PostgreSQL

Recommended Version:

```text
PostgreSQL 17
```

Verify:

```bash
psql --version
```

---

## Step 2. Restore Database

Create database:

```bash
createdb steam
```

Restore backup:

```bash
psql steam < steam_complete_backup.sql
```

Verify:

```bash
psql steam
```

```sql
SELECT COUNT(*) FROM items;
```

Expected*

```*ext
25899
```

Verify*vectors:

```sql
SELECT COUNT(*) FROM item_embeddings;
```

Expected:

```text
25899
```

---

## Step 3. Install Python Dependencies

Open terminal in:

```text
backend/
```

Install:

```bash
pip install -r requirements.txt
```

---

## Step 4. Configure DashScope

Set API key (See dashscope instructions above):

```bash
export DASHSCOPE_API_KEY=YOUR_KEY
```

Verify:

```bash
echo $DASHSCOPE_API_KEY
```

---

## Step 5. Start Backend

From:

```text
backend/
```

Run:

```bash
uvicorn app:app --reload
```

Expected:

```text
Application startup complete
```

---

## Step 6. Open Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

You should see:

```text
GET  /health

POST /search

POST /similar

POST /explain/query

POST /explain/similar
```

---

# API Usage

## Search Games

Endpoint:

```text
POST /search
```

Example:

```json
{
  "query": "a relaxing video game with beautiful art but no combat",
  "top_n": 10
}
```

---

## Find Similar Games

Endpoint:

```text
POST /similar
```

Example:

```json
{
  "item_id": 227300,
  "top_n": 10
}
```

---

## Generate Query Explanation

Endpoint:

```text
POST /explain/query
```

---

## Generate Similarity Explanation

Endpoint:

```text
POST /explain/similar
```

---

# System Architecture

## Database Layer

Main Tables:

```text
items
item_annotations
item_embeddings
```

---

## Retrieval Layer

### Keyword Retrieval

Uses:

```python
keyword_search()
```

Data Sources:

```text
description_clean
summary
LLM tags
```

---

### Vector Retrieval

Uses:

```python
vector_search()
```

Model:

```text
text-embedding-v4
```

Dimension:

```text
256
```

---

### Hybrid Retrieval

Uses:

```python
hybrid_search()
hybrid_similar_db()
```

Fusion:

```text
Reciprocal Rank Fusion (RRF)
```

Formula:

```text
1 / (60 + rank)
```

---

# Known Limitations

## Explanation Endpoints

Current behavior:

```text
/explain/query
```

and

```text
/explain/similar
```

perform retrieval again before generating explanations.

This is acceptable for the prototype but can be optimized later.

---

# Troubleshooting

## Database Not Found

Check:

```bash
psql -l
```

Verify:

```text
steam
```

exists.

---

## Embedding Errors

Verify:

```bash
echo $DASHSCOPE_API_KEY
```

is set.

---

## Backend Fails To Start

Run:

```bash
python -m py_compile config.py
python -m py_compile retrieval.py
python -m py_compile llm.py
```

All commands should complete without errors.