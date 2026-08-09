# System Architecture

```text
Participant speech
      |
      v
ASR
      |
      v
rawInputText + host conversation state
      |
      v
LLM Semantic Router (Protocol 6.3)
      |-- contextual ASR lexical correction
      |-- punctuation/clause reconstruction
      |-- conversational-act classification
      |-- reference resolution
      |-- grounding/final-recommendation gates
      |-- exactly ONE routeCode
      v
Unity / host application
      |-- Broad route: local odd/even count -> Preferred/Alternative
      |-- Specific/Decision/Control: direct local response
      |-- response-library lookup
      |-- local audio lookup
      |-- action-code dispatch
      v
Virtual-character playback and behavior
```

## Responsibility boundaries

| Component | Responsibility |
|---|---|
| ASR | Participant speech -> raw transcript |
| LLM router | Reconstruct likely ASR wording and select one logical route |
| Unity / host | Maintain state, track played Broad groups, compute final-recommendation gate, resolve Broad alternation |
| Response library | Authoritative prerecorded-response text/action metadata |
| Local audio library | Researcher-supplied recordings keyed by response code |
| Character controller | Action code -> project-specific animation/behavior |

The protocol is transport-independent. The OpenAI request may be made directly from a host application or through a backend. The optional Python example in `examples/python_router/` is a command-line reference implementation, not a required service.
