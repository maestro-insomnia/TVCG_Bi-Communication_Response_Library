# TVCG Bi-Communication Response Library

Predefined response library, LLM-based semantic-routing prompt, JSON schemas, routing examples, and Unity integration resources for the bi-directional communication (BC) scenario used in the study **“Virtual Character-Mediated Communication in VR: Effects of Appearance Fidelity and Speech Fidelity.”**

## Overview

This repository provides the response library and routing resources used to implement the bi-directional communication scenario in the study.

In this scenario, a virtual character asks the participant for help choosing between two tops. The participant communicates with the character in their own words, asks questions to gather information about the two options, and eventually provides a recommendation.

The system uses a predefined-response architecture rather than generating virtual-character dialogue dynamically. Participant speech is first converted to text by an automatic speech recognition (ASR) system. An LLM-based semantic router then corrects likely ASR recognition errors, interprets the participant's intended meaning, and selects one predefined response route. The host application, such as Unity, resolves that route locally and plays the corresponding prerecorded response and character action.

The LLM is therefore used as a **semantic router, not as a dialogue generator**.

## Repository Contents

This repository includes:

* the fixed opening message used before the interactive conversation begins;
* 9 broad response groups with 18 Preferred/Alternative response texts;
* 48 specific responses;
* 2 final-decision responses;
* 6 conversation-control responses;
* action-code definitions;
* the complete response-routing catalog;
* an LLM prompt for contextual ASR correction and semantic intent routing;
* JSON schemas for routing requests and structured routing results;
* routing examples and test cases;
* Unity C# data structures and response-resolution examples;
* an optional Python/FastAPI routing example;
* documentation describing the scenario, participant instructions, system architecture, response-selection rules, and API protocol.

The fixed opening message is stored separately and is not selectable by the LLM router.

Excluding the fixed opening, the response library contains **74 selectable prerecorded responses**:

* 18 broad responses;
* 48 specific responses;
* 2 final-decision responses;
* 6 conversation-control responses.

## Audio Availability

Audio recordings from the original experiment are **not included in this repository because they cannot be redistributed for copyright or licensing reasons**.

The response texts, response codes, action mappings, and recommended audio-file naming conventions are provided so that researchers can create their own recordings while preserving the same response structure.

See:

```text
audio/README.md
audio/audio_manifest.example.csv
```

## Core Design Principle

The communication pipeline is conceptually:

```text
      Participant Speech
              |
              v
             ASR
              |
              v
         Raw ASR Text
              |
              v
+----------------------------+
| LLM Semantic Router        |
|                            |
| 1. Contextual ASR          |
|    correction              |
| 2. Reference resolution    |
| 3. Intent recognition      |
| 4. Route selection         |
+-------------+--------------+
              |
              v
        ONE Route Code
              |
              v
+----------------------------+
| Unity / Host Application   |
|                            |
| - broad-response switching |
| - response-library lookup  |
| - audio selection          |
| - character-action control |
+----------------------------+
```

The response library is independent of any particular client-server architecture.

The LLM router may be called:

* directly from Unity;
* through a local backend;
* through a remote backend;
* or through another application layer.

A Python/FastAPI example is included only as an optional implementation example. **FastAPI is not required to use this response library or routing protocol.**

## Repository Structure

```text
TVCG_BC_Response_Library/
|
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
|
├── docs/
|   ├── participant_instructions.md
|   ├── scenario_description.md
|   ├── system_architecture.md
|   ├── response_selection_rules.md
|   └── api_protocol.md
|
├── library/
|   ├── fixed_opening.json
|   ├── response_library.json
|   ├── broad_responses.json
|   ├── specific_responses.json
|   ├── final_decision_responses.json
|   ├── conversation_control_responses.json
|   ├── route_catalog.json
|   ├── action_codes.json
|   └── response_library.schema.json
|
├── prompts/
|   ├── bc_intent_router_v1.md
|   ├── domain_terms.json
|   ├── route_request.schema.json
|   └── route_result.schema.json
|
├── examples/
|   ├── api_request_examples.jsonl
|   ├── api_response_examples.jsonl
|   ├── routing_test_cases.jsonl
|   └── python_router/
|       ├── README.md
|       ├── app.py
|       ├── requirements.txt
|       └── .env.example
|
├── unity/
|   ├── README.md
|   ├── AgentRouteRequest.cs
|   ├── AgentRouteResult.cs
|   ├── ConversationState.cs
|   └── ResponseLibraryResolver.cs
|
└── audio/
    ├── README.md
    └── audio_manifest.example.csv
```

