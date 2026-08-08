# Local Router Service

This FastAPI example keeps the OpenAI API key outside the Unity client. It validates the Unity request, calls the OpenAI Responses API with the router prompt and strict JSON Schema, validates the model result, and returns the route to Unity.

## Setup

```bash
python -m venv .venv
# activate the environment
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then:

```bash
uvicorn app:app --host 127.0.0.1 --port 5050
```

Do not commit `.env` or an API key. For experimental reproducibility, record the exact model identifier, prompt version, schema version, and repository commit hash used for each data collection session.
