# Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps

**75-Minute (1 hr 15 min) GDE Talk + Hands-On Workshop Presentation & Facilitator Kit**
- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)
- **Base Codelab**: [https://codelabs.developers.google.com/adk-mcp-bigquery-maps](https://codelabs.developers.google.com/adk-mcp-bigquery-maps)
- **Companion repo (lab code)**: [github.com/google/mcp → examples/launchmybakery](https://github.com/google/mcp/tree/main/examples/launchmybakery)

---

## What this session is

A story-driven talk that builds the concepts first — what makes an LLM an *agent*, how **ADK** defines one, why **MCP** turns N×M integrations into N+M, and how Google's **managed remote MCP servers** for BigQuery and Google Maps hand the agent its tools — then a guided hands-on workshop where every attendee builds the agent themselves.

The running scenario: *"Help a friend open a high-end sourdough bakery in Los Angeles."* One conversation walks down the decision funnel — foot-traffic (BigQuery) → market saturation (Maps) → pricing (BigQuery) → revenue forecast (BigQuery `AI.FORECAST`) → supplier logistics (Maps) — switching servers with no glue code.

---

## 📂 Files in This Folder

| File | Purpose |
| :--- | :--- |
| [`Location_Intelligence_ADK_MCP_Workshop.pptx`](./Location_Intelligence_ADK_MCP_Workshop.pptx) | **38-Slide Editable PowerPoint / Google Slides Deck** on the Google Cloud Labs master theme, with codelab screenshots, the demo GIF still, scannable QR codes, and **full speaker notes embedded in every slide**. |
| [`index.html`](./index.html) | **Interactive Web Presentation Deck** matching the Google Cloud Labs theme, with live polls, click-to-reveal quizzes, hands-on lab countdown timers, 1-click copy buttons for every command/prompt, an inline **Teleprompter Drawer (`S`)**, and a **Dual-Screen Synchronized Presenter Console (`P`)**. |
| [`speaker-notes.html`](./speaker-notes.html) | **Standalone Live Speaker Console & Continuous Talk Script** (synced with `index.html` via `BroadcastChannel`, or usable standalone on a second screen, tablet, or phone). |
| [`SPEAKER_NOTES_AND_SCRIPT.md`](./SPEAKER_NOTES_AND_SCRIPT.md) | **Complete Markdown Facilitator Runbook & Verbatim Talk Script** with minute-by-minute pacing, engagement cues, copy-paste commands/prompts, and the 6-point troubleshooting table. |
| [`present.sh`](./present.sh) | **One-Command Live Presentation Launcher** (`./present.sh`). Starts a local HTTP server and opens the interactive slide deck. |
| [`generate_slides.py`](./generate_slides.py) | Reproducible Python generator that builds the `.pptx`, `index.html`, `speaker-notes.html`, and `.md` from one `SLIDES_DATA` list. Edit that, re-run, and all four artifacts regenerate together. |

---

## 🚀 Quick Start: Presenting Live

### Option 1: Present Directly from Browser (Interactive + Dual-Screen Notes)
```bash
cd Location-Intelligence-ADK-MCP-Workshop
./present.sh            # serves on http://localhost:8086
```
- Press **`P`** to pop the **Synchronized Speaker Notes Console** onto your laptop screen while keeping `index.html` full-screen (`F`) on the projector.
- Press **`S`** to toggle the built-in Speaker Notes Teleprompter drawer.
- Press **`→`** to advance; on the build-diagram slides each press reveals the next block.

### Option 2: Present from Google Slides or PowerPoint
1. Upload `Location_Intelligence_ADK_MCP_Workshop.pptx` to Google Drive and open with **Google Slides** (or open directly in PowerPoint / Keynote).
2. **Slideshow → Presenter view** shows the embedded slide-by-slide script and timing cues.

---

## ⏱️ Session Arc (75 min)

| Time | Module | Slides | Hands-on beat |
| :--- | :--- | :--- | :--- |
| 00:00–00:06 | Welcome & Start Engines | 1–5 | Redeem credits, kick off both setup scripts in the background |
| 00:06–00:26 | Concepts (Agent → ADK → MCP → Tools) | 6–20 | Poll, quiz, guardrails |
| 00:26–00:36 | Lab A: Setup | 21–25 | ✋ CP1: `mcp_bakery` dataset live |
| 00:36–00:52 | Lab B: Run the Agent | 26–32 | ✋ CP2 macro SQL · ✋ CP3 Maps · bonus breaks |
| 00:52–01:03 | Troubleshoot, Cleanup, Playbook | 32–36 | Flexible buffer + cleanup + 4 takeaways |
| 01:03–01:15 | Closing & Q&A | 37–38 | Open Q&A + live troubleshooting |

The talk deliberately front-loads setup (slide 5) so the multi-minute BigQuery provisioning runs while the concepts are explained.

---

## 🔧 The two managed MCP servers used

| Server | Endpoint | Auth | Tools |
| :--- | :--- | :--- | :--- |
| **BigQuery MCP** | `https://bigquery.googleapis.com/mcp` | OAuth 2.0 bearer (from ADC) + `x-goog-user-project` | `list_dataset_ids`, `list_table_ids`, `get_dataset_info`, `get_table_info`, `execute_sql`, `execute_sql_readonly` |
| **Maps Grounding Lite** | `https://mapstools.googleapis.com/mcp` | API key in `X-Goog-Api-Key` header | `search_places`, `lookup_weather`, `compute_routes`, `resolve_names`, `resolve_maps_urls` |

> ⚠️ **Token lifetime:** the ADC OAuth token expires after ~60 minutes and ADK does not auto-refresh it. If the agent starts failing mid-lab, re-run `gcloud auth application-default login`.

---

## 🔁 Editing & Regenerating

All four artifacts are generated — do not edit the outputs by hand. Edit the `SLIDES_DATA` list in `generate_slides.py`, then:

```bash
pip install python-pptx pillow   # one-time (qrcode only needed to regenerate QR assets)
python3 generate_slides.py
```

This regenerates the `.pptx`, `index.html`, `speaker-notes.html`, and `SPEAKER_NOTES_AND_SCRIPT.md` together so they never drift. The `.pptx` is built on the Google Cloud Labs master layouts carried by the sibling `Command-and-Control-Gemini-MCP-Workshop` deck (used as the template via `REF_PPTX`).

---

## ⚠️ Before you present

1. **Credits QR is wired** — slide 3's middle card uses the real event link `g.dev/credits/latw-bigquery-100` (QR: `assets/qr_credits.png`). If you get a fresh code for a future event, regenerate the QR and re-run the generator.
2. **Do one full dry-run** of the codelab in a fresh project and record a backup video of the five prompts — live MCP + BigQuery + Cloud Shell has three separate failure surfaces.
3. The codelab's own architecture image labels the model "Gemini 3 Pro", but `agent.py` uses `gemini-3.5-flash`. Slide 18's speaker notes call this out if an attendee asks.
