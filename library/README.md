# Response Library

This folder contains the response library in two forms:

- **JSON files** for programmatic loading and routing;
- **`text/` files** for quick viewing, copying, and reuse of the response wording.

## Machine-readable files

- `response_library.json` — combined library.
- `route_catalog.json` — logical route codes available to the router.
- `fixed_opening.json` — fixed opening played before Turn 1; not router-selectable.
- `broad_responses.json` — nine Broad groups with Preferred/Alternative variants.
- `specific_responses.json` — 48 Specific responses.
- `final_decision_responses.json` — two Final-decision responses.
- `conversation_control_responses.json` — seven Conversation-control responses.
- `action_codes.json` — character-action code definitions.
- `response_library.schema.json` — schema for the combined library.

## Copy-friendly text files

`text/` contains the same response wording without JSON syntax:

- `all_response_texts.txt`
- `fixed_opening.txt`
- `broad_responses.txt`
- `specific_responses.txt`
- `final_decision_responses.txt`
- `conversation_control_responses.txt`
- `action_codes.txt`

The JSON files are authoritative for code integration. The text files are convenience copies for reading and reuse.
