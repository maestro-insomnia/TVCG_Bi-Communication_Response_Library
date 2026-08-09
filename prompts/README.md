# Routing Prompt and Schemas

- `routing_prompt.md` — semantic-routing prompt used at runtime.
- `route_request.schema.json` — request contract sent by the host application.
- `route_result.schema.json` — structured-output contract returned by the LLM.

The prompt returns exactly one logical `routeCode`; prerecorded response text and character actions are resolved locally by the host application.
