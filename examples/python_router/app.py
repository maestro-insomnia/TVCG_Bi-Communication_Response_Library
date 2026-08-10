#!/usr/bin/env python3
"""Reference implementation for the BC semantic-routing pipeline (protocol 6.3).

This example sends participant text and host-maintained conversation state to the
OpenAI Responses API. The model returns one structured semantic route. The
virtual-character response is then resolved locally from the predefined response
library; the model never generates the character's spoken reply.

The example supports both reasoning models (for example GPT-5-family models)
and non-reasoning models such as gpt-4.1-2025-04-14. Model-specific reasoning
parameters are added only when the selected model supports them.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
API_URL = "https://api.openai.com/v1/responses"

LIBRARY_PATH = REPO_ROOT / "library" / "response_library.json"
RESULT_SCHEMA_PATH = REPO_ROOT / "prompts" / "route_result.schema.json"
ROUTING_PROMPT_PATH = REPO_ROOT / "prompts" / "routing_prompt.md"

REQUIRED_BROAD_GROUPS = {
    "G01_SHIRT_OVERVIEW",
    "G02_SHIRT_LIKES",
    "G03_SHIRT_WARDROBE",
    "G04_SHIRT_REPLACEABILITY",
    "G05_HOODIE_OVERVIEW",
    "G06_HOODIE_LIKES",
    "G07_HOODIE_WARDROBE",
    "G08_HOODIE_REPLACEABILITY",
}

# Explicitly list model families for which the Responses API accepts the
# reasoning object. Unknown model names default to no reasoning parameter,
# which is the safer behavior for non-reasoning models.
REASONING_MODEL_PREFIXES = ("gpt-5", "o1", "o3", "o4")


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE settings without an external dependency."""
    if not path.exists():
        return

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def supports_reasoning(model: str) -> bool:
    """Return True only for model families known here to accept reasoning."""
    name = model.strip().lower()
    return name.startswith(REASONING_MODEL_PREFIXES)


load_dotenv(BASE_DIR / ".env")

LIBRARY = load_json(LIBRARY_PATH)
RESULT_SCHEMA = load_json(RESULT_SCHEMA_PATH)
ROUTING_PROMPT = ROUTING_PROMPT_PATH.read_text(encoding="utf-8")

BROAD_GROUPS = LIBRARY["broadGroups"]
RESPONSES = LIBRARY["responses"]
OPENING = LIBRARY["fixedOpening"]
VALID_ROUTES = set(RESULT_SCHEMA["properties"]["routeCode"]["enum"])


class ConversationState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.started = False
        self.ended = False
        self.active_item = "unknown"
        self.turn_index = 0
        self.played_broad_groups: set[str] = set()
        self.broad_counts: defaultdict[str, int] = defaultdict(int)
        self.recent_turns: list[dict] = []

    @property
    def final_recommendation_enabled(self) -> bool:
        return REQUIRED_BROAD_GROUPS.issubset(self.played_broad_groups)

    @property
    def missing_required_broad_groups(self) -> list[str]:
        return sorted(REQUIRED_BROAD_GROUPS - self.played_broad_groups)

    def make_route_request(self, participant_text: str, input_mode: str) -> dict:
        return {
            "protocolVersion": "6.3",
            "turnIndex": self.turn_index + 1,
            "finalRecommendationEnabled": self.final_recommendation_enabled,
            "inputMode": input_mode,
            "activeItem": self.active_item,
            "rawInputText": participant_text,
            "playedBroadGroups": sorted(self.played_broad_groups),
            "recentTurns": self.recent_turns[-4:],
        }

    def resolve_response(self, route_code: str) -> tuple[str, dict]:
        """Resolve the model's logical route to one local prerecorded response."""
        if route_code in BROAD_GROUPS:
            self.broad_counts[route_code] += 1
            group = BROAD_GROUPS[route_code]
            odd_selection = self.broad_counts[route_code] % 2 == 1
            response_code = group["preferred"] if odd_selection else group["alternative"]
            self.played_broad_groups.add(route_code)
            return response_code, RESPONSES[response_code]

        if route_code not in RESPONSES:
            raise KeyError(f"No local response is mapped to route {route_code!r}.")

        return route_code, RESPONSES[route_code]

    def update_after_turn(
        self,
        participant_text: str,
        result: dict,
        response: dict,
    ) -> None:
        self.turn_index += 1
        route_code = result["routeCode"]

        if result["routeCategory"] != "control":
            if route_code in BROAD_GROUPS:
                self.active_item = BROAD_GROUPS[route_code]["target"]
            elif route_code.startswith("BC_SPC"):
                number = int(route_code[6:8])
                if number <= 21:
                    self.active_item = "first_top"
                elif number <= 38:
                    self.active_item = "second_top"
                else:
                    self.active_item = "both"
            elif route_code.startswith("BC_DEC"):
                self.active_item = "both"

        self.recent_turns.append(
            {
                "turnIndex": self.turn_index,
                "participantText": participant_text,
                "correctedParticipantText": result["correctedInputText"],
                "utteranceType": result["utteranceType"],
                "routeCode": route_code,
            }
        )
        self.recent_turns = self.recent_turns[-4:]

        if response.get("endsConversation"):
            self.ended = True


def extract_output_text(api_response: dict) -> str:
    """Extract the Structured Output JSON text from a Responses API response."""
    for item in api_response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                return content["text"]

    raise RuntimeError("Responses API returned no output_text item.")