## Fixed Opening Message

Before the participant's first turn, the virtual character automatically delivers the fixed opening message.

The opening message is stored separately in:

```text
library/fixed_opening.json
```

It is not part of the selectable response library and must never be returned as an LLM routing result.

After the fixed opening message finishes, the participant begins the first interactive turn.

## Response Categories

The selectable response library contains four response categories.

| Category | LLM returns         | Host-application behavior                                |
| -------- | ------------------- | -------------------------------------------------------- |
| Broad    | `G01_...`–`G09_...` | Resolve locally to Preferred or Alternative response     |
| Specific | `BC_SPC..`          | Use the directly mapped response                         |
| Decision | `BC_DEC..`          | Use the selected final response and end the conversation |
| Control  | `BC_CTL..`          | Use the corresponding clarification/control response     |

### Broad Responses

Broad responses are used when the participant asks for a general description or requests information covering a broader aspect of one or both clothing options.

There are nine broad response groups.

Each group contains:

```text
Preferred Response
Alternative Response
```

The LLM returns only the broad **group code**, for example:

```text
G01_SHIRT_OVERVIEW
```

The LLM does **not** select Preferred or Alternative.

The host application maintains a local count for each broad group:

```text
1st selection -> Preferred
2nd selection -> Alternative
3rd selection -> Preferred
4th selection -> Alternative
...
```

Thus, odd-numbered selections use the Preferred response and even-numbered selections use the Alternative response.

This prevents the exact same broad response from being played twice consecutively when a participant asks a similar broad question again.

### Specific Responses

Specific responses are used when the participant asks about one clearly defined information point, such as:

* color;
* material;
* pattern;
* fit;
* buttons;
* logo;
* lining;
* wearing method;
* comfort;
* replaceability;
* current preference.

Each specific intent maps directly to one response code.

For example:

```text
BC_SPC02_SHIRT_COLOR
BC_SPC23_HOODIE_COLOR
BC_SPC27_HOODIE_FIT
BC_SPC47_CURRENT_PREFERENCE
```

Specific responses do not use Preferred/Alternative switching.

### Final-Decision Responses

Final-decision responses are available only during the final recommendation stage.

If the participant clearly recommends the hoodie:

```text
BC_DEC01_HOODIE
```

If the participant clearly recommends the shirt:

```text
BC_DEC02_SHIRT
```

After either final-decision response is played, the conversation ends.

If the participant does not clearly choose one option, recommends both options, or gives no final recommendation, the system uses:

```text
BC_CTL06_FINAL_CHOICE
```

to request a single final choice.

### Conversation-Control Responses

Conversation-control responses handle cases in which normal information routing is not appropriate.

These include:

```text
BC_CTL01_ONE_QUESTION
```

The participant asks two or more separate questions in the same turn.

```text
BC_CTL02_CLARIFY_ITEM
```

The requested information is identifiable, but it is unclear whether the participant means the first or second top.

```text
BC_CTL03_CLARIFY_DETAIL
```

The target item is identifiable, but the information being requested is unclear.

```text
BC_CTL04_ASR_RETRY
```

The ASR transcript is too incomplete or unclear to recover the participant's intended meaning reliably.

```text
BC_CTL05_OUT_OF_SCOPE
```

The participant's input is understandable but unrelated to the clothing-choice task.

```text
BC_CTL06_FINAL_CHOICE
```

The participant has not provided one clear recommendation during the final recommendation stage.

## LLM Routing Pipeline

The LLM router performs four logically ordered operations.

### 1. Contextual ASR Correction

The raw ASR transcript must first be treated as potentially noisy speech-recognition output.

The router considers:

* the complete ASR utterance;
* recent conversation context;
* the currently active item;
* grammatical plausibility;
* semantic plausibility;
* phonetic similarity;
* vocabulary relevant to the clothing-choice scenario.

For example:

```text
Raw ASR:
"What color are the bottoms on the short?"

Possible corrected utterance:
"What color are the buttons on the shirt?"
```

when the surrounding context strongly supports this interpretation.

ASR correction is performed before intent classification.

The router must make only the minimum correction necessary to reconstruct the likely intended utterance.

It must not modify the participant's meaning merely because the participant's question conflicts with information in the response library.

For example:

```text
"Is the shirt made of linen?"
```

must not be changed to:

```text
"Is the shirt made of cotton?"
```

simply because the library states that the shirt is made of cotton.

