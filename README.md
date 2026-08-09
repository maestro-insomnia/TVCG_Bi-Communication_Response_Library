# TVCG Bi-Communication Response Library

This repository provides the predefined response library, semantic-routing prompt, structured route schemas, and implementation examples used to map participants' natural-language input to controlled virtual-character responses in the bi-directional communication scenario of the study:

> **Virtual Character-Mediated Communication in VR: Effects of Appearance Fidelity and Speech Fidelity**

The resources are intended to support reproduction and reuse of the study's controlled conversational pipeline, in which participant speech is transcribed by ASR, semantically routed to a predefined response code, and resolved locally to a prerecorded virtual-character response and action.


## Purpose

This repository focuses on the files needed to **reuse or implement** the predefined-response conversation system:

- machine-readable response libraries;
- copy-friendly plain-text response libraries;
- the LLM semantic-routing prompt;
- request/result JSON schemas;
- API input/output examples;
- Unity integration examples;
- an optional Python reference implementation;
- audio-file naming/mapping guidance.

The full experimental description, participant instructions, and detailed protocol explanation are provided separately in the paper's supplementary material and are intentionally not duplicated here.

The runtime design is:

```text
Participant speech
-> ASR
-> LLM semantic routing
-> exactly one routeCode
-> Unity / host-side response resolution
-> locally prepared audio + character action
```

The LLM selects a predefined logical route. It does not generate the virtual character's spoken response text.

## Repository Structure

```text
TVCG_Bi-Communication_Response_Library/
├── README.md
├── .gitignore
├── library/
│   ├── README.md
│   ├── response_library.json
│   ├── route_catalog.json
│   ├── fixed_opening.json
│   ├── broad_responses.json
│   ├── specific_responses.json
│   ├── final_decision_responses.json
│   ├── conversation_control_responses.json
│   ├── action_codes.json
│   ├── response_library.schema.json
│   └── text/
│       ├── all_response_texts.txt
│       ├── fixed_opening.txt
│       ├── broad_responses.txt
│       ├── specific_responses.txt
│       ├── final_decision_responses.txt
│       ├── conversation_control_responses.txt
│       └── action_codes.txt
├── prompts/
│   ├── README.md
│   ├── routing_prompt.md
│   ├── route_request.schema.json
│   └── route_result.schema.json
├── examples/
│   ├── README.md
│   ├── api_request_examples.jsonl
│   ├── api_response_examples.jsonl
│   └── python_router/
│       ├── README.md
│       ├── app.py
│       └── .env
├── unity/
│   ├── README.md
│   ├── BcRouteRequest.cs
│   ├── BcRouteResult.cs
│   ├── ConversationState.cs
│   └── ResponseLibraryResolver.cs
└── audio/
    ├── README.md
    └── audio_manifest.example.csv
```

## Response Library

For application development, use the JSON files in `library/`. `response_library.json` provides the combined library, while the category-specific files are convenient when only one response type is needed.

For direct reading or copy/paste, use `library/text/`. `all_response_texts.txt` contains the complete wording in one file, and the other text files separate the Broad, Specific, Final-decision, and Conversation-control libraries.

The fixed opening is stored separately and is not a router-selectable response.

## Routing Prompt and Schemas

The runtime semantic-routing prompt is:

```text
prompts/routing_prompt.md
```

The host-to-router request and structured router result are defined by:

```text
prompts/route_request.schema.json
prompts/route_result.schema.json
```

`library/route_catalog.json` contains the logical route codes available to the router.

## API Examples

Example request and result objects are provided in:

```text
examples/api_request_examples.jsonl
examples/api_response_examples.jsonl
```

These examples are intended to make it easier to reproduce the JSON interface in another application or language.

## Unity Integration

The `unity/` folder provides reference C# classes for:

- building routing requests;
- parsing structured routing results;
- maintaining conversation state;
- resolving Broad-group Preferred/Alternative responses locally;
- mapping logical routes to local response/action data.

These files are reference components rather than a complete Unity scene or project.

## Optional Python Reference

`examples/python_router/` provides a small Python command-line reference implementation for calling the OpenAI API with the routing prompt and structured output schema. It is optional and is not required by the library.

Before using it, edit:

```text
examples/python_router/.env
```

and add your own local API key. Do not commit a real API key to a public repository.

## Audio Availability

The original experiment audio is **not included** because it cannot be redistributed for copyright/licensing reasons.

`audio/audio_manifest.example.csv` shows the expected response-code/audio-file mapping so researchers can create and connect their own recordings.

## Citation

If you use these resources in your research, please cite the associated paper:

> *Yu Han, Hao Sha, Tongtai Cao, Xin Wang, Yu Miao, Yue Liu, Huyen Nguyen, and Christian Sandor, “Virtual Character-Mediated Communication in VR: Effects of Appearance Fidelity and Speech Fidelity.”*
