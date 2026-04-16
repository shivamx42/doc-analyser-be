import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"Source {i+1}:\n{chunk['content']}"
        for i, chunk in enumerate(chunks)
    )
    
def generate_answer(question: str, chunks: list[dict]) -> str:
    API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL")

    if not API_KEY:
        raise RuntimeError("API Key is not set")

    if not GROQ_MODEL:
        raise RuntimeError("GROQ Model is not set")

    context = build_context(chunks)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You answer questions using only the provided document context. "
                    "If the answer is not in the context, say so clearly. "
                    "Do not make up facts. "
                    "Do not mention the source numbers in your answer, but use them to determine the answer based on the context."
                ),
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nContext:\n{context}",
            },
        ],
        "temperature": 0.2,
    }

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()