### 2. Reference Resolution

The router then resolves expressions such as:

```text
it
that one
the first one
the second one
the other one
```

using the recent dialogue and the application's `activeItem` state.

For example:

```text
activeItem = first_top

Participant:
"What about the other one?"
```

is interpreted as referring to the second top.

### 3. Intent Recognition

The corrected utterance is classified according to its semantic meaning rather than through exact keyword matching.

Broad and specific questions are distinguished by their requested information scope.

For example:

```text
"What is the first top like?"
-> G01_SHIRT_OVERVIEW
```

whereas:

```text
"What color is the first top?"
-> BC_SPC02_SHIRT_COLOR
```

Similarly:

```text
"Tell me how often you might wear the two tops."
-> G07_EXPECTED_USAGE
```

whereas:

```text
"Which one would you wear more?"
-> BC_SPC45_WHICH_WEAR_MORE
```

### 4. Route Selection

Exactly **one route code** is returned for each participant turn.

The LLM does not:

* generate the virtual character's spoken reply;
* modify predefined response text;
* select Preferred versus Alternative;
* select an audio file;
* select a specific animation;
* return multiple response codes.

The route code is the primary control signal returned to the host application.

## Routing Request Format

A routing request should contain the current ASR transcript and sufficient conversation state to interpret it.

A typical request is:

```json
{
  "protocolVersion": "1.0",
  "turnIndex": 4,
  "stage": "information_gathering",
  "activeItem": "first_top",
  "rawAsrText": "what color are the bottoms on the short",
  "recentTurns": [
    {
      "turnIndex": 3,
      "participantText": "tell me about the first one",
      "correctedParticipantText": "Tell me about the first one.",
      "routeCode": "G01_SHIRT_OVERVIEW"
    }
  ]
}
```

The complete request schema is provided in:

```text
prompts/route_request.schema.json
```

## Structured Routing Result

A routing result contains the corrected ASR interpretation together with one route code.

Example:

```json
{
  "correctedAsrText": "What color are the buttons on the shirt?",
  "correctionStatus": "corrected",
  "asrCorrectionConfidence": 0.97,
  "target": "first_top",
  "routeCategory": "specific",
  "routeCode": "BC_SPC06_SHIRT_BUTTONS",
  "intentConfidence": 0.99
}
```

The corresponding schema is provided in:

```text
prompts/route_result.schema.json
```

The corrected ASR text and confidence fields are useful for logging, debugging, and later evaluation.

The field that controls the experiment is:

```text
routeCode
```

## Conversation State

Conversation state should be controlled by the host application rather than inferred entirely by the LLM.

At minimum, the application should maintain:

```text
turnIndex
stage
activeItem
recentTurns
broadGroupCounts
conversationEnded
```

Recommended stages are:

```text
information_gathering
final_recommendation
```

The application, rather than the LLM, determines when the experiment enters the final recommendation stage.

This prevents an incidental preference statement during information gathering from prematurely ending the conversation.

## Unity Response Resolution

For a specific route:

```text
BC_SPC23_HOODIE_COLOR
```

Unity can directly resolve:

```text
route code
-> response-library entry
-> locally prepared audio
-> action code
```

For a broad route:

```text
G03_HOODIE_OVERVIEW
```

Unity first increments the local count for that group.

For example:

```text
G03 count = 1
-> BC_BRD03_PREFERRED

G03 count = 2
-> BC_BRD03_ALTERNATIVE

G03 count = 3
-> BC_BRD03_PREFERRED
```

The LLM is not involved in this Preferred/Alternative selection process.

See:

```text
unity/ResponseLibraryResolver.cs
```

## Integration Options

The response library and routing protocol do not require a particular networking architecture.

### Option 1: Direct Unity Integration

Unity may directly send the routing request to the LLM API and parse the structured result.

Conceptually:

```text
Unity
  |
  +-- ASR
  |
  +-- build routing request
  |
  +-- call LLM API
  |
  +-- receive routeCode
  |
  +-- resolve local response
```

This is the simplest architecture when API credentials and deployment conditions can be managed appropriately.

### Option 2: Backend Routing Layer

A backend may be placed between Unity and the LLM API:

```text
Unity
   |
   v
Local or Remote Backend
   |
   v
LLM API
```

This can be useful when researchers want to:

* keep API credentials outside the Unity client;
* centralize prompt loading;
* validate structured output before returning it to Unity;
* centralize logging and error handling.

The backend implementation is not part of the experimental protocol and may be written in Python, C#, JavaScript, or another language.

