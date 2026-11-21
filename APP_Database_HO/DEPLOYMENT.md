# Deployment Guide

## Requirements

- PostgreSQL 17
- pgvector
- Python 3.8+

---

## Start Database

```bash
brew services start postgresql@17
```

---

## Verify Database

```bash
psql steam
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start Backend

```bash
cd backend

uvicorn app:app --reload
```

---

## Swagger

Open

```text
http://127.0.0.1:8000/docs
```

---

## Stop Backend

Press

```text
CTRL + C
```