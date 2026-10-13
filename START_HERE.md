# FarmRelay AI — start here

This download contains two separate projects:

1. `farmrelay-ai/` — the primary simulated Alexa+ web experience.
2. `farmplan-guard/` — the additional open-source mini-challenge project.

## First: run the main project

Open PowerShell in `farmrelay-ai` and run:

```powershell
py --version
py server.py
```

Then open http://127.0.0.1:8000.

## Second: test the main project

Open a second PowerShell window in `farmrelay-ai`:

```powershell
py -m unittest discover -s tests -v
```

## Third: test the open-source project

Open PowerShell in `farmplan-guard`:

```powershell
py -m unittest discover -s tests -v
```

No pip installs or paid services are required.

## What changed in the hackathon-readiness update

- The schedule now includes estimated start/end times and rough crew-size checks.
- The dashboard shows a planning decision trail and lets you export a plan as JSON.
- Input validation rejects fractional worker counts and oversized task lists.
- Additional tests cover sequential scheduling, duplicate tasks, staffing review, and the human-approval gate.
- Weather and fertilizer calculations remain clearly labeled demo assumptions; no live weather or external AI is called.

## Before submitting

- Run both test suites on your laptop.
- Verify the demo end-to-end and record a public video under 3 minutes.
- Publish the main repository with its license and run instructions.
- Publish `farmplan-guard` as a separate public repository during the hackathon window.
- Complete product feedback based on your real experience.
- Record genuine tool friction, expected vs. actual behavior, severity, workaround, and actionable suggestion.
- Add the actual GitHub URLs and open-source contribution details to Devpost.
- Do not claim the demo uses live weather or a real Alexa+ connection; it currently does neither.