## Optional Python/FastAPI Example

The directory:

```text
examples/python_router/
```

contains a minimal FastAPI implementation showing one possible backend architecture.

This example demonstrates:

```text
Unity/application request
-> FastAPI endpoint
-> LLM API
-> structured routing result
-> Unity/application
```

It is included only as a reusable programming example.

**FastAPI is not required to use this repository.**

Researchers who prefer direct Unity integration or another backend technology can ignore this directory entirely.

## OpenAI API Notes

The provided routing example is designed around structured JSON output so that the host application receives a predictable result rather than free-form natural-language output.

Model selection should remain configurable.

For exact experimental reproduction, researchers should use the same model version used in the original experiment when available rather than silently substituting a newer model version.

The selected model identifier, routing-prompt version, and schema version should be recorded in the experiment configuration or logs.

For example:

```json
{
  "model": "<MODEL_ID>",
  "promptVersion": "bc_intent_router_v1",
  "schemaVersion": "1.0"
}
```

API keys must not be committed to the repository.

Use environment variables or another appropriate secret-management mechanism.

## Prompt

The complete routing prompt is provided in:

```text
prompts/bc_intent_router_v1.md
```

Its required processing sequence is:

```text
Raw ASR
-> Contextual ASR Correction
-> Reference Resolution
-> Intent Recognition
-> Route Selection
```

The prompt explicitly requires the model to distinguish between uncertain ASR transcription and uncertain semantic intent.

If the wording cannot be reconstructed reliably but the communicative intent remains clear, the system may still route the utterance normally.

If the transcript is too corrupted to identify the requested information, the system routes to:

```text
BC_CTL04_ASR_RETRY
```

## Routing Catalog

All valid LLM-returnable route codes are defined in:

```text
library/route_catalog.json
```

The fixed opening message is deliberately excluded from this catalog.

The routing catalog contains:

```text
9 broad route codes
48 specific route codes
2 decision route codes
6 conversation-control route codes
```

for a total of:

```text
65 valid routing outputs
```

These 65 routes ultimately resolve to the 74 selectable response recordings because each of the nine broad routes corresponds to two local response variants.

## Testing and Evaluation

Example routing cases are provided in:

```text
examples/routing_test_cases.jsonl
```

The test cases include:

* straightforward broad questions;
* straightforward specific questions;
* pronoun and reference-resolution cases;
* multiple-question cases;
* final recommendation cases;
* unclear-item cases;
* ASR recognition-error cases.

Examples of intentionally noisy ASR inputs include:

```text
short -> shirt
bottoms -> buttons
hoody -> hoodie
feet -> fit
```

These examples should not be interpreted as a fixed word-replacement dictionary. The router is expected to use the full utterance and conversation context when deciding whether a correction is appropriate.

Researchers adapting the routing system to another model are encouraged to evaluate routing accuracy using these test cases before deploying the model in an experiment.

## Validation

Repository consistency can be checked using:

```bash
python scripts_validate.py
```

The validation script checks items such as:

* expected response-library counts;
* route-code uniqueness;
* valid broad-group mappings;
* consistency between route catalogs and schemas;
* exclusion of the fixed opening from selectable routes.

## Participant Instructions

The participant instructions used in the scenario are provided in:

```text
docs/participant_instructions.md
```

The instructions encourage participants to:

* communicate naturally with the virtual character;
* begin with broad questions when useful;
* ask more specific follow-up questions based on the information received;
* keep questions short, clear, and direct;
* focus on one main idea at a time whenever possible;
* use their own judgment to provide a final recommendation.

These instructions are part of the experimental setup and should be considered when reproducing the original communication task.

## Adapting the Library

Researchers may adapt this repository for other controlled conversational studies by replacing:

* the scenario;
* predefined response texts;
* route catalog;
* locally prepared speech recordings;
* action mappings;
* routing prompt.

The general control structure can remain:

```text
natural participant input
-> ASR
-> contextual semantic routing
-> predefined response code
-> controlled virtual-character response
```

For controlled experiments, keeping semantic interpretation separate from response generation can help maintain consistency in the information provided across participants.

## Citation

Before publishing or redistributing a derived package, update:

```text
CITATION.cff
```

with the final paper and repository metadata.

If you use this response library or adapt its routing architecture in academic work, please cite the associated paper and repository.

## License

See:

```text
LICENSE
```

for the repository's licensing terms.

The original experiment audio is not distributed and is therefore not covered as repository content.
