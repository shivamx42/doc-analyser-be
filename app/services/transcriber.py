import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

def transcribe_audio(content: bytes, content_type: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_SPEECH_MODEL")

    if not api_key:
        raise ValueError("API key is not set")

    if not model:
        raise ValueError("Groq speech model is not set")

    files = {
        "file": ("audio.wav", content, content_type)
    }

    data = {
        "model": model,
        "response_format": "json",
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files=files,
            data=data,
            timeout=60,
        )

        response.raise_for_status()
        return response.json().get("text", "").strip()

    except requests.RequestException as e:
        error_message = str(e)

        if getattr(e, "response", None) is not None:
            try:
                error_data = e.response.json()
                error_message = (
                    error_data.get("error", {}).get("message")
                    or e.response.text
                )
            except Exception:
                error_message = e.response.text

        raise ValueError(f"Groq transcription failed: {error_message}")