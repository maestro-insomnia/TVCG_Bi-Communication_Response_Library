# Python Router Example

This folder contains a small standard-library Python reference implementation of the BC semantic-routing pipeline. It is an example integration, not a required server framework.

The script reads the repository's existing resources directly:

- `../../prompts/routing_prompt.md`
- `../../prompts/route_result.schema.json`
- `../../library/response_library.json`

The LLM returns one structured semantic route. The corresponding virtual-character response is resolved locally from the predefined response library.

## Model compatibility

The example supports both reasoning and non-reasoning models through the OpenAI Responses API with Structured Outputs.

Two model configurations relevant to this repository are:

```text
OPENAI_MODEL=gpt-5.6-luna
```

and

```text
OPENAI_MODEL=gpt-4.1-2025-04-14
```

For GPT-5-family models, the script can send `reasoning.effort` using `OPENAI_REASONING_EFFORT`. For `gpt-4.1-2025-04-14`, the script automatically omits the `reasoning` object because GPT-4.1 is a non-reasoning model. No change to the routing prompt, request schema, result schema, response library, or Unity-side route handling is required.

## Configuration

Edit `.env` directly:

```env
OPENAI_API_KEY=YOUR_LOCAL_KEY
OPENAI_MODEL=gpt-4.1-2025-04-14
OPENAI_REASONING_EFFORT=low
OPENAI_TIMEOUT_SECONDS=60
INPUT_MODE=asr
SHOW_ROUTING_DEBUG=1
```

`OPENAI_REASONING_EFFORT` can remain in `.env` when GPT-4.1 is selected; it is simply ignored.

Do not commit a real API key to a public repository.

## Run

From this folder:

```powershell
python app.py
```

Then type:

```text
start
```

The fixed opening is resolved locally. Each later participant turn is sent to the semantic router together with the current host-maintained conversation state.

Useful commands:

```text
/state
/debug
/reset
/help
/quit
```

You can also override the model without editing `.env`:

```powershell
python app.py --model gpt-4.1-2025-04-14
```

or, for a reasoning model:

```powershell
python app.py --model gpt-5.6-luna --reasoning low
```

## Integration note

This example uses Python's standard library (`urllib`) to keep dependencies minimal. A production Unity application may call the OpenAI API through its own backend or another integration layer while preserving the same route-request and route-result contracts.
