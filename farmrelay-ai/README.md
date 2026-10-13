# FarmRelay AI

**Tagline:** Your AI farm manager that turns everyday challenges into smarter, weather-aware farming plans.

FarmRelay AI is a local-first simulated assistant for coordinating farm work. It turns user-entered farm constraints into a reviewable task plan, explains each task, and flags resource or weather-scenario concerns.

## What works in this prototype

- Local web interface and Python HTTP API.
- Multi-step deterministic planning tools.
- Farm size, worker, inventory, and task inputs.
- Rain scenarios that are explicitly user-entered demo data.
- Sequential task timeline with estimated start/end times and rough crew requirements.
- Visible planning checks/decision trail for input validation, weather scenario, inventory, staffing, and human approval.
- Warnings for simulated fertilizer shortfalls, staffing concerns, and weather-sensitive tasks.
- Exportable plan JSON for review and reproducible demo evidence.
- Human approval step; approval is saved only in the local browser demo.
- Automated tests using Python's standard library.

## Honest limitations

- This version uses transparent heuristics and a rule-based orchestration flow, not a generative AI model.
- Weather values are entered by the user; no live forecast is fetched.
- The fertilizer estimate of 25 kg per acre is only a demo threshold, not agronomic advice or a recommendation.
- It does not operate irrigation, apply chemicals, purchase supplies, or contact workers.
- This is the **simulated Alexa+ web-experience route**, not a production Alexa+ integration or MCP server.

## Requirements

- Python 3.10+ recommended (no pip packages required).
- A modern browser.
- No API keys, cloud account, or paid service.

## Run on Windows

1. Extract this project folder.
2. Open PowerShell in the `farmrelay-ai` folder.
3. Check Python:

   ```powershell
   py --version
   ```

4. Start the server:

   ```powershell
   py server.py
   ```

5. Open `http://127.0.0.1:8000` in your browser.
6. Click **Load example scenario** or edit the inputs and click **Generate my farm plan**.
7. Stop the server with `Ctrl+C`.

If `py` is not recognized, try `python --version` and `python server.py`.

## Run tests

In a second PowerShell window, from the project folder:

```powershell
py -m unittest discover -s tests -v
```

## API

- `GET /api/health` — local service health check.
- `POST /api/plan` — validates inputs and returns a structured draft plan.

Example request:

```json
{
  "location": "Green Valley Farm",
  "crop": "Tomato",
  "acres": 2,
  "workers": 2,
  "fertilizer_kg": 20,
  "rain_forecast": "likely",
  "tasks": ["Inspect crops", "Irrigation check", "Apply fertilizer", "Weed control"]
}
```

## Architecture

```text
Browser UI
  -> POST /api/plan
      -> input validation
      -> validation + scenario checks
      -> inventory + staffing checks
      -> sequential schedule + explanations + warnings
      -> planning decision trail
  <- draft plan
  -> user reviews and approves
  -> browser-local demo save
```

## Hackathon alignment

The project is designed for the Alexa+ simulated web experience option described in the Build, Ship, Shape: Amazon Developer Hackathon rules. It demonstrates an agentic-style workflow with multiple tools, persistent user approval state, and a custom visual interface. Verify the current official rules and FAQ before submitting.

## Product feedback notes to complete truthfully

- Tools used: Python standard library, browser APIs, local JSON HTTP endpoint.
- What worked well: fill this in after testing on your machine.
- What needs work: record actual issues and workarounds encountered.
- Onboarding experience: record your actual setup experience.
- Would you build with these tools again? Answer based on your testing.

## License

MIT. See `LICENSE`.
