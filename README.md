# TVCG Bi-Communication Response Library

Predefined response library, finalized LLM semantic-routing prompt, protocol schemas, routing examples, and Unity integration resources for the bi-directional communication (BC) scenario used in the study **“Virtual Character-Mediated Communication in VR: Effects of Appearance Fidelity and Speech Fidelity.”**

Repository: https://github.com/maestro-insomnia/TVCG_Bi-Communication_Response_Library

## Overview

In the BC scenario, a virtual character asks a participant for help choosing between two tops. The participant communicates in their own words, gathers information about the two options, and ultimately recommends one top.

The system uses a **predefined-response architecture**. The LLM is a semantic router, not a dialogue generator:

```text
Participant speech
-> ASR
-> contextual ASR reconstruction
-> semantic routing
-> exactly ONE routeCode
-> Unity/local response resolution
-> prerecorded audio + character action
```

All virtual-character response text is predefined in `library/`. The router never generates spoken response text, never chooses the Broad Preferred/Alternative variant, and never chooses character actions.

## Final Protocol

This repository implements routing protocol **6.3** and uses the finalized prompt:

```text
prompts/router_prompt_compact_v2.md
```

The final protocol uses:

- 8 regular Broad groups: four information dimensions for the first top and the same four for the second top;
- 1 special Broad group (`G09_CURRENT_PREFERENCE`) for an explicit overall request about the character's current desired choice;
- 48 Specific routes;
- 2 Decision routes;
- 7 Conversation-Control routes.

The router therefore has **66 logical route codes**. The local response library contains **75 selectable prerecorded responses** because each of the 9 Broad routes has both a Preferred and an Alternative recording. The fixed opening is separate and is not selectable by the router.

## Audio Availability

The original experiment audio is **not included** because it cannot be redistributed for copyright/licensing reasons. The repository provides an audio mapping template so researchers can create their own recordings. See `audio/README.md`.

## Repository Structure

```text
TVCG_Bi-Communication_Response_Library/
├── README.md
├── CITATION.cff
├── CHANGELOG.md
├── .gitignore
├── validate_repository.py
│
├── docs/
│   ├── participant_instructions.md
│   ├── scenario_description.md
│   ├── system_architecture.md
│   ├── response_selection_rules.md
│   └── routing_protocol.md
│
├── library/
│   ├── response_library.json
│   ├── route_catalog.json
│   ├── fixed_opening.json
│   ├── broad_responses.json
│   ├── specific_responses.json
│   ├── final_decision_responses.json
│   ├── conversation_control_responses.json
│   ├── action_codes.json
│   └── response_library.schema.json
│
├── prompts/
│   ├── README.md
│   ├── router_prompt_compact_v2.md
│   ├── route_request.schema.json
│   └── route_result.schema.json
│
├── examples/
│   ├── README.md
│   ├── api_request_examples.jsonl
│   ├── api_response_examples.jsonl
│   └── python_router/
│       ├── README.md
│       ├── app.py
│       └── .env.example
│
├── unity/
│   ├── README.md
│   ├── BcRouteRequest.cs
│   ├── BcRouteResult.cs
│   ├── ConversationState.cs
│   └── ResponseLibraryResolver.cs
│
├── tests/
│   ├── README.md
│   ├── conversation_test_cases.json
│   └── run_api_tests.py
│
└── audio/
    ├── README.md
    └── audio_manifest.example.csv
```

No LaTeX source from the paper/supplement is included in the GitHub package.

## Fixed Opening

Before the first participant turn, the host application plays the fixed opening locally:

> Hey, my friend. I really need your help. I have found two tops that I absolutely love, but I am completely stuck on which one to get.

It is stored in `library/fixed_opening.json`. It is not part of the 75 selectable responses and must never be returned by the LLM.

## Participant Interaction Structure

Participants are instructed to ask the same four main Broad question types separately about each top:

1. what it looks like;
2. what the character likes about it and how it could be worn;
3. how it fits with clothes already owned / what need it fills / likely use;
4. how easy it would be to replace.

The first-top Broad routes are `G01-G04`; the corresponding second-top routes are `G05-G08`.

## Grounding Rules

- `G01_SHIRT_OVERVIEW` introduces the first top.
- `G05_HOODIE_OVERVIEW` introduces the second top.
- A Specific question asked before its top is introduced is first routed to the corresponding overview.
- The second-top overview cannot precede the first-top overview because its prerecorded wording assumes that the first option has already been described.

These gates are implemented by the semantic router using `playedBroadGroups` supplied by the host.

## Broad Preferred/Alternative Resolution

The LLM returns a Broad **group code**, not a prerecorded Broad response code. Unity/host maintains a count for each Broad group:

```text
1st, 3rd, 5th, ... -> Preferred
2nd, 4th, 6th, ... -> Alternative
```

Example:

