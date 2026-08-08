import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from jsonschema import validate, ValidationError

load_dotenv()

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROMPT = (ROOT / "prompts" / "bc_intent_router_v1.md").read_text(encoding="utf-8")
ROUTE_SCHEMA = json.loads((ROOT / "prompts" / "route_result.schema.json").read_text(encoding="utf-8"))
REQUEST_SCHEMA = json.loads((ROOT / "prompts" / "route_request.schema.json").read_text(encoding="utf-8"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

app = FastAPI(title="TVCG BC Response Router", version="1.0.0")


def extract_output_text(response_json: dict[str, Any]) -> str:
    """Extract text from a raw Responses API response."""
    for item in response_json.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]
    raise ValueError("No output_text found in Responses API result")


@app.get("/health")
def health():
    return {"ok": True, "modelConfigured": bool(OPENAI_MODEL), "apiKeyConfigured": bool(OPENAI_API_KEY)}


@app.post("/api/bc/route")
async def route(payload: dict[str, Any]):
    try:
        validate(payload, REQUEST_SCHEMA)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid route request: {exc.message}") from exc

    if not OPENAI_API_KEY or not OPENAI_MODEL or OPENAI_MODEL.startswith("replace_"):
        raise HTTPException(status_code=500, detail="Configure OPENAI_API_KEY and OPENAI_MODEL in server/.env")

    request_body: dict[str, Any] = {
        "model": OPENAI_MODEL,
        "instructions": PROMPT,
        "input": json.dumps(payload, ensure_ascii=False),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "bc_route_result",
                "strict": True,
                "schema": ROUTE_SCHEMA,
            }
        },
        "store": False,
    }

    if OPENAI_REASONING_EFFORT:
        request_body["reasoning"] = {"effort": OPENAI_REASONING_EFFORT}

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{OPENAI_BASE_URL}/responses", headers=headers, json=request_body)

    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail={"openaiStatus": resp.status_code, "openaiBody": resp.text})

    try:
        raw = resp.json()
        route_result = json.loads(extract_output_text(raw))
        validate(route_result, ROUTE_SCHEMA)
    except (ValueError, json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=502, detail=f"Invalid structured model result: {exc}") from exc

    # Add transport fields required by the Unity-facing protocol.
    return {
        "protocolVersion": payload["protocolVersion"],
        "turnIndex": payload["turnIndex"],
        "rawAsrText": payload["rawAsrText"],
        **route_result,
    }
