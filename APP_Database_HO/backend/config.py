# ============================================================
# CONFIG
# ============================================================

import os

# ----------------------------
# PostgreSQL
# ----------------------------

DB_NAME = "steam"
DB_USER = "kesiyun"
DB_HOST = "localhost"

# ----------------------------
# Embeddings
# ----------------------------

EMBEDDING_MODEL = "text-embedding-v4"
EMBEDDING_DIM = 256

# ----------------------------
# LLM
# ----------------------------

#LLM_MODEL = "qwen3.8-27b"
LLM_MODEL = "qwen4-max"


# ----------------------------
# Hybrid Retrieval
# ----------------------------

RRF_K = 60

KEYWORD_CANDIDATES = 50
VECTOR_CANDIDATES = 50

# ----------------------------
# Default Demo Values
# ----------------------------

DEFAULT_TOP_N = 10

DEFAULT_GAME_ID = 227300
#DEFAULT_GAME_ID = 413150

DEFAULT_QUERY = (
    "a relaxing video game "
    "with beautiful art "
    "but no combat"
)

# ----------------------------
# DashScope
# ----------------------------

DASHSCOPE_API_KEY = os.getenv(
    "DASHSCOPE_API_KEY"
)