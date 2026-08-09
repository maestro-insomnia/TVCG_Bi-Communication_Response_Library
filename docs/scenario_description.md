# Scenario Description

## Bi-directional communication scenario

The BC scenario is a two-way conversation in which the virtual character asks the participant for help choosing between two tops: a light blue button-up shirt and a deep forest green hoodie.

All virtual-character speech is predefined and was recorded before the experiment. Participant speech is converted to text by ASR. The ASR text together with host-maintained conversation state is sent to the semantic router, which returns one predefined logical route code. The host application then resolves that route to a local prerecorded response and character action.

The LLM is used to interpret participant input and select a response route; it does **not** generate virtual-character response text.

## Fixed opening

Before Turn 1, the application plays:

> Hey, my friend. I really need your help. I have found two tops that I absolutely love, but I am completely stuck on which one to get.

The opening is stored separately in `library/fixed_opening.json`, is not part of the selectable response library, and must never be returned as a route code.

## Library size

Excluding the fixed opening, the final library contains:

- 18 Broad response recordings (9 Preferred + 9 Alternative);
- 48 Specific responses;
- 2 Final-decision responses;
- 7 Conversation-control responses;
- **75 selectable prerecorded responses in total**.

The router has 66 logical outputs because each of the nine Broad routes resolves locally to one of two prerecorded variants.
