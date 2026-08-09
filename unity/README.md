# Unity Integration

The files in this folder define the recommended Unity-side responsibility boundary for protocol `6.3`. They are reference components rather than a drop-in scene implementation.

Recommended flow:

1. Play `BC_OPENING` locally before Turn 1.
2. Obtain participant text from ASR.
3. Build `BcRouteRequest` from the current `ConversationState`.
4. Send the request to your LLM routing layer.
5. Parse the structured `BcRouteResult`.
6. Resolve the route locally with `ResponseLibraryResolver`.
7. Play your locally recorded audio and dispatch the `actionCode`.
8. Record the turn in recent history and advance the turn counter.

`finalRecommendationEnabled` must be computed locally from actual Broad playback: it becomes true only after G01-G08 have each been played at least once.

The response-library JSON is dictionary-heavy. Newtonsoft.Json is generally more convenient than Unity `JsonUtility` for loading it directly; alternatively, transform the JSON to DTO arrays during import.

Do not commit API keys in Unity source or project assets. If you do not want credentials in the client, place the OpenAI call behind your own backend.
