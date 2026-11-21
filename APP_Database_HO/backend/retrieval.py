import psycopg2
import pandas as pd

from collections import defaultdict
from dashscope import TextEmbedding

from config import (
    DB_NAME,
    DB_USER,
    DB_HOST,
    EMBEDDING_MODEL,
    EMBEDDING_DIM,
    RRF_K,
    KEYWORD_CANDIDATES,
    VECTOR_CANDIDATES,
    DEFAULT_TOP_N
)

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    host=DB_HOST
)



# paste:

# ============================================================
# GAME NAME RESOLUTION
# ============================================================

def resolve_game_name(
    name
):

    exact_sql = """
    SELECT
        item_id,
        name
    FROM items
    WHERE lower(name) = lower(%s)
    LIMIT 1
    """

    exact = pd.read_sql(
        exact_sql,
        conn,
        params=(name,)
    )

    if len(exact) > 0:

        return {
            "item_id": int(exact.iloc[0]["item_id"]),
            "name": exact.iloc[0]["name"]
        }

    fuzzy_sql = """
    SELECT
        item_id,
        name
    FROM items
    WHERE lower(name)
          LIKE lower(%s)
    ORDER BY name
    LIMIT 1
    """

    fuzzy = pd.read_sql(
        fuzzy_sql,
        conn,
        params=(f"%{name}%",)
    )

    if len(fuzzy) > 0:

        return {
            "item_id": int(fuzzy.iloc[0]["item_id"]),
            "name": fuzzy.iloc[0]["name"]
        }

    return None


# ============================================================
# AUTOCOMPLETE
# ============================================================

def resolve_search(
    query,
    limit=8
):

    sql = """
    SELECT
        item_id,
        name
    FROM items
    WHERE lower(name)
          LIKE lower(%s)
    ORDER BY name
    LIMIT %s
    """

    df = pd.read_sql(
        sql,
        conn,
        params=(
            f"%{query}%",
            limit
        )
    )

    results = []

    for _, row in df.iterrows():

        results.append(
            {
                "item_id": int(row["item_id"]),
                "name": row["name"]
            }
        )

    return results

def resolve_seed_game(
    item_id=None,
    name=None
):

    if item_id is not None:

        sql = """
        SELECT
            item_id,
            name
        FROM items
        WHERE item_id = %s
        """

        df = pd.read_sql(
            sql,
            conn,
            params=(item_id,)
        )

        if len(df) == 0:
            return None

        return {
            "item_id": int(df.iloc[0]["item_id"]),
            "name": df.iloc[0]["name"]
        }

    if name is not None:

        exact_sql = """
        SELECT
            item_id,
            name
        FROM items
        WHERE lower(name)=lower(%s)
        LIMIT 1
        """

        exact = pd.read_sql(
            exact_sql,
            conn,
            params=(name,)
        )

        if len(exact) > 0:

            return {
                "item_id": int(exact.iloc[0]["item_id"]),
                "name": exact.iloc[0]["name"]
            }

        fuzzy_sql = """
        SELECT
            item_id,
            name
        FROM items
        WHERE lower(name)
              LIKE lower(%s)
        ORDER BY name
        LIMIT 1
        """

        fuzzy = pd.read_sql(
            fuzzy_sql,
            conn,
            params=(f"%{name}%",)
        )

        if len(fuzzy) > 0:

            return {
                "item_id": int(fuzzy.iloc[0]["item_id"]),
                "name": fuzzy.iloc[0]["name"]
            }

    return None

# keyword_search()
# ============================================================
# KEYWORD SEARCH
# ============================================================

def keyword_search(
    query,
    top_k=KEYWORD_CANDIDATES
):

    sql = """
    SELECT
        i.item_id,
        i.name,
        a.summary,
        a.tags,

        ts_rank_cd(
            to_tsvector(
                'english',
                coalesce(i.description_clean,'')
                || ' ' ||
                coalesce(a.summary,'')
                || ' ' ||
                coalesce(a.tags::text,'')
            ),
            websearch_to_tsquery(
                'english',
                %s
            )
        ) AS score

    FROM items i
    JOIN item_annotations a
        USING(item_id)

    ORDER BY score DESC

    LIMIT %s
    """

    df = pd.read_sql(
        sql,
        conn,
        params=(query, top_k)
    )

    results = []

    for _, row in df.iterrows():

        results.append(
            (
                {
                    "item_id": row["item_id"],
                    "name": row["name"],
                    "summary": row["summary"],
                    "tags": row["tags"]
                },
                float(row["score"])
            )
        )

    return results



# vector_search()
# ============================================================
# QUERY -> VECTOR SEARCH
# ============================================================

