# Response Library

`response_library.json` is the combined human-readable master file. The category-specific JSON files contain the same content split for easier application loading and review.

- `fixed_opening.json`: played locally before Turn 1; never selectable by the API.
- `broad_responses.json`: nine semantic groups, each with Preferred and Alternative texts.
- `specific_responses.json`: 48 single-information-point responses.
- `final_decision_responses.json`: two terminal responses.
- `conversation_control_responses.json`: six clarification/control responses.
- `route_catalog.json`: the 65 route codes the LLM is allowed to return.
- `action_codes.json`: action semantics for Unity.

The response text is the authoritative transcript. Do not let the LLM rewrite it at runtime. Audio paths are expected local paths only; original recordings are not distributed.
