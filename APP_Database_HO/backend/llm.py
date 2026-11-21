import json
import dashscope

from config import (
    LLM_MODEL,
    DASHSCOPE_API_KEY
)


def explain_query_match(
    query,
    game
):

    SYSTEM_PROMPT = """
You are a game recommendation explanation assistant.

Explain why the retrieved game matches the user's query.

Rules:
- Maximum 60 words.
- Friendly and natural.
- Focus on gameplay, theme and mood.
"""

    USER_PROMPT = f"""
User query:
{query}

Retrieved game:
{game['name']}

Summary:
{game['summary']}

Tags:
{json.dumps(game['tags'], ensure_ascii=False)}
"""

    response = dashscope.MultiModalConversation.call(
        api_key=DASHSCOPE_API_KEY,
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": USER_PROMPT
                    }
                ]
            }
        ]
    )

    return (
        response.output
        .choices[0]
        .message.content[0]["text"]
    )


def explain_item_similarity(
    source_game,
    recommended_game
):

    SYSTEM_PROMPT = """
You are a game recommendation explanation assistant.

Explain why the recommended game is similar to the source game.

Rules:
- Maximum 80 words.
"""

    USER_PROMPT = f"""
Source Game:
{source_game['name']}

Source Summary:
{source_game['summary']}

Source Tags:
{json.dumps(source_game['tags'], ensure_ascii=False)}

Recommended Game:
{recommended_game['name']}

Recommended Summary:
{recommended_game['summary']}

Recommended Tags:
{json.dumps(recommended_game['tags'], ensure_ascii=False)}
"""

    response = dashscope.MultiModalConversation.call(
        api_key=DASHSCOPE_API_KEY,
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": USER_PROMPT
                    }
                ]
            }
        ]
    )

    return (
        response.output
        .choices[0]
        .message.content[0]["text"]
    )