def vector_search(
    query,
    top_k=VECTOR_CANDIDATES
):

    response = TextEmbedding.call(
        model=EMBEDDING_MODEL,
        input=query,
        dimension=EMBEDDING_DIM
    )

    query_vector = (
        response.output["embeddings"][0]
        ["embedding"]
    )

    vector_str = (
        "["
        + ",".join(
            map(str, query_vector)
        )
        + "]"
    )

    sql = """
    SELECT
        i.item_id,
        i.name,
        a.summary,
        a.tags,

        ROUND(
            (
                1 -
                (
                    e.embedding
                    <=>
                    %s::vector
                )
            )::numeric,
            4
        ) AS score

    FROM item_embeddings e

    JOIN items i
        ON i.item_id = e.item_id

    JOIN item_annotations a
        ON a.item_id = e.item_id

    ORDER BY
        e.embedding
        <=>
        %s::vector

    LIMIT %s
    """

    df = pd.read_sql(
        sql,
        conn,
        params=(
            vector_str,
            vector_str,
            top_k
        )
    )

    results = []

    for _, row in df.iterrows():

        results.append(
            (
                {
                    "item_id": row["item_id"],
                    "name": row["name"],
                    "summary": row["summary"],
                    "tags": row["tags"]
                },
                float(row["score"])
            )
        )

    return results


# recommend_similar_db()
# ============================================================
# ITEM -> VECTOR SEARCH
# ============================================================

def recommend_similar_db(
    item_id,
    top_k=VECTOR_CANDIDATES
):

    sql = """
    SELECT
        i.item_id,
        i.name,
        a.summary,
        a.tags,

        ROUND(
            (
                1 -
                (
                    e.embedding
                    <=>
                    s.embedding
                )
            )::numeric,
            4
        ) AS score

    FROM item_embeddings s

    JOIN item_embeddings e
        ON e.item_id <> s.item_id

    JOIN items i
        ON i.item_id = e.item_id

    JOIN item_annotations a
        ON a.item_id = e.item_id

    WHERE s.item_id = %s

    ORDER BY
        e.embedding
        <=>
        s.embedding

    LIMIT %s
    """

    df = pd.read_sql(
        sql,
        conn,
        params=(
            item_id,
            top_k
        )
    )

    results = []

    for _, row in df.iterrows():

        results.append(
            (
                {
                    "item_id": row["item_id"],
                    "name": row["name"],
                    "summary": row["summary"],
                    "tags": row["tags"]
                },
                float(row["score"])
            )
        )

    return results


# hybrid_search()
def hybrid_search(
    query,
    top_k=DEFAULT_TOP_N,
    candidate_k=50
):
    keyword_results = keyword_search(
        query,
        top_k=candidate_k
    )

    vector_results = vector_search(
        query,
        top_k=candidate_k
    )

    scores = defaultdict(float)

    for rank, (game, _) in enumerate(
        keyword_results,
        start=1
    ):
        scores[game["item_id"]] += (
            1 / (RRF_K + rank)
        )

    for rank, (game, _) in enumerate(
        vector_results,
        start=1
    ):
        scores[game["item_id"]] += (
            1 / (RRF_K + rank)
        )

    game_lookup = {}

    for game, _ in keyword_results:
        game_lookup[game["item_id"]] = game

    for game, _ in vector_results:
        game_lookup[game["item_id"]] = game

    final_results = []

    for gid, score in sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]:

        final_results.append(
            (
                game_lookup[gid],
                score
            )
        )

    return final_results

# hybrid_similar_db(

# ============================================================
# HYBRID ITEM SEARCH
# ============================================================

def hybrid_similar_db(
    item_id,
    top_k=DEFAULT_TOP_N,
    candidate_k=50
):

    target = pd.read_sql(
        """
        SELECT
            i.name,
            a.summary,
            a.tags
        FROM items i
        JOIN item_annotations a
            USING(item_id)
        WHERE i.item_id = %s
        """,
        conn,
        params=(item_id,)
    ).iloc[0]

    query_text = " ".join(
        [
            target["name"],
            target["summary"],
            str(target["tags"])
        ]
    )

    keyword_results = keyword_search(
        query_text,
        top_k=candidate_k
    )

    vector_results = recommend_similar_db(
        item_id,
        top_k=candidate_k
    )

    scores = defaultdict(float)

    for rank, (game, _) in enumerate(
        keyword_results,
        start=1
    ):
        scores[game["item_id"]] += (
            1 / (RRF_K + rank)
        )

    for rank, (game, _) in enumerate(
        vector_results,
        start=1
    ):
        scores[game["item_id"]] += (
            1 / (RRF_K + rank)
        )

    game_lookup = {}

    for game, _ in keyword_results:
        game_lookup[game["item_id"]] = game

    for game, _ in vector_results:
        game_lookup[game["item_id"]] = game

    if item_id in scores:
        del scores[item_id]

    final_results = []

    for gid, score in sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]:

        final_results.append(
            (
                game_lookup[gid],
                score
            )
        )

    return final_results