# Optional Python Router Example

This is a command-line reference implementation for protocol `6.3`. It calls the OpenAI Responses API directly and uses only the Python standard library; **it is not a FastAPI service and is not required by the repository**.

From this folder:

```bash
# edit .env and add your local API key
python app.py --input-mode asr
```

Then type `start`. The program plays the fixed opening as text, accepts participant text, sends the routing prompt and structured-output schema to the API, resolves the returned route locally, and prints the prerecorded-response text that would be played by Unity.

The example intentionally keeps response generation local: the model returns only the semantic route object.