def build_api_payload(
    request_obj: dict,
    *,
    model: str,
    reasoning_effort: str,
) -> dict:
    """Build a Responses API payload compatible with GPT-4.1 and GPT-5 families."""
    api_schema = {
        key: value
        for key, value in RESULT_SCHEMA.items()
        if key not in {"$schema", "title"}
    }

    payload = {
        "model": model,
        "instructions": ROUTING_PROMPT,
        "input": json.dumps(request_obj, ensure_ascii=False),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "bc_route_result_v63",
                "strict": True,
                "schema": api_schema,
            }
        },
        "max_output_tokens": 450,
        "store": False,
    }

    # gpt-4.1-2025-04-14 is a non-reasoning model, so this field must be
    # omitted. GPT-5-family models can receive the configured reasoning effort.
    if supports_reasoning(model) and reasoning_effort:
        payload["reasoning"] = {"effort": reasoning_effort}

    return payload


def call_router(
    request_obj: dict,
    *,
    api_key: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
) -> tuple[dict, dict]:
    payload = build_api_payload(
        request_obj,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            api_response = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Network error calling OpenAI API: {error}") from error

    if api_response.get("status") not in (None, "completed"):
        raise RuntimeError(
            "OpenAI response did not complete: "
            f"status={api_response.get('status')}, "
            f"details={api_response.get('incomplete_details')}"
        )

    result = json.loads(extract_output_text(api_response))
    if result.get("routeCode") not in VALID_ROUTES:
        raise RuntimeError(f"Model returned invalid routeCode: {result.get('routeCode')!r}")

    return result, api_response


def print_debug(
    state: ConversationState,
    result: dict,
    response_code: str,
    api_response: dict,
) -> None:
    print("[debug] correctedInputText:", result["correctedInputText"])
    print("[debug] correctionStatus:", result["correctionStatus"])
    print("[debug] punctuationStatus:", result["punctuationStatus"])
    print("[debug] utteranceType:", result["utteranceType"])
    print("[debug] informationRequestCount:", result["informationRequestCount"])
    print("[debug] routingBasisText:", result["routingBasisText"])
    print("[debug] semanticTarget:", result["semanticTarget"])
    print("[debug] intentClass:", result["intentClass"])
    print("[debug] routeCode:", result["routeCode"])
    print("[debug] responseCode:", response_code)
    print("[debug] confidence:", result["confidence"])
    print(
        "[debug] finalRecommendationEnabled(after turn):",
        state.final_recommendation_enabled,
    )
    print("[debug] usage:", json.dumps(api_response.get("usage", {}), ensure_ascii=False))


def print_help() -> None:
    print("Commands:")
    print("  start   start/reset the conversation and play the fixed opening")
    print("  /state  show locally maintained conversation state")
    print("  /debug  toggle routing diagnostics")
    print("  /reset  reset and immediately play the fixed opening")
    print("  /help   show commands")
    print("  /quit   exit")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BC semantic-routing reference implementation (protocol 6.3)"
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        help="Responses API model name, e.g. gpt-5.6-luna or gpt-4.1-2025-04-14.",
    )
    parser.add_argument(
        "--reasoning",
        default=os.getenv("OPENAI_REASONING_EFFORT", "low"),
        choices=["none", "minimal", "low", "medium", "high", "xhigh"],
        help="Applied only when the selected model supports reasoning.",
    )
    parser.add_argument(
        "--input-mode",
        default=os.getenv("INPUT_MODE", "asr"),
        choices=["typed", "asr"],
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("OPENAI_TIMEOUT_SECONDS", "60")),
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    debug = os.getenv("SHOW_ROUTING_DEBUG", "1") == "1"
    state = ConversationState()

    reasoning_mode = args.reasoning if supports_reasoning(args.model) else "omitted"
    print(
        "BC Semantic Router v6.3 | "
        f"model={args.model} | inputMode={args.input_mode} | reasoning={reasoning_mode}"
    )
    print("Type 'start' to begin. Type /help for commands.")

    while True:
        try:
            participant_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if not participant_text:
            continue

        command = participant_text.lower()
        if command in {"/quit", "quit", "exit"}:
            print("Bye.")
            return 0
        if command == "/help":
            print_help()
            continue
        if command == "/debug":
            debug = not debug
            print(f"Debug {'ON' if debug else 'OFF'}.")
            continue
        if command == "/state":
            print(
                json.dumps(
                    {
                        "activeItem": state.active_item,
                        "playedBroadGroups": sorted(state.played_broad_groups),
                        "missingRequiredBroadGroups": state.missing_required_broad_groups,
                        "finalRecommendationEnabled": state.final_recommendation_enabled,
                        "broadCounts": dict(state.broad_counts),
                        "turnIndex": state.turn_index,
                        "ended": state.ended,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            continue
        if command in {"start", "/reset"}:
            state.reset()
            state.started = True
            print("Character:", OPENING)
            continue

        if not state.started or state.ended:
            print("Type 'start' to begin a new conversation.")
            continue

        if not api_key:
            print("[error] OPENAI_API_KEY is not set. Add your key to .env and restart.")
            continue

        route_request = state.make_route_request(participant_text, args.input_mode)

        try:
            result, api_response = call_router(
                route_request,
                api_key=api_key,
                model=args.model,
                reasoning_effort=args.reasoning,
                timeout=args.timeout,
            )
            response_code, response = state.resolve_response(result["routeCode"])
            state.update_after_turn(participant_text, result, response)

            if debug:
                print_debug(state, result, response_code, api_response)

            print("Character:", response["text"])
            if state.ended:
                print("[conversation ended] Type 'start' to begin a new conversation.")
        except Exception as error:
            print("[error]", error)


if __name__ == "__main__":
    raise SystemExit(main())