```text
G05_HOODIE_OVERVIEW
  count 1 -> BC_BRD05_PREFERRED
  count 2 -> BC_BRD05_ALTERNATIVE
  count 3 -> BC_BRD05_PREFERRED
```

## Final Recommendation Gate

The host computes `finalRecommendationEnabled`. It becomes true only after **all eight regular Broad groups G01-G08 have each actually played at least once**. G09 and Specific responses do not count toward this condition.

Enabling final recommendations does not stop information gathering. Participants can continue asking Broad or Specific follow-up questions.

When there is no information request in the same turn:

- recommendation before enabled -> `BC_CTL07_CONTINUE_ASKING`;
- enabled + hoodie recommendation -> `BC_DEC01_HOODIE`;
- enabled + shirt recommendation -> `BC_DEC02_SHIRT`;
- enabled + both/neither/unclear selection -> `BC_CTL06_FINAL_CHOICE`.

Either Decision response ends the conversation.

## ASR Reconstruction Before Intent Routing

`inputMode` may be `typed` or `asr`. For ASR input, the finalized Compact v2 prompt treats punctuation and word recognition as potentially noisy. Before route selection, it may:

- reconstruct missing clause boundaries and punctuation;
- repair misleading ASR punctuation;
- make minimal context-supported lexical corrections;
- use `activeItem` and up to four `recentTurns` for reliable reference resolution.

The router must not change the participant's meaning simply to match facts in the response library. For example, a genuine question asking whether the shirt is made of linen must not be rewritten as a question about cotton merely because cotton is the known library fact.

## One Request Per Turn

The protocol counts genuine information-seeking requests rather than surface mentions of features. Comments, reactions, summaries, and recommendations do not create additional questions by themselves.

- 2+ independent information requests -> `BC_CTL01_ONE_QUESTION`;
- exactly 1 information request -> answer that request even if commentary or a recommendation also appears in the turn;
- recommendation-only handling occurs only when there is no information request left to answer.

## API Request

Requests follow `prompts/route_request.schema.json`. Example:

```json
{
  "protocolVersion": "6.3",
  "turnIndex": 3,
  "finalRecommendationEnabled": false,
  "inputMode": "asr",
  "activeItem": "first_top",
  "rawInputText": "what color are the bottoms on the short",
  "playedBroadGroups": ["G01_SHIRT_OVERVIEW"],
  "recentTurns": []
}
```

## Structured Router Result

The router returns the strict object defined by `prompts/route_result.schema.json`. Example:

```json
{
  "correctedInputText": "What color are the buttons on the shirt?",
  "correctionStatus": "corrected",
  "punctuationStatus": "restored",
  "utteranceType": "question",
  "informationRequestCount": 1,
  "routingBasisText": "What color are the buttons on the shirt?",
  "semanticTarget": "first_top",
  "intentClass": "specific_detail",
  "routeCategory": "specific",
  "routeCode": "BC_SPC06_SHIRT_BUTTONS",
  "confidence": 0.98
}
```

`routeCode` is the field used for local response selection. The other fields are diagnostic and can be logged for later routing-error analysis.

## OpenAI API Integration

The optional Python example uses the OpenAI **Responses API** with strict structured JSON output. The repository does not require Python, FastAPI, or a particular transport architecture. Researchers may implement the same protocol directly in Unity/C#, in another backend language, or in any environment that can send the request object and validate the structured result.

Model selection is configurable. For experimental reproducibility, record the exact model identifier/snapshot and reasoning setting used during data collection. Do not commit API keys.

## Optional Python Reference

`examples/python_router/app.py` is a small standard-library command-line tester. It is intended to demonstrate the protocol and local response resolution; it is **not** a required server.

```bash
cd examples/python_router
cp .env.example .env
# edit .env
python app.py --self-test
python app.py --input-mode asr
```

## Unity Integration

The Unity examples keep state and local response resolution outside the LLM. In particular, Unity/host owns:

- `playedBroadGroups`;
- per-Broad selection counts;
- `finalRecommendationEnabled`;
- local response/audio lookup;
- action dispatch;
- conversation termination after a Decision response.

See `unity/README.md`.

## Testing

Validate repository structure and route consistency without API calls:

```bash
python validate_repository.py
python tests/run_api_tests.py --validate-only
```

The API test runner uses the finalized Compact v2 prompt and the frozen multi-turn test cases supplied with the final router package. Running live API tests incurs API usage.

## Reuse

Researchers can reuse the protocol while replacing the scenario-specific library, locally recorded speech, or virtual-character actions. For controlled experiments, keeping semantic interpretation separate from response generation helps ensure that participants receive predefined information rather than unconstrained model-generated dialogue.

## Citation

Update `CITATION.cff` with the final bibliographic metadata and repository URL before public release. If you reuse this response library or routing protocol in academic work, cite the associated paper and repository.

## Licensing

No license is selected automatically by this package. Add the repository license you intend to use before public release. The original experiment audio is not distributed.
