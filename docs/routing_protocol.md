# Routing Protocol 6.3

## Request

The host sends the fields defined in `prompts/route_request.schema.json`:

- `protocolVersion` (`6.3`);
- `turnIndex`;
- `finalRecommendationEnabled` (host-computed);
- `inputMode` (`typed` or `asr`);
- `activeItem`;
- `rawInputText`;
- `playedBroadGroups`;
- up to four `recentTurns`.

`playedBroadGroups` and `finalRecommendationEnabled` are authoritative host state. The model must not infer that a Broad group has played merely because the participant mentions its content.

## Router processing order

The finalized Compact v2 prompt requires the router to process each turn in this order:

```text
raw input
-> contextual ASR lexical/punctuation reconstruction
-> conversational-act classification
-> information-request counting
-> reference/target resolution
-> grounding and recommendation gates
-> Broad / Specific / comparison / preference routing
-> exactly one structured result
```

The ASR transcript is not treated as ground truth. Punctuation may be absent or misleading, and small lexical errors may be repaired when supported by context. Corrections must not substitute library facts for what the participant appeared to say.

## Result

The LLM returns the object defined by `prompts/route_result.schema.json`, including:

- `correctedInputText`;
- `correctionStatus`;
- `punctuationStatus`;
- `utteranceType`;
- `informationRequestCount`;
- `routingBasisText`;
- `semanticTarget`;
- `intentClass`;
- `routeCategory`;
- `routeCode`;
- `confidence`.

Only `routeCode` drives response selection. The diagnostic fields are useful for logging, auditing, and routing-error analysis. Confidence is model-reported and should not be treated as a calibrated probability unless separately calibrated.
