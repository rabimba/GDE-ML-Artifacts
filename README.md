# GDE-ML-Artifacts

Hands-on workshops, notebooks, and demo artifacts for Google's Gemini & Gemma models — built for train-the-trainer sessions and GDE talks.

**Browse it as a website:** [rabimba.github.io/GDE-ML-Artifacts](https://rabimba.github.io/GDE-ML-Artifacts/)

## 🎤 Workshop Kits (75-min talk + hands-on lab)

| Workshop | Deck | Artifacts |
| :--- | :--- | :--- |
| **Location Intelligence ADK Agent** — MCP servers for BigQuery & Google Maps ([codelab](https://codelabs.developers.google.com/adk-mcp-bigquery-maps)) | [Interactive deck](https://rabimba.github.io/GDE-ML-Artifacts/Location-Intelligence-ADK-MCP-Workshop/) | [`Location-Intelligence-ADK-MCP-Workshop/`](Location-Intelligence-ADK-MCP-Workshop/) — PPTX, speaker console, facilitator runbook |
| **Command and Control** — orchestrate app development with Gemini & MCP ([codelab](https://codelabs.developers.google.com/gemini-mcp-agy)) | [Interactive deck](https://rabimba.github.io/GDE-ML-Artifacts/Command-and-Control-Gemini-MCP-Workshop/) | [`Command-and-Control-Gemini-MCP-Workshop/`](Command-and-Control-Gemini-MCP-Workshop/) — PPTX, speaker console, facilitator runbook |

Both decks are generated from a single `generate_slides.py` per folder — edit the `SLIDES_DATA` list and re-run to regenerate PPTX + HTML + notes together.

## 📓 Notebooks

Colab-ready (see the [landing page](https://rabimba.github.io/GDE-ML-Artifacts/) for descriptions): Gemma use cases, Gemma on Vertex AI, Gemma 3n multimodal feedback, Arxiv reader/Q&A, Gemini function calling & structured output, video/audio understanding, story writing.

## 🤖 Demo apps

- [`ADK/`](ADK/) — multi-agent trip planner (router + Sequential/Loop/Parallel workflows) with CLI and Streamlit frontends.
