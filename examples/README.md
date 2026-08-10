# Examples

This folder contains minimal examples for integrating the repository's response library and semantic-routing resources.

## Contents

- `api_request_examples.jsonl` — example host-to-router request objects following protocol 6.3.
- `api_response_examples.jsonl` — corresponding examples of structured semantic-routing results.
- `python_router/` — a runnable Python reference implementation using the OpenAI Responses API and local response resolution.

The examples intentionally do not duplicate the routing prompt, schemas, or response library. The Python example reads those files from the repository's `prompts/` and `library/` folders.

## Model compatibility

The Python example can use either reasoning models such as GPT-5-family models or the non-reasoning snapshot `gpt-4.1-2025-04-14`. The same routing prompt and Structured Output schema are used in both cases; model-specific reasoning parameters are handled by the example code.

The JSONL files illustrate the protocol format rather than model-specific output wording. Diagnostic fields such as `confidence` may vary between API calls; `routeCode` is the field used to resolve the local response.
