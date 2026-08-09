# Router Prompt and Schemas

This folder contains the finalized **Compact v2** semantic-routing prompt for protocol `6.3` and its request/result schemas.

- `router_prompt_compact_v2.md` — authoritative runtime routing prompt.
- `route_request.schema.json` — host-to-router request contract.
- `route_result.schema.json` — strict structured-output contract returned by the LLM.

The router performs contextual ASR reconstruction before intent routing. It returns exactly one logical `routeCode`; it never generates the virtual character's spoken response, never selects Broad Preferred/Alternative variants, and never selects character actions.

For reproducible experiments, keep the prompt file unchanged during one data-collection run and record the prompt version, protocol version, model identifier, reasoning setting, and repository commit hash.
