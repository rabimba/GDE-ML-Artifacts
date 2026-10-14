#!/usr/bin/env python3
"""
Generator for "Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps"
75-min GDE talk + hands-on workshop based on codelab:
  https://codelabs.developers.google.com/adk-mcp-bigquery-maps
Builds:
1. Location_Intelligence_ADK_MCP_Workshop.pptx (editable, Google Cloud Labs master layouts, full speaker notes)
2. index.html (Interactive Web Presentation Deck: Presenter Console [P], Teleprompter [S], polls, lab timers)
3. speaker-notes.html (Standalone continuous-scroll Speaker Notes & Script)
4. SPEAKER_NOTES_AND_SCRIPT.md (Facilitator Runbook & Verbatim Speaker Script)
"""

import json
import os
import html
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# The Command-and-Control deck's output pptx doubles as our Google Cloud Labs
# master-layout template (CUSTOM_6_1_3_3_1, TITLE_AND_BODY_1, CUSTOM_6_1_3_2_1_1_4,
# CUSTOM_6_1_3_2_1_1_3_1_1_1_1_1_2_1). The original coffee_agent_slides.pptx lived
# on a Linux workstation and is not present on this machine.
REF_PPTX = os.path.join(
    os.path.dirname(BASE_DIR),
    "Command-and-Control-Gemini-MCP-Workshop",
    "Command_and_Control_Gemini_MCP_Workshop.pptx",
)

# ---------------------------------------------------------------------------
# COMPLETE 32-SLIDE DATA & VERBATIM SPEAKER NOTES
# ---------------------------------------------------------------------------
SLIDES_DATA = [
    # =====================================================================
    # MODULE 0 — WELCOME & ONBOARDING (00:00 – 00:06)
    # =====================================================================
    # SLIDE 1 — Cover
    {
        "num": 1,
        "module": "Module 0 • Welcome",
        "time": "00:00 – 00:02 (2 min)",
        "type": "cover",
        "title": "Build a Location Intelligence\nADK Agent with MCP servers\nfor BigQuery and Google Maps",
        "subtitle": "Hands-On Workshop • Ground a Gemini agent in enterprise data and the real world",
        "badge": "75-Min GDE Workshop",
        "notes": (
            "TIMING: 00:00 - 00:02 (2 mins)\n"
            "GOAL: High-energy welcome; name the payoff.\n\n"
            "SAY THIS:\n"
            "\"Welcome, everyone! Today we're going to build a Location Intelligence agent — an AI that answers a real business question: where should I open my bakery, and how much should I charge? It will do that by reasoning over enterprise data in BigQuery AND the real world in Google Maps, at the same time.\"\n\n"
            "\"The best part? You won't write any BigQuery or Maps API boilerplate. Two Google-managed MCP servers hand the agent its tools over a single open protocol. You'll build the whole thing yourself in this room.\""
        ),
    },
    # SLIDE 2 — What you'll build (demo GIF)
    {
        "num": 2,
        "module": "Module 0 • Welcome",
        "time": "00:02 – 00:03 (1 min)",
        "type": "hero_media",
        "title": "This is what you'll have running in about 40 minutes",
        "subtitle": "One Gemini agent • Two managed MCP servers • Zero hand-written API clients",
        "image": "adk_bq_maps_mcp.gif",
        "image_still": "adk_bq_maps_mcp_still.png",
        "caption": "Live demo: an ADK agent chains BigQuery SQL with Google Maps lookups (source: Google Cloud announcement, Dec 10 2025).",
        "notes": (
            "TIMING: 00:02 - 00:03 (1 min)\n"
            "GOAL: Hook — show the finished product before any explanation.\n\n"
            "SAY THIS:\n"
            "\"Before any slides: here is the exact agent you'll build. Watch the bottom — the user asks 'which zip code has the highest morning foot traffic', the agent writes SQL and runs it in BigQuery. Then 'is that area saturated with bakeries' — it switches to Google Maps and searches Places. One conversation, two totally different data worlds, joined by one agent.\"\n\n"
            "\"Keep this picture in your head. Every concept I explain for the next 20 minutes maps to something you just saw.\""
        ),
    },
    # SLIDE 3 — QR hub
    {
        "num": 3,
        "module": "Module 0 • Welcome",
        "time": "00:03 – 00:04 (1 min)",
        "type": "qr_hub",
        "title": "Workshop Hub — scan these now",
        "subtitle": "Everything you need is one QR away; the codelab has all commands and prompts",
        "cards": [
            {
                "title": "1. The Codelab (follow along)",
                "url_text": "codelabs.developers.google.com/adk-mcp-bigquery-maps",
                "url": "https://codelabs.developers.google.com/adk-mcp-bigquery-maps",
                "desc": "Full step-by-step lab: setup scripts, agent code, and every prompt we will run today.",
                "qr": "qr_codelab.png",
            },
            {
                "title": "2. Free Credits (redeem first!)",
                "url_text": "g.dev/credits/latw-bigquery-100",
                "url": "https://g.dev/credits/latw-bigquery-100",
                "desc": "Maps Grounding Lite and BigQuery need billing enabled. Redeem your event credit code, then create a project.",
                "qr": "qr_credits.png",
            },
            {
                "title": "3. Slides & Speaker Runbook",
                "url_text": "github.com/rabimba/GDE-ML-Artifacts",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts",
                "desc": "This deck, the verbatim facilitator script, and the copy-paste prompt sheet.",
                "qr": "qr_rabimba_github.png",
            },
        ],
        "notes": (
            "TIMING: 00:03 - 00:04 (1 min)\n"
            "ENGAGEMENT CUE: 'Phones out — scan the left QR for the codelab. That page has every command and every prompt, so you never have to type from the projector.'\n\n"
            "SAY THIS:\n"
            "\"Three links matter today. Left: the codelab — keep it open all session, it's your source of truth. Middle: your free Google Cloud credit — g.dev/credits/latw-bigquery-100 — redeem it now and create a project with billing on, because both services we use are pay-as-you-go. Right: my GitHub, where this deck and the full speaker script live if you want to rerun this workshop for your own GDG chapter.\""
        ),
    },
    # SLIDE 4 — Speaker
    {
        "num": 4,
        "module": "Module 0 • Welcome",
        "time": "00:04 – 00:05 (1 min)",
        "type": "speaker",
        "title": "Rabimba\nKaranjai",
        "subtitle": "Google Developer Expert (AI & ML)\nML Scientist - PayPal",
        "photo": "ref_slide4_pic2.jpg",
        "notes": (
            "TIMING: 00:04 - 00:05 (1 min)\n"
            "SAY THIS:\n"
            "\"Quick intro — I'm Rabimba Karanjai, a Google Developer Expert in AI/ML, and by day an ML Scientist at PayPal where I build and break agentic systems. This is a hands-on room: if something fails — and with live APIs something always hiccups — shout it out. Debugging together is part of the workshop.\""
        ),
    },
    # SLIDE 5 — Start your engines (parallel setup)
    {
        "num": 5,
        "module": "Module 0 • Welcome",
        "time": "00:05 – 00:06 (1 min)",
        "type": "stepper_split",
        "title": "Start your engines — setup runs while I talk",
        "callout_badge": "DO THIS NOW",
        "callout_title": "Provision in the background",
        "callout_body": "The two setup scripts take ~3-5 min. Kick them off now, then look up — I'll explain what everything is while your project provisions itself.",
        "steps": [
            ("1", "Open Cloud Shell", "console.cloud.google.com → Activate Cloud Shell (top bar)"),
            ("2", "Clone the demo repo", "git clone https://github.com/google/mcp.git"),
            ("3", "Run setup_env.sh", "cd mcp/examples/launchmybakery && ./setup/setup_env.sh"),
            ("4", "Run setup_bigquery.sh", "./setup/setup_bigquery.sh"),
        ],
        "code_title": "Cloud Shell",
        "code": (
            "# Verify auth + project\n"
            "gcloud auth list\n"
            "export PROJECT_ID=$(gcloud config get project)\n\n"
            "# Get the code\n"
            "git clone https://github.com/google/mcp.git\n"
            "cd mcp/examples/launchmybakery\n\n"
            "# Kick off BOTH setup scripts\n"
            "./setup/setup_env.sh\n"
            "./setup/setup_bigquery.sh"
        ),
        "notes": (
            "TIMING: 00:05 - 00:06 (1 min)\n"
            "GOAL: Fire-and-forget provisioning so nobody waits on BigQuery loads later.\n\n"
            "SAY THIS:\n"
            "\"Here's my favorite workshop trick: the slowest part of today is provisioning APIs and loading BigQuery tables — and it needs zero attention. So start it NOW, in the background. Activate Cloud Shell from the Cloud Console top bar, paste these commands, and let them run in a corner.\"\n\n"
            "\"While Google does the boring work, I'll spend 20 minutes explaining what an agent, ADK, and MCP actually are. When we come back to the terminal, everything will be green. Use the Copy button — don't type these by hand.\"\n\n"
            "FACILITATOR: Watch the room. If more than ~30% look lost at 'Activate Cloud Shell', pause 60 extra seconds here — it's the single biggest dropout point."
        ),
    },
    # =====================================================================
    # MODULE 1 — CONCEPTS (00:06 – 00:25)
    # =====================================================================
    # SLIDE 6 — Poll: the problem
    {
        "num": 6,
        "module": "Module 1 • Concepts",
        "time": "00:06 – 00:08 (2 min)",
        "type": "section_poll",
        "icon": "icon_maps.png",
        "title": "Your friend is opening a sourdough\nbakery in Los Angeles. Where?",
        "poll": {
            "question": "🎤 Quick poll: how would you actually decide which LA zip code to open in?",
            "options": [
                "A) Walk around and 'get a feel' for neighborhoods",
                "B) Hire a market-research firm ($$$, weeks)",
                "C) Ask an LLM chatbot for the 'best' zip code",
                "D) Combine real foot-traffic data with live Maps info",
            ],
            "answer": "C alone hallucinates — a model can't know current foot traffic or which bakeries exist. The winning move is D: data + the real world, joined by an agent. Today we build exactly that.",
        },
        "notes": (
            "TIMING: 00:06 - 00:08 (2 mins)\n"
            "GOAL: Frame the business problem; let the audience discover why a bare LLM fails.\n\n"
            "SAY THIS:\n"
            "\"A friend wants to open a high-end sourdough bakery in LA. Wrong zip code = bankruptcy. So — how do you pick? Show of hands for A... B... C? Someone always says 'just ask ChatGPT.' Here's the trap: a language model has no idea what foot traffic looks like in 90403 this morning, or that three new bakeries opened there last month. It will confidently invent an answer. That's not intelligence, that's a hallucination with a business plan.\"\n\n"
            "\"Click D on screen. Real foot-traffic data lives in a database. Real competitors live on a map. Today's agent queries BOTH, then reasons over the combined evidence.\""
        ),
    },
    # SLIDE 7 — Two worlds (split)
    {
        "num": 7,
        "module": "Module 1 • Concepts",
        "time": "00:08 – 00:09 (1 min)",
        "type": "split_worlds",
        "title": "Two data worlds, one question",
        "left": {
            "icon": "icon_bigquery.png",
            "heading": "Enterprise Data — BigQuery",
            "color": "blue",
            "points": [
                "Demographics & foot-traffic index by zip",
                "Competitor product pricing",
                "Weekly sales history per store",
                "Your private, governed numbers",
            ],
        },
        "right": {
            "icon": "icon_maps.png",
            "heading": "The Real World — Google Maps",
            "color": "green",
            "points": [
                "Which bakeries actually exist nearby?",
                "Drive time to the supplier",
                "Weather for opening weekend",
                "Fresh, public, geospatial truth",
            ],
        },
        "bridge": "An agent must reason across BOTH to answer 'where should I open?'",
        "notes": (
            "TIMING: 00:08 - 00:09 (1 min)\n"
            "SAY THIS:\n"
            "\"Look at the two columns. On the left, the private numbers every business guards: census demographics, what competitors charge for a loaf, your own sales history. That lives in BigQuery. On the right, public real-world facts that change daily: is there already a bakery on that block, how long is the drive to Restaurant Depot, will it rain on opening day. That lives in Google Maps.\"\n\n"
            "\"No single system answers both. The whole point of today is the bridge at the bottom — one agent that treats both as just... tools.\""
        ),
    },
    # SLIDE 8 — What is an agent (build)
    {
        "num": 8,
        "module": "Module 1 • Concepts",
        "time": "00:09 – 00:11 (2 min)",
        "type": "diagram_build",
        "title": "What makes an LLM an Agent?",
        "subtitle": "Build the definition up piece by piece — press → to reveal each part",
        "build_steps": [
            {"label": "1. MODEL", "desc": "Gemini 3.5 Flash — the reasoning brain. Alone, it only predicts text.", "icon": "icon_gemini.png"},
            {"label": "2. + INSTRUCTIONS", "desc": "A system prompt that defines the goal, persona, and rules of the game.", "icon": "icon_adk.png"},
            {"label": "3. + TOOLS", "desc": "Functions the model may call to act on the world — query BigQuery, search Maps.", "icon": "icon_mcp.png"},
            {"label": "4. + LOOP", "desc": "Reason → pick a tool → act → observe result → reason again, until the goal is met.", "icon": "icon_gemini.png"},
        ],
        "summary": "Agent = Model + Instructions + Tools, running in a Reason-Act-Observe loop",
        "notes": (
            "TIMING: 00:09 - 00:11 (2 mins)\n"
            "GOAL: Demystify 'agent' in four reveals. In the web deck each press of → reveals the next block.\n\n"
            "SAY THIS (per reveal):\n"
            "\"First: a model. Gemini 3.5 Flash — a brain that predicts text. Powerful, but it can only talk. [→] Give it instructions — a job description: 'you are a location-intelligence analyst; combine BigQuery and Maps.' [→] Give it tools — actual capabilities: run SQL, search places, compute a route. [→] And wrap it in a loop: the model reasons about what to do, calls a tool, observes the result, and reasons again.\"\n\n"
            "\"That loop is the whole magic trick. An agent isn't a bigger model — it's a model with hands and a while-loop.\""
        ),
    },
    # SLIDE 9 — The stack (three tech)
    {
        "num": 9,
        "module": "Module 1 • Concepts",
        "time": "00:11 – 00:12 (1 min)",
        "type": "three_tech",
        "title": "The three pillars we'll use today",
        "cols": [
            {
                "icon": "icon_gemini.png",
                "title": "Gemini 3.5 Flash\n(on Vertex AI)",
                "body": "The reasoning model. Our .env sets GOOGLE_GENAI_USE_VERTEXAI=1, so ADK calls it through your project's Vertex AI endpoint.",
            },
            {
                "icon": "icon_adk.png",
                "title": "ADK\nAgent Development Kit",
                "body": "Google's open-source framework for building agents: LlmAgent, tool wiring, sessions, and a built-in web UI for debugging.",
            },
            {
                "icon": "icon_mcp.png",
                "title": "MCP\nModel Context Protocol",
                "body": "The open standard (started by Anthropic) that lets any agent discover and call tools on any server — one protocol instead of N custom integrations.",
            },
        ],
        "notes": (
            "TIMING: 00:11 - 00:12 (1 min)\n"
            "SAY THIS:\n"
            "\"Three pillars. Gemini 3.5 Flash is the brain — we run it on Vertex AI so it's authenticated and billed through your Cloud project, which that setup script already switched on. ADK is the framework — you describe the agent in a few lines of Python and it handles the loop, tool dispatch, and a debug UI. And MCP is the connective tissue — the open protocol that lets ADK talk to BigQuery and Maps without us writing a single API wrapper. Next three slides take each in turn.\""
        ),
    },
    # SLIDE 10 — ADK anatomy (code focus)
    {
        "num": 10,
        "module": "Module 1 • Concepts",
        "time": "00:12 – 00:13 (1 min)",
        "type": "code_focus",
        "title": "An ADK agent in ~15 lines",
        "subtitle": "adk_agent/mcp_bakery_app/agent.py — the entire agent definition",
        "lang": "python",
        "code": (
            "root_agent = LlmAgent(\n"
            "    model='gemini-3.5-flash',\n"
            "    name='root_agent',\n"
            "    instruction=f\"\"\"Help the user by strategically combining:\n"
            "        1. BigQuery toolset — demographics, foot traffic,\n"
            "           pricing and sales in the `mcp_bakery` dataset.\n"
            "           Run all query jobs from project id: {PROJECT_ID}.\n"
            "        2. Maps Toolset — real-world location analysis,\n"
            "           competition search, and travel routes.\n"
            "           Include a hyperlink to an interactive map.\n"
            "    \"\"\",\n"
            "    tools=[maps_toolset, bigquery_toolset]\n"
            ")"
        ),
        "callouts": [
            ("model", "Which Gemini does the thinking"),
            ("instruction", "The agent's job description — notice it scopes the data AND names the project"),
            ("tools", "Two MCP toolsets = every tool from both servers"),
        ],
        "notes": (
            "TIMING: 00:12 - 00:13 (1 min)\n"
            "SAY THIS:\n"
            "\"This is genuinely the whole agent — about fifteen lines. An LlmAgent needs three things: a model, an instruction, and tools. Read the instruction like a job description: it tells the agent which dataset it's allowed to touch — mcp_bakery and nothing else — which project to bill queries to, and to always include a Maps link when it talks about places.\"\n\n"
            "\"The instruction is your strongest control surface. In the bonus section you'll edit it live and watch the agent's behavior change.\""
        ),
    },
    # SLIDE 11 — MCP: why (N x M -> N + M)
    {
        "num": 11,
        "module": "Module 1 • Concepts",
        "time": "00:13 – 00:15 (2 min)",
        "type": "nxm",
        "title": "MCP: from N×M integrations to N+M",
        "subtitle": "The 'USB-C for AI' — Anthropic's open standard, adopted across the industry",
        "left_caption": "Without MCP: every agent hand-codes every API",
        "right_caption": "With MCP: each side implements the protocol once",
        "agents": ["ADK Agent", "Gemini CLI", "Any MCP client"],
        "servers": ["BigQuery", "Google Maps", "Your API?"],
        "notes": (
            "TIMING: 00:13 - 00:15 (2 mins)\n"
            "GOAL: The 'why' of MCP — the integration math.\n\n"
            "SAY THIS:\n"
            "\"Before MCP, wiring an agent to a data source meant a bespoke adapter: read the API docs, hand-write a client, hand-write the tool schema, pray about auth. Three agents times three data sources is nine brittle adapters.\"\n\n"
            "\"MCP flips that. It's an open protocol — Anthropic created it, and it's now industry-wide, with Google as a founding member of the Agentic AI Foundation. A server exposes its capabilities as standard 'tools'; any MCP client discovers and calls them. Write the server once, write the client once, and N-plus-M replaces N-times-M. People call it 'USB-C for AI' and the analogy is exact: one connector, any device.\"\n\n"
            "KEY VOCAB on this slide: Host = the app the user talks to (ADK web UI). Client = the connection inside the host. Server = the thing exposing tools (BigQuery, Maps)."
        ),
    },
    # SLIDE 12 — MCP roles & transport (build)
    {
        "num": 12,
        "module": "Module 1 • Concepts",
        "time": "00:15 – 00:16 (1 min)",
        "type": "diagram_build",
        "title": "MCP anatomy: Host, Client, Server",
        "subtitle": "And the transport that carries it — today that's Streamable HTTP",
        "build_steps": [
            {"label": "HOST", "desc": "ADK's web UI — the app the user chats with.", "icon": "icon_adk.png"},
            {"label": "CLIENT", "desc": "An MCP client inside the host keeps a dedicated connection per server.", "icon": "icon_mcp.png"},
            {"label": "SERVER", "desc": "BigQuery & Maps servers expose a catalog of named, typed tools.", "icon": "icon_bigquery.png"},
            {"label": "TRANSPORT", "desc": "Stdio for local servers; Streamable HTTP for remote, Google-hosted ones — what we use today.", "icon": "icon_maps.png"},
        ],
        "summary": "Our agent never runs BigQuery or Maps code — it calls remote tools over HTTP",
        "notes": (
            "TIMING: 00:15 - 00:16 (1 min)\n"
            "SAY THIS:\n"
            "\"Three roles. The Host is the app you talk to — ADK's web UI. Inside it, a Client maintains one dedicated connection per server. The Server is where the tools live. And the transport is how bytes move: stdio for a server running as a subprocess on your laptop, or Streamable HTTP for a remote server.\"\n\n"
            "\"Today both our servers are remote and Google-hosted, so it's Streamable HTTP with an auth header. That's why you don't install BigQuery or Maps SDKs at all — you saw the repo: no BigQuery client code, no Places client code. Just two URLs.\""
        ),
    },
    # SLIDE 13 — Google-managed remote MCP servers (arch)
    {
        "num": 13,
        "module": "Module 1 • Concepts",
        "time": "00:16 – 00:18 (2 min)",
        "type": "arch_split",
        "title": "Google's managed, remote MCP servers",
        "subtitle": "Announced Dec 10, 2025 — Google's API infrastructure now speaks MCP",
        "intro": "No local servers to install, patch, or secure. You point your client at a globally-consistent endpoint.",
        "bullets": [
            ("BigQuery", "https://bigquery.googleapis.com/mcp"),
            ("Google Maps (Grounding Lite)", "https://mapstools.googleapis.com/mcp"),
            ("Also GA/Preview", "GCE, GKE, Spanner, AlloyDB, Cloud Run, Developer Knowledge..."),
            ("Enable per project", "gcloud beta services mcp enable <service> (setup_env.sh did this)"),
            ("Governance", "IAM (roles/mcp.toolUser), audit logging, Model Armor for prompt-injection defense"),
        ],
        "image": "repo_architecture.png",
        "notes": (
            "TIMING: 00:16 - 00:18 (2 mins)\n"
            "GOAL: Position Google's managed servers as the enterprise-ready path.\n\n"
            "SAY THIS:\n"
            "\"Last December, Google announced that its API infrastructure itself now speaks MCP. Instead of installing some community server and babysitting it, you point at a managed endpoint: bigquery.googleapis.com/mcp, mapstools.googleapis.com/mcp. Same URL everywhere on Earth.\"\n\n"
            "\"Two things to notice. First, MCP is opt-in per project — that's why setup_env.sh ran 'gcloud beta services mcp enable' for both services. Second, it's governed like the rest of Google Cloud: there's a dedicated IAM role — roles/mcp.toolUser — every tool call lands in audit logs, and Model Armor can screen for prompt injection. That governance story is exactly why enterprises can actually deploy this.\""
        ),
    },
    # SLIDE 14 — BigQuery MCP tool catalog
    {
        "num": 14,
        "module": "Module 1 • Concepts",
        "time": "00:18 – 00:19 (1 min)",
        "type": "tool_catalog",
        "title": "BigQuery MCP server — the 6 tools",
        "subtitle": "The agent discovers these itself; column descriptions become its documentation",
        "accent": "blue",
        "icon": "icon_bigquery.png",
        "tools": [
            ("list_dataset_ids", "What datasets exist in this project?"),
            ("list_table_ids", "What tables are in mcp_bakery?"),
            ("get_dataset_info", "Metadata about a dataset"),
            ("get_table_info", "Schema + column descriptions for a table"),
            ("execute_sql", "Run any SQL — including AI.FORECAST"),
            ("execute_sql_readonly", "Same, but mutations blocked by design"),
        ],
        "callout": "The agent reads get_table_info output to write its own SQL. Rich column descriptions in setup_bigquery.sh = a better agent. Your schema docs ARE the prompt.",
        "notes": (
            "TIMING: 00:18 - 00:19 (1 min)\n"
            "SAY THIS:\n"
            "\"What can the agent actually do in BigQuery? Six tools. It can list datasets, list tables, and read metadata — and then the two interesting ones: execute_sql runs arbitrary SQL, and execute_sql_readonly does the same with mutations blocked. Because it's full SQL, the agent can even call BigQuery's AI.FORECAST function — that's how it does the revenue projection you'll see later.\"\n\n"
            "\"Here's the subtle part — watch get_table_info. When the agent needs to write SQL, it first asks the server for the table schema, and the server returns the column descriptions that the setup script wrote: 'foot_traffic_index — index of estimated foot traffic based on commercial density.' The agent uses that text to decide which column to query. So your schema documentation literally becomes part of the prompt. Good descriptions, smarter agent.\""
        ),
    },
    # SLIDE 15 — Maps Grounding Lite tool catalog
    {
        "num": 15,
        "module": "Module 1 • Concepts",
        "time": "00:19 – 00:20 (1 min)",
        "type": "tool_catalog",
        "title": "Maps Grounding Lite — the 5 tools",
        "subtitle": "Trusted geospatial grounding with required Google Maps attribution",
        "accent": "green",
        "icon": "icon_maps.png",
        "tools": [
            ("search_places", "Find places + AI summaries + Maps links"),
            ("compute_routes", "Distance & duration between two points"),
            ("lookup_weather", "Current conditions & forecasts"),
            ("resolve_names", "Free-text address/place -> Place ID"),
            ("resolve_maps_urls", "Google Maps URL -> Place ID"),
        ],
        "callout": "Grounding Lite returns distance & duration — NOT turn-by-turn directions. Every grounded answer must show its Google Maps source link (the agent is instructed to include it).",
        "notes": (
            "TIMING: 00:19 - 00:20 (1 min)\n"
            "SAY THIS:\n"
            "\"The Maps side is called Grounding Lite — an MCP server over Google's geospatial data. Five tools. search_places finds businesses and returns an AI summary plus a Maps link for each. compute_routes gives distance and drive time — note, deliberately not turn-by-turn navigation. lookup_weather does what it says. And the two resolve tools turn fuzzy text — 'a bakery near the pier' — into stable Place IDs you can feed to other Maps APIs.\"\n\n"
            "\"One rule matters: attribution. When the agent's answer is grounded in Maps, the Google Maps source link must be shown. Remember our agent instruction said 'include a hyperlink to an interactive map'? That line is doing attribution compliance.\""
        ),
    },
    # SLIDE 16 — Two auth patterns (code split, tools.py)
    {
        "num": 16,
        "module": "Module 1 • Concepts",
        "time": "00:20 – 00:21 (1 min)",
        "type": "code_split",
        "title": "Two servers, two auth patterns — tools.py",
        "subtitle": "Same MCPToolset, different credentials",
        "intro": "Both toolsets use StreamableHTTPConnectionParams; only the header differs.",
        "bullets": [
            ("Maps", "Simple API key in the X-Goog-Api-Key header (restricted to mapstools.googleapis.com)."),
            ("BigQuery", "OAuth 2.0 bearer token from your Application Default Credentials + x-goog-user-project for billing."),
            ("⚠️ Token lifetime", "ADC tokens expire ~60 min and ADK does not auto-refresh — re-run gcloud auth application-default login if a long session dies."),
        ],
        "code_title": "adk_agent/mcp_bakery_app/tools.py",
        "code": (
            "# --- Maps: API key ---\n"
            "MCPToolset(connection_params=\n"
            "  StreamableHTTPConnectionParams(\n"
            "    url='https://mapstools.googleapis.com/mcp',\n"
            "    headers={'X-Goog-Api-Key': maps_api_key}))\n\n"
            "# --- BigQuery: OAuth bearer (from ADC) ---\n"
            "creds, pid = google.auth.default(scopes=[BQ_SCOPE])\n"
            "creds.refresh(Request())\n"
            "MCPToolset(connection_params=\n"
            "  StreamableHTTPConnectionParams(\n"
            "    url='https://bigquery.googleapis.com/mcp',\n"
            "    headers={'Authorization': f'Bearer {creds.token}',\n"
            "             'x-goog-user-project': pid}))"
        ),
        "notes": (
            "TIMING: 00:20 - 00:21 (1 min)\n"
            "SAY THIS:\n"
            "\"Open tools.py and it's almost disappointingly simple — two functions, same pattern. Maps takes an API key in a header; the setup script created a restricted key that only works for the maps tools service. BigQuery is stricter: it's your enterprise data, so it wants OAuth. We pull a token from your Application Default Credentials and pass it as a Bearer header, plus x-goog-user-project so queries bill to your project.\"\n\n"
            "\"Now the one operational gotcha of the whole day — star this. That OAuth token lives about 60 minutes, and ADK does not refresh it for you. If your agent suddenly starts failing late in the workshop, re-run gcloud auth application-default login. Write it down.\""
        ),
    },
    # SLIDE 17 — Macro -> micro journey (storyboard)
    {
        "num": 17,
        "module": "Module 1 • Concepts",
        "time": "00:21 – 00:23 (2 min)",
        "type": "journey_storyboard",
        "title": "The reasoning journey: macro → micro → money",
        "subtitle": "Watch how one conversation walks down the decision funnel, switching tools",
        "steps": [
            ("Q1", "Which zip has the highest morning foot traffic?", "BigQuery • execute_sql", "→ 90403 (Santa Monica)", "blue"),
            ("Q2", "Is 90403 already saturated with bakeries?", "Maps • search_places", "→ competitor scan", "green"),
            ("Q3", "Max price of a Sourdough Loaf in LA Metro?", "BigQuery • execute_sql", "→ Erewhon ≈ $18.50", "blue"),
            ("Q4", "Forecast Dec sales from my best store @ $18", "BigQuery • AI.FORECAST", "→ revenue projection", "blue"),
            ("Q5", "Is Restaurant Depot < 30 min away?", "Maps • compute_routes", "→ logistics check", "green"),
        ],
        "notes": (
            "TIMING: 00:21 - 00:23 (2 mins)\n"
            "GOAL: The narrative spine of the whole workshop — memorize this funnel.\n\n"
            "SAY THIS:\n"
            "\"Here's the entire workshop as five questions. Notice the rhythm — it zooms from the whole city down to a loading dock. Question one is MACRO: across all of LA, where's the morning foot traffic? That's a BigQuery aggregate — the agent writes SQL, scans the foot_traffic table, and lands on zip 90403, Santa Monica. Question two goes MICRO: is that zip already crawling with bakeries? No database knows that — that's a live Maps search. Three: pricing — back to BigQuery, max price for a sourdough loaf, and Erewhon tops out around $18.50. Four: money — forecast December revenue off your best store using BigQuery's AI.FORECAST. Five: logistics — a compute_routes call to confirm the supplier run is under 30 minutes.\"\n\n"
            "\"Blue rows are BigQuery, green rows are Maps. The agent is choosing the right tool for each question with no router, no if-statements — the instruction plus the model's reasoning does it.\""
        ),
    },
    # SLIDE 18 — Full architecture (codelab diagram)
    {
        "num": 18,
        "module": "Module 1 • Concepts",
        "time": "00:23 – 00:24 (1 min)",
        "type": "arch_split",
        "title": "The full architecture",
        "subtitle": "Everything on one slide — this is your 'you are here' map for the lab",
        "intro": "Trace one request end to end:",
        "bullets": [
            ("1. User", "asks in the ADK web UI (adk web)"),
            ("2. Agent (Gemini 3.5 Flash)", "reasons on Vertex AI, picks a tool"),
            ("3. MCP toolset", "sends a signed Streamable HTTP call"),
            ("4a. BigQuery MCP", "interprets schema & runs SQL in place — data never leaves BigQuery"),
            ("4b. Maps MCP", "grounds in live places, routes, weather"),
            ("5. Agent", "combines both into one grounded business answer"),
        ],
        "image": "codelab_architecture.png",
        "notes": (
            "TIMING: 00:23 - 00:24 (1 min)\n"
            "SAY THIS:\n"
            "\"Everything we just covered, one diagram. User talks to the ADK web UI. The agent — Gemini 3.5 Flash on Vertex AI — reads the question and the instruction, decides it needs data, and the MCPToolset fires a signed HTTP call. BigQuery interprets the schema and runs SQL where the data lives — the rows never get shipped into the model, only the answer does. Maps grounds the same conversation in live places and routes. Then the agent fuses both into one answer.\"\n\n"
            "\"Screenshot this slide. In the lab, whenever you're lost, find yourself on this map.\"\n\n"
            "NOTE: This codelab diagram says 'Gemini 3 Pro' — the actual code uses gemini-3.5-flash. If a sharp attendee asks, confirm: model ID is set in agent.py and swappable."
        ),
    },
    # SLIDE 19 — Quiz
    {
        "num": 19,
        "module": "Module 1 • Concepts",
        "time": "00:24 – 00:25 (1 min)",
        "type": "two_cards_quiz",
        "left_card": {
            "color": "blue",
            "title": "Concept Check",
            "subtitle": "Click to reveal each answer",
            "items": [
                ("Q1", "Agent needs today's weather at the site?"),
                ("Q2", "Agent must forecast December revenue?"),
                ("Q3", "Agent must list tables before writing SQL?"),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Why not just…?",
            "subtitle": "Common objections",
            "items": [
                ("Paste CSVs into the prompt?", "40k+ rows won't fit, goes stale, and leaves governance."),
                ("Call Maps with curl?", "You'd hand-write auth, parsing & schemas — MCP already did it."),
                ("Fine-tune on my data?", "Teaches style, not fresh facts. Tools > training for live data."),
            ],
        },
        "quiz": {
            "question": "🎯 Answers: Q1 → Maps lookup_weather  •  Q2 → BigQuery execute_sql + AI.FORECAST  •  Q3 → BigQuery list_table_ids / get_table_info",
            "answer": "Rule of thumb: facts that live in your warehouse → BigQuery tool. Facts about the physical world right now → Maps tool. The agent learns the tools exist from the toolsets, not from you hard-coding the path.",
        },
        "notes": (
            "TIMING: 00:24 - 00:25 (1 min)\n"
            "GOAL: Lock in tool selection intuition before hands-on.\n\n"
            "SAY THIS:\n"
            "\"Sixty-second check. Weather at the site? Maps lookup_weather. December revenue forecast? BigQuery execute_sql calling AI.FORECAST. How does the agent know what columns exist? It calls list_table_ids and get_table_info first.\"\n\n"
            "\"And the right column kills the three things people always try instead: pasting CSVs into the prompt — stale and ungoverned; curling the Maps API — you're back to hand-rolled auth and parsing; fine-tuning — which teaches a model style, not today's facts. When in doubt: warehouse facts, BigQuery; real-world right-now, Maps.\""
        ),
    },
    # SLIDE 20 — Production guardrails
    {
        "num": 20,
        "module": "Module 1 • Concepts",
        "time": "00:25 – 00:26 (1 min)",
        "type": "objectives_card",
        "title": "Taking this to production — the guardrails that matter",
        "intro": "The demo uses your personal credentials for speed. Before this pattern ships, layer on:",
        "bullets": [
            ("Least privilege", "grant only roles/mcp.toolUser + bigquery.jobUser + bigquery.dataViewer; nothing broader"),
            ("Separate agent identity", "run the agent as its own service account so tool calls are attributable & revocable"),
            ("Prefer read-only SQL", "use execute_sql_readonly, or an IAM deny policy on execute_sql, so the agent can't mutate"),
            ("Restrict the Maps key", "scope it to mapstools.googleapis.com only (setup_env.sh already did)"),
            ("Defend the prompt", "Model Armor screens tool output for indirect prompt injection"),
            ("Watch the logs", "every MCP tool call lands in Cloud Audit Logs — alert on anomalies"),
        ],
        "notes": (
            "TIMING: 00:25 - 00:26 (1 min)\n"
            "GOAL: Bridge from toy to enterprise; this is what makes it 'GDE-grade'.\n\n"
            "SAY THIS:\n"
            "\"Quick reality check — today we use YOUR credentials because it's fast. In production you tighten it: grant only the three least-privilege roles; give the agent its own service account so every call is attributable; prefer execute_sql_readonly — or a deny policy on execute_sql — so the agent physically cannot DROP a table; keep the Maps key restricted to one service; put Model Armor in front of tool output so a poisoned web result can't hijack the agent; and alert on the audit logs. That's the list a security team will ask about — now you have answers.\"\n\n"
            "With that — enough theory. Let's build it."
        ),
    },
    # =====================================================================
    # MODULE 2 — LAB A: SETUP (00:26 – 00:38)
    # =====================================================================
    # SLIDE 21 — Lab divider
    {
        "num": 21,
        "module": "Module 2 • Lab A: Setup",
        "time": "00:26 – 00:27 (1 min)",
        "type": "lab_divider",
        "title": "Let's build this!",
        "subtitle": "Part A: finish provisioning • Part B: run the agent • Part C: the full journey",
        "notes": (
            "TIMING: 00:26 - 00:27 (1 min)\n"
            "GOAL: Shift the room from listening to doing.\n\n"
            "SAY THIS:\n"
            "\"Concepts done. From here it's all hands-on — three parts. Part A, we finish setup and verify the data landed. Part B, we boot the agent and say hello. Part C, the fun part: the full five-question business journey. If you started the scripts at the beginning, you're already ahead. Let's check on them.\"\n\n"
            "FACILITATOR: From this point, keep the codelab page open on the projector when not on a slide — attendees should mirror you."
        ),
    },
    # SLIDE 22 — Catch-up: project + auth
    {
        "num": 22,
        "module": "Module 2 • Lab A: Setup",
        "time": "00:27 – 00:29 (2 min)",
        "type": "code_split",
        "title": "Step 1: Project, auth & the code",
        "subtitle": "If you did the 'engines' step, just verify — else run it now",
        "intro": "Confirm you're authenticated and the repo is cloned.",
        "bullets": [
            ("gcloud auth list", "must show your account as ACTIVE"),
            ("export PROJECT_ID=$(gcloud config get project)", "every later script reads this"),
            ("gcloud auth application-default login", "creates the ADC the BigQuery MCP toolset needs"),
            ("⚠️ Billing", "Maps Grounding Lite & BigQuery both require billing — redeem your credit first"),
        ],
        "code_title": "Cloud Shell",
        "code": (
            "gcloud auth list\n"
            "gcloud config get project\n"
            "export PROJECT_ID=$(gcloud config get project)\n\n"
            "git clone https://github.com/google/mcp.git\n"
            "cd mcp/examples/launchmybakery\n\n"
            "# Required so ADK can call BigQuery via MCP\n"
            "gcloud auth application-default login"
        ),
        "screenshot": "codelab_activate_cloudshell.png",
        "notes": (
            "TIMING: 00:27 - 00:29 (2 mins)\n"
            "GOAL: Everyone authenticated with ADC set.\n\n"
            "SAY THIS:\n"
            "\"Step one. Three checks. gcloud auth list — your account should say ACTIVE. Then export PROJECT_ID so every later command knows your project. And the important one: gcloud auth application-default login. That creates Application Default Credentials on this machine — remember, the BigQuery toolset turns that into the OAuth bearer token. Skip this and the agent fails at query time, not at startup, which confuses everyone.\"\n\n"
            "WALK THE ROOM: the #1 failure here is people not having billing enabled because they skipped the credit redemption. Ask for a show of hands: 'Who sees their account as ACTIVE?'"
        ),
    },
    # SLIDE 23 — What the setup scripts do (diagram)
    {
        "num": 23,
        "module": "Module 2 • Lab A: Setup",
        "time": "00:29 – 00:31 (2 min)",
        "type": "diagram_build",
        "title": "What those two setup scripts just did",
        "subtitle": "Press → to walk through the provisioning you kicked off at minute 5",
        "build_steps": [
            {"label": "setup_env.sh • 1", "desc": "Enables APIs: aiplatform, apikeys, mapstools, bigquery — plus the MCP endpoints (gcloud beta services mcp enable).", "icon": "icon_gemini.png"},
            {"label": "setup_env.sh • 2", "desc": "Creates a Maps API key restricted to mapstools.googleapis.com and writes .env (VERTEXAI flag, project, key).", "icon": "icon_maps.png"},
            {"label": "setup_bigquery.sh • 1", "desc": "Creates a Cloud Storage bucket and uploads the 4 CSVs (demographics, prices, sales, foot traffic).", "icon": "icon_bigquery.png"},
            {"label": "setup_bigquery.sh • 2", "desc": "Creates dataset mcp_bakery and 4 tables — each column carrying a description the agent will read.", "icon": "icon_bigquery.png"},
        ],
        "summary": "Result: a governed dataset + a restricted key + MCP endpoints switched on",
        "notes": (
            "TIMING: 00:29 - 00:31 (2 mins)\n"
            "GOAL: Convert 'magic scripts' into understood infrastructure.\n\n"
            "SAY THIS:\n"
            "\"So what did you actually run? setup_env.sh did two things — it enabled the four APIs, AND it flipped on the MCP endpoints themselves with gcloud beta services mcp enable; remember, MCP is opt-in. Then it minted a Maps API key locked to just the maps-tools service and dropped your .env. setup_bigquery.sh staged the four CSVs into a bucket, then created the mcp_bakery dataset with four tables. And here's that detail again: every column got an OPTIONS description. Those descriptions are what get_table_info will feed the agent so it can write sensible SQL.\"\n\n"
            "CHECK: 'Everyone whose scripts finished — green check in chat / hand up. Still running? Fine, keep going, it'll catch up.'"
        ),
    },
    # SLIDE 24 — Checkpoint 1: verify dataset
    {
        "num": 24,
        "module": "Module 2 • Lab A: Setup",
        "time": "00:31 – 00:33 (2 min)",
        "type": "checkpoint_visual",
        "title": "✋ Checkpoint 1: Your data is live",
        "timer_seconds": 180,
        "bullets": [
            ("Open", "the BigQuery console in your project"),
            ("Confirm", "dataset mcp_bakery exists with 4 tables"),
            ("Peek", "at foot_traffic → notice the morning score column"),
            ("Stuck?", "re-run ./setup/setup_bigquery.sh; check PROJECT_ID is set"),
        ],
        "screenshot": "codelab_bigquery_console.jpeg",
        "caption": "BigQuery console: mcp_bakery dataset with its 4 tables",
        "notes": (
            "TIMING: 00:31 - 00:33 (2 mins) — START THE 3-MIN LAB TIMER.\n"
            "GOAL: First tangible win; everyone sees their own data.\n\n"
            "SAY THIS:\n"
            "\"First checkpoint — make it real. Open the BigQuery console. You should see a dataset called mcp_bakery with four tables: demographics, bakery_prices, sales_history_weekly, foot_traffic. Click into foot_traffic and find the morning score column — that's the exact column the agent is about to query for question one.\"\n\n"
            "\"If mcp_bakery isn't there, nine times out of ten the PROJECT_ID export didn't stick — echo it, re-run the script. Hands up when you see the four tables!\""
        ),
    },
    # SLIDE 25 — Install ADK
    {
        "num": 25,
        "module": "Module 2 • Lab A: Setup",
        "time": "00:33 – 00:36 (3 min)",
        "type": "code_split",
        "title": "Step 2: Install ADK in a virtualenv",
        "subtitle": "google-adk[mcp] — the [mcp] extra brings the MCP client",
        "intro": "Isolate the install, then install ADK with MCP support.",
        "bullets": [
            ("python3 -m venv .venv", "keep Cloud Shell's system Python clean"),
            ("pip install \"google-adk[mcp]\"", "the extra pulls in the MCP client libraries"),
            ("Trouble?", "the repo pins a known-good: pip install google-adk==1.28.0"),
            ("Then", "cd adk_agent/ — adk web discovers apps under the CWD"),
        ],
        "code_title": "Cloud Shell",
        "code": (
            "python3 -m venv .venv\n"
            "source .venv/bin/activate\n\n"
            "# The [mcp] extra = MCP client support\n"
            "pip install \"google-adk[mcp]\"\n\n"
            "# adk web scans the current dir for agents\n"
            "cd adk_agent/"
        ),
        "notes": (
            "TIMING: 00:33 - 00:36 (3 mins)\n"
            "SAY THIS:\n"
            "\"Install time. Make a virtualenv — Cloud Shell's system Python is shared, don't pollute it. Then pip install quote google-adk bracket mcp unquote. That little [mcp] extra is what brings the MCP client; without it MCPToolset import fails. If the resolver gives you grief, the repo pins google-adk==1.28.0 as a known-good.\"\n\n"
            "\"Then cd into adk_agent. Important: adk web discovers agent apps by scanning the CURRENT directory, so where you run it from matters. If the UI later shows an empty dropdown, you're in the wrong folder.\""
        ),
    },
    # =====================================================================
    # MODULE 3 — LAB B: RUN THE AGENT (00:36 – 00:50)
    # =====================================================================
    # SLIDE 26 — Inspect the code
    {
        "num": 26,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:36 – 00:38 (2 min)",
        "type": "checkpoint_visual",
        "title": "Step 3: Read the agent you'll run",
        "bullets": [
            ("Open Editor", "in Cloud Shell, browse mcp/examples/launchmybakery"),
            ("agent.py", "find the LlmAgent — model, instruction, tools"),
            ("tools.py", "find the two MCPToolset calls & their headers"),
            (".env", "confirm GOOGLE_GENAI_USE_VERTEXAI=1 and MAPS_API_KEY are set"),
        ],
        "screenshot": "codelab_open_editor.png",
        "caption": "Cloud Shell Editor showing the launchmybakery layout",
        "notes": (
            "TIMING: 00:36 - 00:38 (2 mins)\n"
            "GOAL: Connect the concept slides to real files before running.\n\n"
            "SAY THIS:\n"
            "\"Before we run anything, open it. Click 'Open Editor' in Cloud Shell and navigate into launchmybakery. Open agent.py — there's the LlmAgent from slide 10, word for word. Open tools.py — there's the API-key header and the OAuth header from slide 16. And check .env: you should see GOOGLE_GENAI_USE_VERTEXAI=1 and a MAPS_API_KEY, both written by the setup script. You're not writing code today — you're recognizing it, so that next week you can write your own.\""
        ),
    },
    # SLIDE 27 — Run adk web
    {
        "num": 27,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:38 – 00:41 (3 min)",
        "type": "code_split",
        "title": "Step 4: Launch the agent UI",
        "subtitle": "adk web + Cloud Shell Web Preview on port 8000",
        "intro": "Start the dev server, then open it through Web Preview.",
        "bullets": [
            ("--allow_origins", "required in Cloud Shell so the IDE proxy origin is accepted"),
            ("Web Preview", "top-right of Cloud Shell → Change port → 8000 → Change and Preview"),
            ("Pick the app", "select mcp_bakery_app in the UI's dropdown"),
            ("Empty dropdown?", "you ran adk web from the wrong directory — cd adk_agent/ first"),
        ],
        "code_title": "Cloud Shell (inside adk_agent/)",
        "code": (
            "adk web --allow_origins \\\n"
            "  'regex:https://.*\\.cloudshell\\.dev'\n\n"
            "# Then in Cloud Shell:\n"
            "#  Web Preview (top right)\n"
            "#    → Change port → 8000\n"
            "#    → Change and Preview"
        ),
        "screenshot": "codelab_open_adk_ui.png",
        "notes": (
            "TIMING: 00:38 - 00:41 (3 mins)\n"
            "GOAL: Everyone has the ADK web UI open.\n\n"
            "SAY THIS:\n"
            "\"Launch it. From inside adk_agent, run adk web with allow_origins set to the cloudshell.dev regex — that flag exists because you're reaching the server through Cloud Shell's web proxy, and without it the WebSocket gets rejected. When you see 'Uvicorn running on 127.0.0.1:8000', click Web Preview in the top right, change the port to 8000, and preview.\"\n\n"
            "\"A chat UI opens. Top-left dropdown: pick mcp_bakery_app. If that dropdown is empty, stop — you're in the wrong directory. Ctrl-C, cd adk_agent, rerun. This trips up half the room every time.\""
        ),
    },
    # SLIDE 28 — Checkpoint 2: first query (macro)
    {
        "num": 28,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:41 – 00:44 (3 min)",
        "type": "checkpoint_visual",
        "title": "✋ Checkpoint 2: First tool call (macro)",
        "timer_seconds": 300,
        "bullets": [
            ("Ask", "\"I want to open a bakery in LA. Find the zip code with the highest morning foot traffic score.\""),
            ("Watch the trace", "agent calls get_table_info, then execute_sql on foot_traffic"),
            ("Expect", "zip 90403 (Santa Monica) surfaces to the top"),
            ("Auth error?", "re-run gcloud auth application-default login (60-min token)"),
        ],
        "screenshot": "codelab_adk_macro.png",
        "caption": "ADK web: execute_sql finds the top morning-traffic zip",
        "notes": (
            "TIMING: 00:41 - 00:44 (3 mins) — START THE 5-MIN TIMER.\n"
            "GOAL: The 'wow' moment — the agent writes and runs its own SQL.\n\n"
            "SAY THIS:\n"
            "\"First real question — copy it from the codelab, don't type it: 'I want to open a bakery in LA. Find the zip code with the highest morning foot traffic score.' Hit enter and DON'T just read the answer — open the Events / trace panel. You'll see the agent think: it calls get_table_info to learn the schema, then execute_sql with a query it wrote itself ordering by morning foot traffic. And 90403 — Santa Monica — floats to the top.\"\n\n"
            "\"You just watched a model turn English into SQL, run it against governed data, and reason over the result. If you got an auth error instead — say it with me — 60-minute token; re-run gcloud auth application-default login.\""
        ),
    },
    # SLIDE 29 — Checkpoint: micro validation (Maps)
    {
        "num": 29,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:44 – 00:47 (3 min)",
        "type": "checkpoint_visual",
        "title": "✋ Checkpoint 3: Validate on the ground (micro)",
        "timer_seconds": 300,
        "bullets": [
            ("Follow up", "\"Search for 'Bakeries' in that zip code — is it saturated?\""),
            ("Notice", "no zip in your prompt — the agent carried 90403 from memory"),
            ("Watch", "the trace switch servers: Maps search_places"),
            ("Click", "the Google Maps link in the answer — that's the required attribution"),
        ],
        "screenshot": "codelab_adk_micro.png",
        "caption": "ADK web: Maps search_places scans 90403 for bakeries",
        "notes": (
            "TIMING: 00:44 - 00:47 (3 mins)\n"
            "GOAL: The pivot moment — same conversation, different server, conversational memory.\n\n"
            "SAY THIS:\n"
            "\"Now the move that makes this more than a text-to-SQL demo. Follow up with: 'Search for Bakeries in that zip code — is it saturated?' Two things to notice. First, you never repeated the zip — the agent remembered 90403 from the conversation. Second, look at the trace: it did NOT touch BigQuery. It switched servers and called search_places on Maps.\"\n\n"
            "\"Same thread, two data worlds. And when the answer comes back with a Maps link — click it. That link isn't decoration, it's the attribution requirement we talked about, and the agent included it because the instruction told it to.\""
        ),
    },
    # SLIDE 30 — The full journey (challenge round)
    {
        "num": 30,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:47 – 00:50 (3 min)",
        "type": "journey_storyboard",
        "title": "Your turn: run the rest of the journey",
        "subtitle": "Three more prompts — predict the tool before you run each (answers in the codelab)",
        "steps": [
            ("Q3", "Max price of a Sourdough Loaf in LA Metro?", "BigQuery", "Erewhon ≈ $18.50", "blue"),
            ("Q4", "Forecast Dec '25 from best store, price $18", "BigQuery + AI.FORECAST", "qty → ×$18 revenue", "blue"),
            ("Q5", "Closest Restaurant Depot under 30 min away?", "Maps", "compute_routes check", "green"),
            ("★", "Chain them yourself — one thread, all five", "both servers", "full business case", "yellow"),
        ],
        "notes": (
            "TIMING: 00:47 - 00:50 (3 mins)\n"
            "GOAL: Self-directed exploration; make it a game.\n\n"
            "SAY THIS:\n"
            "\"Three more, and I want you to play a game: before you run each one, call the tool out loud. Pricing — 'max price for a Sourdough Loaf in LA Metro' — which server? BigQuery; Erewhon's at about eighteen-fifty, so our premium price lands around fifteen-to-eighteen. Forecasting — 'take my best store, forecast December, multiply by eighteen' — that's execute_sql running AI.FORECAST. Logistics — 'closest Restaurant Depot under thirty minutes' — Maps compute_routes.\"\n\n"
            "\"Run them in the SAME chat thread. The agent will carry context across all five. By the end you'll have a zip code, a saturation read, a price point, a revenue forecast, and a supply-chain check — a whole mini business case, in one conversation. GO.\""
        ),
    },
    # SLIDE 31 — Bonus challenges
    {
        "num": 31,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:50 – 00:52 (2 min)",
        "type": "two_cards_code",
        "title": "⚡ Finished early? Break it (productively)",
        "left_card": {
            "color": "blue",
            "title": "Tweak the instruction",
            "subtitle": "The cheapest way to change behavior",
            "code": (
                "# agent.py — edit the instruction, e.g.:\n"
                "\"Position the brand as budget-friendly\n"
                " and always cite the source table.\"\n"
                "# save → adk web reloads → re-ask Q3"
            ),
            "bullets": [
                ("Watch", "the price recommendation shift with one sentence"),
                ("Try", "a persona: 'You are a skeptical CFO'"),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Stretch the tools",
            "subtitle": "Push past the script",
            "code": (
                "# Ask about the weather on opening day\n"
                "\"Weather in 90403 this Saturday?\"\n"
                "   → Maps lookup_weather\n\n"
                "# Safety: swap to read-only SQL\n"
                "# in tools.py, the agent can only\n"
                "# call execute_sql_readonly"
            ),
            "bullets": [
                ("Weather", "a 3rd tool you never configured — it was just there"),
                ("Read-only", "one change removes the agent's ability to mutate data"),
            ],
        },
        "notes": (
            "TIMING: 00:50 - 00:52 (2 mins)\n"
            "GOAL: Keep fast finishers engaged while others catch up.\n\n"
            "SAY THIS:\n"
            "\"If you're done, don't sit idle — break it, productively. Two challenges. One: edit the instruction in agent.py — say 'position the brand as budget-friendly' — save, let adk web hot-reload, and re-ask the pricing question. One sentence changes the whole recommendation; that's prompt-as-control-surface. Two: ask about the weather on opening day. You never wrote a weather tool — lookup_weather was just there in the Maps server. That's the power of a tool catalog.\"\n\n"
            "FACILITATOR: This slide is your pressure-release valve. Keep it up while stragglers finish Checkpoint 3."
        ),
    },
    # SLIDE 32 — Troubleshooting
    {
        "num": 32,
        "module": "Module 3 • Lab B: Run It",
        "time": "00:52 – 00:55 (3 min)",
        "type": "objectives_card",
        "title": "Quick fixes — the 6 ways today breaks",
        "intro": "Hit a wall? It's almost certainly one of these:",
        "bullets": [
            ("Auth errors mid-lab", "ADC token expired (~60 min) → gcloud auth application-default login"),
            ("'API not enabled' / 403", "MCP endpoint off → gcloud beta services mcp enable bigquery.googleapis.com mapstools.googleapis.com"),
            ("Empty app dropdown", "adk web run from wrong dir → cd mcp/examples/launchmybakery/adk_agent"),
            ("Web Preview refuses", "missing --allow_origins 'regex:https://.*\\.cloudshell\\.dev'"),
            ("Maps calls fail", "key missing/restricted wrong → check .env MAPS_API_KEY, target service mapstools.googleapis.com"),
            ("Billing errors", "project has no billing → redeem the event credit and re-attach"),
        ],
        "notes": (
            "TIMING: 00:52 - 00:55 (3 mins) — buffer / catch-up window.\n"
            "GOAL: Clear every blocker so the room ends on a win.\n\n"
            "SAY THIS:\n"
            "\"This is the slide to photograph. Every failure today is one of these six. Auth error after working fine? 60-minute token — re-login. 403 that says not enabled? The MCP endpoint flag from setup_env. Empty dropdown? Wrong directory. Web preview won't load? You dropped the allow_origins flag. Maps failing but BigQuery fine? Check the key in .env. Anything about billing? You need the credit redeemed.\"\n\n"
            "FACILITATOR: Use this whole block as flexible time. If the room is ahead, invite people to try their own city. If behind, this is your catch-up."
        ),
    },
    # =====================================================================
    # MODULE 4 — WRAP-UP (00:55 – 01:15)  [flexible buffer built in]
    # =====================================================================
    # SLIDE 33 — Cleanup
    {
        "num": 33,
        "module": "Module 4 • Wrap-Up",
        "time": "00:55 – 00:57 (2 min)",
        "type": "code_split",
        "title": "Clean up — don't donate your credits back",
        "subtitle": "One script deletes the dataset, bucket, and API key",
        "intro": "Stop the server (Ctrl+C), then run cleanup from the repo root.",
        "bullets": [
            ("Deletes", "BigQuery dataset mcp_bakery + the GCS bucket"),
            ("Revokes", "the restricted Maps API key created at setup"),
            ("Keeps", "your project — so you can re-run ./setup scripts any time"),
            ("Why it matters", "BigQuery storage & Maps calls are pay-as-you-go"),
        ],
        "code_title": "Cloud Shell (repo root)",
        "code": (
            "# Ctrl+C to stop adk web, then:\n"
            "cd mcp/examples/launchmybakery\n\n"
            "chmod +x cleanup/cleanup_env.sh\n"
            "./cleanup/cleanup_env.sh\n\n"
            "# Deletes: mcp_bakery dataset,\n"
            "#  the staging bucket, and the API key."
        ),
        "notes": (
            "TIMING: 00:55 - 00:57 (2 mins)\n"
            "GOAL: Good cloud hygiene; protect the credits we just handed out.\n\n"
            "SAY THIS:\n"
            "\"Last responsible step: clean up. Ctrl+C to stop the server, then run cleanup_env.sh from the repo root. It deletes the mcp_bakery dataset, the staging bucket, and that API key. Your project stays, so if you want to run this again — or demo it to your team on Monday — the setup scripts recreate everything in about four minutes. Don't be the person who burns their credits on a forgotten BigQuery table.\""
        ),
    },
    # SLIDE 34 — Playbook recap
    {
        "num": 34,
        "module": "Module 4 • Wrap-Up",
        "time": "00:57 – 01:00 (3 min)",
        "type": "four_steps",
        "title": "Your Location-Intelligence Agent playbook",
        "subtitle": "The four ideas to take with you",
        "intro": "Everything today reduces to four moves you can reuse for any agent + any data.",
        "steps": [
            {"num": "1", "title": "Ground,\ndon't guess", "body": "An LLM alone hallucinates business facts. Ground it in your warehouse and live Maps data.", "highlight": False},
            {"num": "2", "title": "One agent,\nmany tools", "body": "A single ADK LlmAgent + MCP toolsets reasons across BigQuery AND Maps — no glue code.", "highlight": True},
            {"num": "3", "title": "Schema is\nthe prompt", "body": "get_table_info feeds column descriptions to the model. Documented data = smarter agent.", "highlight": False},
            {"num": "4", "title": "Govern by\ndefault", "body": "Managed MCP servers bring IAM, audit logs, read-only SQL, and Model Armor. Ship with guardrails.", "highlight": False},
        ],
        "notes": (
            "TIMING: 00:57 - 01:00 (3 mins)\n"
            "GOAL: Crystallize the four takeaways so they survive the parking lot.\n\n"
            "SAY THIS:\n"
            "\"If you remember four things. One: ground, don't guess — a bare model invents foot-traffic numbers; a grounded one queries them. Two: one agent, many tools — you never wrote a BigQuery or Maps client; two MCP toolsets gave one agent both worlds. Three: your schema is the prompt — the agent read our column descriptions to write its own SQL, so documenting your data is now an AI feature, not busywork. Four: govern by default — managed servers mean IAM, audit logs, read-only SQL and Model Armor come along for free.\"\n\n"
            "\"Ground, tools, schema, governance. Say it back to me on the way out.\""
        ),
    },
    # SLIDE 35 — What's next
    {
        "num": 35,
        "module": "Module 4 • Wrap-Up",
        "time": "01:00 – 01:02 (2 min)",
        "type": "three_tech",
        "title": "Where to take this next",
        "cols": [
            {
                "icon": "icon_adk.png",
                "title": "Deploy the agent",
                "body": "Move off adk web: containerize and ship to Cloud Run or Agent Engine, with a service-account identity.",
            },
            {
                "icon": "icon_mcp.png",
                "title": "More MCP servers",
                "body": "Same pattern, new tools: GCE, GKE, Spanner, AlloyDB, Cloud Run, Developer Knowledge — google/mcp on GitHub.",
            },
            {
                "icon": "icon_bigquery.png",
                "title": "Your own data",
                "body": "Point the agent at YOUR dataset: write rich column descriptions, scope the instruction, start with execute_sql_readonly.",
            },
        ],
        "notes": (
            "TIMING: 01:00 - 01:02 (2 mins)\n"
            "SAY THIS:\n"
            "\"Three on-ramps. First, deploy it — adk web is a debug UI, so for real users containerize and push to Cloud Run or Agent Engine with a service account. Second, more servers — the google/mcp repo lists every managed server: GCE, GKE, Spanner, Developer Knowledge; the wiring you learned today is identical. Third, the real homework — point this at your own data. Write honest column descriptions, scope the instruction to your dataset, and start on execute_sql_readonly until you trust it.\""
        ),
    },
    # SLIDE 36 — Closing cover reprise
    {
        "num": 36,
        "module": "Module 4 • Closing",
        "time": "01:02 – 01:03 (1 min)",
        "type": "cover",
        "title": "Build a Location Intelligence\nADK Agent with MCP servers\nfor BigQuery and Google Maps",
        "subtitle": "You built it: one grounded agent over your data and the real world",
        "badge": "Mission Complete 🎉",
        "notes": (
            "TIMING: 01:02 - 01:03 (1 min)\n"
            "SAY THIS:\n"
            "\"Look back at the GIF from the first minute. That agent — the one that queries BigQuery, searches Maps, forecasts revenue, checks drive time — you just built it, yourself, with your own project. Not a demo I showed you. Yours.\""
        ),
    },
    # SLIDE 37 — Thank you / Q&A
    {
        "num": 37,
        "module": "Module 4 • Closing & Q&A",
        "time": "01:03 – 01:15 (12 min)",
        "type": "thank_you",
        "title": "Thank you!",
        "subtitle": "Questions & live troubleshooting.\nThe codelab stays free — take it, fork it, teach it.",
        "qr_top": "qr_codelab.png",
        "qr_top_label": "Codelab\nadk-mcp-bigquery-maps",
        "qr_mid": "qr_linkedin.png",
        "qr_mid_label": "Connect on LinkedIn\nin/rabimba-karanjai",
        "qr_bottom": "qr_rabimba_github.png",
        "qr_bottom_label": "Slides & Runbook\nGDE-ML-Artifacts",
        "notes": (
            "TIMING: 01:03 - 01:15 (remaining time — Q&A).\n"
            "SAY THIS:\n"
            "\"Thank you! Everything is open: the codelab is free and stays up — take it, fork it, run this same workshop at your own GDG. Top QR is the codelab, bottom is my repo with this deck and the full speaker script. And if you want to compare notes on agents in production — the middle QR is my LinkedIn; I answer.\"\n\n"
            "\"The rest of our time is yours — questions, and if anyone's still fighting a red error, bring it up now and we'll fix it live.\"\n\n"
            "FACILITATOR: Keep the troubleshooting slide (G key) one keystroke away during Q&A. Budget remaining clock — the runbook pacing table gives you slack back if concepts ran long."
        ),
    },
    # =====================================================================
    # REFERENCE (untimed, not presented)
    # =====================================================================
    # SLIDE 38 — Cheat sheet
    {
        "num": 38,
        "module": "Appendix • Reference",
        "time": "Reference Slide",
        "type": "two_cards_code",
        "title": "Cheat sheet — every command from today",
        "left_card": {
            "color": "blue",
            "title": "Setup",
            "subtitle": "Run once per project",
            "code": (
                "export PROJECT_ID=$(gcloud config get project)\n"
                "git clone https://github.com/google/mcp.git\n"
                "cd mcp/examples/launchmybakery\n"
                "gcloud auth application-default login\n"
                "./setup/setup_env.sh\n"
                "./setup/setup_bigquery.sh"
            ),
            "bullets": [
                ("MCP endpoints", "gcloud beta services mcp enable <svc>"),
                ("Billing", "required for BigQuery + Maps"),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Run & clean up",
            "subtitle": "Each session",
            "code": (
                "python3 -m venv .venv && source .venv/bin/activate\n"
                "pip install \"google-adk[mcp]\"\n"
                "cd adk_agent/\n"
                "adk web --allow_origins \\\n"
                "  'regex:https://.*\\.cloudshell\\.dev'\n\n"
                "# later:\n"
                "./cleanup/cleanup_env.sh"
            ),
            "bullets": [
                ("Token", "re-login after ~60 min"),
                ("Read-only", "prefer execute_sql_readonly in prod"),
            ],
        },
        "notes": (
            "REFERENCE SLIDE — not presented live.\n"
            "Every command from the workshop in one place. Point attendees here if they re-run the lab later; it is also the fastest 'second screen' reference while facilitating."
        ),
    },
]


# ---------------------------------------------------------------------------
# PART 1: BUILD EDITABLE POWERPOINT (.PPTX) FROM REFERENCE TEMPLATE
# ---------------------------------------------------------------------------
def clear_slide_shapes(slide):
    for sh in list(slide.shapes):
        sp = sh._element
        sp.getparent().remove(sp)


def set_slide_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=(32, 33, 36), font_name="Google Sans", align=PP_ALIGN.LEFT, word_wrap=True):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)
    return tb


def add_rounded_box(slide, left, top, width, height, fill_rgb=None, line_rgb=None, line_pt=1.5, radius=0.04):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    if sh.adjustments and len(sh.adjustments) > 0:
        sh.adjustments[0] = radius
    if fill_rgb is not None:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor(*fill_rgb)
    else:
        sh.fill.background()
    if line_rgb is not None:
        sh.line.color.rgb = RGBColor(*line_rgb)
        sh.line.width = Pt(line_pt)
    else:
        sh.line.fill.background()
    return sh


def add_terminal_box(slide, left, top, width, height, title_text, code_text, font_size=9.5):
    # Dark container
    add_rounded_box(slide, left, top, width, height, fill_rgb=(32, 33, 36), line_rgb=(60, 64, 67), line_pt=1, radius=0.03)
    # macOS traffic light dots
    dot_colors = [(234, 67, 53), (251, 188, 4), (52, 168, 83)]
    for idx, dc in enumerate(dot_colors):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(left + 0.16 + idx * 0.18),
            Inches(top + 0.13),
            Inches(0.11),
            Inches(0.11),
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = RGBColor(*dc)
        dot.line.fill.background()
    if title_text:
        add_textbox(
            slide,
            left + 0.72,
            top + 0.06,
            width - 0.85,
            0.25,
            title_text,
            font_size=8.5,
            bold=True,
            color=(154, 160, 166),
            font_name="Roboto Mono",
            align=PP_ALIGN.LEFT,
        )
    add_textbox(
        slide,
        left + 0.14,
        top + 0.34,
        width - 0.28,
        height - 0.42,
        code_text,
        font_size=font_size,
        bold=False,
        color=(232, 234, 237),
        font_name="Roboto Mono",
    )


def add_bullet_list_box(slide, left, top, width, height, intro, bullets, intro_size=11.5, bullet_size=10.5):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    first = True
    if intro:
        p = tf.paragraphs[0]
        first = False
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = intro
        r.font.name = "Google Sans"
        r.font.size = Pt(intro_size)
        r.font.color.rgb = RGBColor(60, 64, 67)
    for b_title, b_body in bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(6)
        if b_title is None:
            r1 = p.add_run()
            r1.text = "• "
            r1.font.name = "Google Sans"
            r1.font.size = Pt(bullet_size)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(26, 115, 232)
        else:
            r1 = p.add_run()
            r1.text = f"• {b_title}: "
            r1.font.name = "Google Sans"
            r1.font.size = Pt(bullet_size)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(26, 115, 232)
        r2 = p.add_run()
        r2.text = b_body
        r2.font.name = "Google Sans"
        r2.font.size = Pt(bullet_size)
        r2.font.color.rgb = RGBColor(32, 33, 36)
    return tb


def add_image_fit(slide, img_path, left, top, max_w, max_h):
    from PIL import Image
    full_path = os.path.join(ASSETS_DIR, img_path)
    if not os.path.exists(full_path):
        return
    with Image.open(full_path) as im:
        w_px, h_px = im.size
    aspect = w_px / float(h_px)
    box_aspect = max_w / float(max_h)
    if aspect >= box_aspect:
        w = max_w
        h = max_w / aspect
    else:
        h = max_h
        w = max_h * aspect
    x = left + (max_w - w) / 2.0
    y = top + (max_h - h) / 2.0
    slide.shapes.add_picture(full_path, Inches(x), Inches(y), Inches(w), Inches(h))


def build_pptx(output_path):
    prs = pptx.Presentation(REF_PPTX)

    # Map required slide layouts from the reference presentation
    layouts = {l.name: l for m in prs.slide_masters for l in m.slide_layouts}
    layout_cover = layouts["CUSTOM_6_1_3_3_1"]
    layout_qr = layouts["TITLE_AND_BODY_1"]
    layout_speaker = layouts["CUSTOM_6_1_3_2_1_1_4"]
    layout_content = layouts["CUSTOM_6_1_3_2_1_1_3_1_1_1_1_1_2_1"]

    # Remove existing slides from prs
    xml_slides = prs.slides._sldIdLst
    for sldId in list(xml_slides):
        rId = sldId.rId
        prs.part.drop_rel(rId)
        xml_slides.remove(sldId)

    for sdata in SLIDES_DATA:
        stype = sdata["type"]
        if stype == "cover":
            slide = prs.slides.add_slide(layout_cover)
            clear_slide_shapes(slide)
            add_rounded_box(slide, 0.45, 1.35, 2.75, 0.36, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=1, radius=0.45)
            add_textbox(slide, 0.50, 1.39, 2.65, 0.28, sdata.get("badge", "Workshop"), font_size=11, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.85, 5.10, 2.10, sdata["title"], font_size=28, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.45, 4.05, 5.00, 0.85, sdata["subtitle"], font_size=13, bold=False, color=(95, 99, 104))

        elif stype == "qr_hub":
            slide = prs.slides.add_slide(layout_qr)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.50, 0.45, 9.00, 0.55, sdata["title"], font_size=28, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.50, 1.00, 9.00, 0.35, sdata["subtitle"], font_size=13, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            for idx, c in enumerate(sdata["cards"]):
                cx = 0.55 + idx * 3.05
                add_rounded_box(slide, cx, 1.50, 2.80, 3.70, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_textbox(slide, cx + 0.14, 1.64, 2.52, 0.45, c["title"], font_size=13, bold=True, color=(32, 33, 36))
                add_textbox(slide, cx + 0.14, 2.08, 2.52, 0.36, c["url_text"], font_size=9.5, bold=True, color=(26, 115, 232))
                add_textbox(slide, cx + 0.14, 2.45, 2.52, 0.65, c["desc"], font_size=9.5, bold=False, color=(95, 99, 104))
                add_image_fit(slide, c["qr"], cx + 0.45, 3.15, 1.90, 1.90)

        elif stype == "speaker":
            slide = prs.slides.add_slide(layout_speaker)
            clear_slide_shapes(slide)
            add_image_fit(slide, sdata["photo"], 0.65, 1.15, 3.55, 3.55)
            add_textbox(slide, 4.75, 1.50, 4.75, 1.45, sdata["title"], font_size=40, bold=True, color=(32, 33, 36))
            add_textbox(slide, 4.75, 3.10, 4.75, 1.25, sdata["subtitle"], font_size=18, bold=False, color=(60, 64, 67))

        elif stype == "thank_you":
            slide = prs.slides.add_slide(layout_speaker)
            clear_slide_shapes(slide)
            add_textbox(slide, 4.80, 1.85, 3.30, 1.10, sdata["title"], font_size=44, bold=True, color=(32, 33, 36))
            add_textbox(slide, 4.80, 2.95, 3.30, 1.10, sdata["subtitle"], font_size=14, bold=False, color=(60, 64, 67))
            # Data-driven QR stack: 2 QRs (legacy roomy) or 3 QRs (with LinkedIn)
            qrs = [(sdata["qr_top"], sdata["qr_top_label"])]
            if sdata.get("qr_mid"):
                qrs.append((sdata["qr_mid"], sdata["qr_mid_label"]))
            qrs.append((sdata["qr_bottom"], sdata["qr_bottom_label"]))
            if len(qrs) == 2:
                geom = [(8.15, 0.45, 1.45, 1.92), (8.15, 3.35, 1.45, 4.82)]
                fsz = 8.5
            else:
                geom = [(8.25, 0.28, 1.22, 1.52), (8.25, 2.02, 1.22, 3.26), (8.25, 3.76, 1.22, 5.00)]
                fsz = 8
            for (qimg, qlabel), (qx, qy, qs, ly) in zip(qrs, geom):
                add_image_fit(slide, qimg, qx, qy, qs, qs)
                add_textbox(slide, 7.70, ly, 2.35, 0.45, qlabel, font_size=fsz, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)

        elif stype == "section_poll":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_image_fit(slide, sdata["icon"], 4.62, 0.90, 0.75, 0.75)
            add_textbox(slide, 1.00, 1.72, 8.00, 1.05, sdata["title"], font_size=28, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            poll = sdata["poll"]
            add_rounded_box(slide, 0.75, 2.88, 8.50, 2.20, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=2, radius=0.04)
            add_textbox(slide, 0.95, 2.98, 8.10, 0.62, poll["question"], font_size=12.5, bold=True, color=(23, 78, 166))
            opts_text = "\n".join(f"• {o}" for o in poll["options"])
            add_textbox(slide, 1.05, 3.62, 7.90, 0.75, opts_text, font_size=11, bold=False, color=(32, 33, 36))
            add_textbox(slide, 0.95, 4.42, 8.10, 0.58, f"💡 Key Insight: {poll['answer']}", font_size=10.5, bold=True, color=(19, 115, 51))

        elif stype == "agent_triad":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.45, 0.65, 7.60, 2.10, sdata["headline"], font_size=23, bold=True, color=(32, 33, 36))
            coords = [(0.35, 3.40, 2.75, 1.85), (3.55, 3.40, 2.90, 1.85), (6.90, 3.40, 2.75, 1.85)]
            for idx, box in enumerate(sdata["boxes"]):
                bx, by, bw, bh = coords[idx]
                add_rounded_box(slide, bx, by, bw, bh, fill_rgb=(241, 243, 244), line_rgb=(218, 220, 224), line_pt=1.5, radius=0.05)
                add_image_fit(slide, box["icon"], bx + bw / 2 - 0.35, by - 0.38, 0.70, 0.70)
                add_textbox(slide, bx + 0.12, by + 0.48, bw - 0.24, 1.15, box["label"], font_size=18, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)

        elif stype == "objectives_card":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.82, 9.10, 0.55, sdata["title"], font_size=26, bold=True, color=(32, 33, 36))
            add_rounded_box(slide, 0.45, 1.48, 9.10, 3.60, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.5, radius=0.04)
            add_bullet_list_box(slide, 0.68, 1.64, 8.64, 3.30, sdata["intro"], sdata["bullets"], intro_size=12.5, bullet_size=11)

        elif stype == "arch_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.78, 9.10, 0.52, sdata["title"], font_size=26, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.45, 1.32, 4.45, 0.36, sdata["subtitle"], font_size=13.5, bold=True, color=(26, 115, 232))
            add_bullet_list_box(slide, 0.45, 1.72, 4.35, 3.40, sdata["intro"], sdata["bullets"], intro_size=10.5, bullet_size=10)
            add_image_fit(slide, sdata["image"], 4.88, 1.35, 4.75, 3.70)

        elif stype == "three_tech":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.50, 0.90, 7.00, 0.50, sdata["title"], font_size=22, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            for idx, col in enumerate(sdata["cols"]):
                cx = 0.75 + idx * 2.95
                add_rounded_box(slide, cx, 1.65, 2.65, 3.40, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_image_fit(slide, col["icon"], cx + 0.18, 1.82, 0.68, 0.68)
                add_textbox(slide, cx + 0.16, 2.62, 2.33, 0.62, col["title"], font_size=13.5, bold=True, color=(32, 33, 36))
                add_textbox(slide, cx + 0.16, 3.30, 2.33, 1.60, col["body"], font_size=10.5, bold=False, color=(60, 64, 67))

        elif stype == "two_cards_quiz":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (26, 115, 232) if card["color"] == "blue" else (234, 67, 53)
                add_rounded_box(slide, cx, 0.82, 4.40, 3.32, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 0.94, 4.04, 0.36, card["title"], font_size=15.5, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.30, 4.04, 0.28, card["subtitle"], font_size=10.5, bold=True, color=(95, 99, 104))
                add_bullet_list_box(slide, cx + 0.16, 1.62, 4.08, 2.42, None, card["items"], bullet_size=9.8)
            quiz = sdata["quiz"]
            add_rounded_box(slide, 0.48, 4.24, 9.04, 0.92, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.8, radius=0.03)
            add_textbox(slide, 0.64, 4.28, 8.72, 0.42, quiz["question"], font_size=9.8, bold=True, color=(176, 96, 0))
            add_textbox(slide, 0.64, 4.70, 8.72, 0.42, quiz["answer"], font_size=9.5, bold=False, color=(32, 33, 36))

        elif stype == "lab_divider":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.00, 1.95, 8.00, 0.80, sdata["title"], font_size=36, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_image_fit(slide, "ref_slide11_pic4.png", 1.85, 2.95, 0.42, 0.42)
            add_textbox(slide, 2.40, 2.96, 6.20, 0.50, sdata["subtitle"], font_size=16, bold=True, color=(26, 115, 232))

        elif stype == "code_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.78, 9.04, 0.48, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.48, 1.26, 4.40, 0.32, sdata["subtitle"], font_size=12, bold=True, color=(26, 115, 232))
            add_bullet_list_box(slide, 0.48, 1.60, 4.35, 3.55, sdata.get("intro"), sdata["bullets"], intro_size=10, bullet_size=9.6)
            if sdata.get("screenshot"):
                add_terminal_box(slide, 4.98, 1.28, 4.58, 2.15, sdata["code_title"], sdata["code"], font_size=8.5)
                add_image_fit(slide, sdata["screenshot"], 4.98, 3.52, 4.58, 1.62)
            else:
                add_terminal_box(slide, 4.98, 1.28, 4.58, 3.85, sdata["code_title"], sdata["code"], font_size=8.8)

        elif stype == "stepper_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.55, 0.78, 8.90, 0.50, sdata["title"], font_size=24, bold=True, color=(32, 33, 36))
            add_rounded_box(slide, 0.55, 1.38, 4.10, 3.75, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.5, radius=0.04)
            for idx, (snum, stitle, sdesc) in enumerate(sdata["steps"]):
                sy = 1.52 + idx * 0.92
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.78), Inches(sy), Inches(0.40), Inches(0.40))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(26, 115, 232)
                pill.line.fill.background()
                add_textbox(slide, 0.78, sy + 0.05, 0.40, 0.30, snum, font_size=11, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)
                add_textbox(slide, 1.32, sy - 0.06, 3.15, 0.28, stitle, font_size=12, bold=True, color=(32, 33, 36))
                add_textbox(slide, 1.32, sy + 0.20, 3.15, 0.40, sdesc, font_size=9, bold=False, color=(19, 115, 51), font_name="Roboto Mono")
            # Top-right callout card
            add_rounded_box(slide, 4.88, 1.38, 4.64, 1.62, fill_rgb=(255, 255, 255), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
            add_rounded_box(slide, 5.06, 1.50, 2.65, 0.26, fill_rgb=(252, 232, 230), line_rgb=None, radius=0.3)
            add_textbox(slide, 5.10, 1.52, 2.55, 0.22, sdata["callout_badge"], font_size=8, bold=True, color=(197, 34, 31))
            add_textbox(slide, 5.06, 1.80, 4.30, 0.30, sdata["callout_title"], font_size=12, bold=True, color=(32, 33, 36))
            add_textbox(slide, 5.06, 2.10, 4.30, 0.82, sdata["callout_body"], font_size=9.5, bold=False, color=(60, 64, 67))
            # Bottom-right terminal card
            add_terminal_box(slide, 4.88, 3.12, 4.64, 2.02, sdata["code_title"], sdata["code"], font_size=8.5)

        elif stype == "two_cards_code":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.74, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(32, 33, 36))
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (26, 115, 232) if card["color"] == "blue" else (234, 67, 53)
                add_rounded_box(slide, cx, 1.22, 4.40, 3.92, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 1.32, 4.04, 0.34, card["title"], font_size=14.5, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.64, 4.04, 0.26, card["subtitle"], font_size=10, bold=False, color=(95, 99, 104))
                add_terminal_box(slide, cx + 0.18, 1.96, 4.04, 1.72, "snippet / command", card["code"], font_size=8.2)
                add_bullet_list_box(slide, cx + 0.16, 3.74, 4.08, 1.32, None, card["bullets"], bullet_size=9.5)

        elif stype == "checkpoint_visual":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.78, 9.04, 0.48, sdata["title"], font_size=21, bold=True, color=(32, 33, 36))
            add_bullet_list_box(slide, 0.48, 1.35, 4.35, 3.75, None, sdata["bullets"], bullet_size=10.2)
            add_rounded_box(slide, 4.98, 1.35, 4.55, 3.40, fill_rgb=(248, 249, 250), line_rgb=(26, 115, 232), line_pt=1.8, radius=0.03)
            add_image_fit(slide, sdata["screenshot"], 5.08, 1.45, 4.35, 3.20)
            add_textbox(slide, 4.98, 4.80, 4.55, 0.35, sdata.get("caption", ""), font_size=9, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "four_steps":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.52, 0.76, 8.96, 0.48, sdata["title"], font_size=24, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.52, 1.24, 8.96, 0.32, sdata["subtitle"], font_size=13, bold=True, color=(26, 115, 232))
            add_textbox(slide, 0.52, 1.60, 8.96, 0.62, sdata["intro"], font_size=11, bold=False, color=(60, 64, 67))
            for idx, st in enumerate(sdata["steps"]):
                sx = 0.52 + idx * 2.28
                is_hi = st.get("highlight", False)
                border_rgb = (26, 115, 232) if is_hi else (218, 220, 224)
                add_rounded_box(slide, sx, 2.32, 2.12, 2.80, fill_rgb=(248, 249, 250), line_rgb=border_rgb, line_pt=2.2 if is_hi else 1.2, radius=0.04)
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(sx + 0.18), Inches(2.50), Inches(0.42), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(26, 115, 232) if is_hi else RGBColor(232, 240, 254)
                pill.line.fill.background()
                add_textbox(slide, sx + 0.18, 2.55, 0.42, 0.32, st["num"], font_size=12, bold=True, color=(255, 255, 255) if is_hi else (26, 115, 232), align=PP_ALIGN.CENTER)
                add_textbox(slide, sx + 0.14, 3.02, 1.84, 0.58, st["title"], font_size=11.5, bold=True, color=(26, 115, 232) if is_hi else (32, 33, 36))
                add_textbox(slide, sx + 0.14, 3.64, 1.84, 1.38, st["body"], font_size=9.6, bold=False, color=(60, 64, 67))

        elif stype == "verification_cards":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.74, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(32, 33, 36))
            lc = sdata["left_card"]
            rc = sdata["right_card"]
            # Left card (Blue)
            add_rounded_box(slide, 0.48, 1.20, 4.40, 3.95, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.2, radius=0.04)
            add_textbox(slide, 0.68, 1.32, 4.00, 0.35, lc["title"], font_size=14, bold=True, color=(26, 115, 232))
            add_rounded_box(slide, 0.68, 1.75, 4.00, 0.85, fill_rgb=(241, 243, 244), line_rgb=None, radius=0.03)
            add_textbox(slide, 0.80, 1.80, 3.76, 0.25, "User Query:", font_size=10, bold=True, color=(26, 115, 232))
            add_textbox(slide, 0.80, 2.05, 3.76, 0.50, lc["query"], font_size=9.5, bold=False, color=(32, 33, 36))
            add_rounded_box(slide, 0.68, 2.72, 4.00, 2.25, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=1.2, radius=0.03)
            add_textbox(slide, 0.80, 2.82, 3.76, 0.28, lc["result_title"], font_size=10.5, bold=True, color=(19, 115, 51))
            add_textbox(slide, 0.80, 3.12, 3.76, 1.05, lc["result_body"], font_size=9.5, bold=False, color=(32, 33, 36))
            add_textbox(slide, 0.80, 4.22, 3.76, 0.65, f"Verification Goal: {lc['goal']}", font_size=8.8, bold=False, color=(95, 99, 104))

            # Right card (Red)
            add_rounded_box(slide, 5.12, 1.20, 4.40, 3.95, fill_rgb=(255, 255, 255), line_rgb=(234, 67, 53), line_pt=2.2, radius=0.04)
            add_textbox(slide, 5.32, 1.32, 4.00, 0.35, rc["title"], font_size=14, bold=True, color=(197, 34, 31))
            add_rounded_box(slide, 5.32, 1.75, 4.00, 1.52, fill_rgb=(252, 232, 230), line_rgb=(234, 67, 53), line_pt=1, radius=0.03)
            add_textbox(slide, 5.44, 1.82, 3.76, 0.32, rc["trap1_title"], font_size=9.8, bold=True, color=(197, 34, 31))
            add_textbox(slide, 5.44, 2.14, 3.76, 0.24, rc["trap1_expected"], font_size=9.2, bold=True, color=(19, 115, 51))
            add_textbox(slide, 5.44, 2.40, 3.76, 0.80, rc["trap1_body"], font_size=9.0, bold=False, color=(32, 33, 36))

            add_rounded_box(slide, 5.32, 3.40, 4.00, 1.56, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1, radius=0.03)
            add_textbox(slide, 5.44, 3.47, 3.76, 0.32, rc["trap2_title"], font_size=9.8, bold=True, color=(176, 96, 0))
            add_textbox(slide, 5.44, 3.79, 3.76, 0.24, rc["trap2_expected"], font_size=9.2, bold=True, color=(19, 115, 51))
            add_textbox(slide, 5.44, 4.05, 3.76, 0.82, rc["trap2_body"], font_size=9.0, bold=False, color=(32, 33, 36))

        # ---- NEW TYPES (Location Intelligence deck) ----

        elif stype == "hero_media":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.55, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.10, 9.10, 0.32, sdata["subtitle"], font_size=12, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            # pptx can't animate the gif; use the extracted still frame
            still = sdata.get("image_still", sdata["image"])
            add_rounded_box(slide, 1.15, 1.55, 7.70, 3.05, fill_rgb=(13, 17, 23), line_rgb=None, radius=0.03)
            add_image_fit(slide, still, 1.20, 1.60, 7.60, 2.95)
            add_textbox(slide, 0.45, 4.70, 9.10, 0.35, sdata.get("caption", ""), font_size=8.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "diagram_build":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.52, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.05, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            n = len(sdata["build_steps"])
            top = 1.45
            row_h = 2.95 / n
            for i, st in enumerate(sdata["build_steps"]):
                y = top + i * row_h
                add_rounded_box(slide, 1.10, y, 7.80, row_h - 0.10, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.05)
                add_image_fit(slide, st["icon"], 1.28, y + 0.08, 0.46, 0.46)
                add_textbox(slide, 1.90, y + 0.02, 2.05, 0.34, st["label"], font_size=13, bold=True, color=(23, 78, 166))
                add_textbox(slide, 3.95, y + 0.02, 4.80, row_h - 0.12, st["desc"], font_size=9.5, bold=False, color=(60, 64, 67))
            add_rounded_box(slide, 1.10, 4.55, 7.80, 0.50, fill_rgb=(230, 244, 234), line_rgb=None, radius=0.3)
            add_textbox(slide, 1.10, 4.62, 7.80, 0.36, sdata["summary"], font_size=12, bold=True, color=(19, 115, 51), align=PP_ALIGN.CENTER)

        elif stype == "split_worlds":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.60, 9.10, 0.55, sdata["title"], font_size=26, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            specs = [("left", 0.55, (26, 115, 232), (232, 240, 254)), ("right", 6.05, (19, 115, 51), (230, 244, 234))]
            for key, cx, line, fill in specs:
                w = sdata[key]
                add_rounded_box(slide, cx, 1.45, 3.40, 3.30, fill_rgb=fill, line_rgb=line, line_pt=2.2, radius=0.04)
                add_image_fit(slide, w["icon"], cx + 0.18, 1.62, 0.55, 0.55)
                add_textbox(slide, cx + 0.82, 1.72, 2.40, 0.40, w["heading"], font_size=13.5, bold=True, color=line)
                add_bullet_list_box(slide, cx + 0.20, 2.30, 3.00, 2.30, None, [(None, p) for p in w["points"]], bullet_size=10.5)
            add_rounded_box(slide, 4.05, 2.55, 1.90, 1.20, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.8, radius=0.06)
            add_textbox(slide, 4.12, 2.66, 1.76, 1.00, sdata["bridge"], font_size=8.8, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)

        elif stype == "nxm":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.52, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.05, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            for ci, (cx, cap) in enumerate([(0.55, sdata["left_caption"]), (5.15, sdata["right_caption"])]):
                add_rounded_box(slide, cx, 1.50, 4.30, 3.55, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_textbox(slide, cx + 0.10, 1.58, 4.10, 0.30, cap, font_size=10.5, bold=True, color=(95, 99, 104), align=PP_ALIGN.CENTER)
                for ri, a in enumerate(sdata["agents"]):
                    add_rounded_box(slide, cx + 0.25, 2.05 + ri * 0.92, 1.45, 0.72, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=1.5, radius=0.08)
                    add_textbox(slide, cx + 0.25, 2.22 + ri * 0.92, 1.45, 0.40, a, font_size=9.5, bold=True, color=(23, 78, 166), align=PP_ALIGN.CENTER)
                for ri, sv in enumerate(sdata["servers"]):
                    add_rounded_box(slide, cx + 2.60, 2.05 + ri * 0.92, 1.45, 0.72, fill_rgb=(255, 255, 255), line_rgb=(19, 115, 51), line_pt=1.5, radius=0.08)
                    add_textbox(slide, cx + 2.60, 2.22 + ri * 0.92, 1.45, 0.40, sv, font_size=9.5, bold=True, color=(19, 115, 51), align=PP_ALIGN.CENTER)
                if ci == 0:
                    add_textbox(slide, cx + 1.80, 2.40, 0.70, 1.60, "✕\n✕\n✕", font_size=20, bold=True, color=(234, 67, 53), align=PP_ALIGN.CENTER)
                else:
                    hub = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx + 1.80), Inches(2.75), Inches(0.72), Inches(0.72))
                    hub.fill.solid(); hub.fill.fore_color.rgb = RGBColor(26, 115, 232); hub.line.fill.background()
                    add_textbox(slide, cx + 1.80, 2.93, 0.72, 0.36, "MCP", font_size=10, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)

        elif stype == "tool_catalog":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            accent = sdata.get("accent", "blue")
            ac = (23, 78, 166) if accent == "blue" else (19, 115, 51)
            add_image_fit(slide, sdata["icon"], 0.55, 0.55, 0.55, 0.55)
            add_textbox(slide, 1.25, 0.60, 8.20, 0.40, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 1.25, 1.02, 8.20, 0.28, sdata["subtitle"], font_size=11, bold=False, color=(95, 99, 104))
            n = len(sdata["tools"])
            top = 1.50
            row_h = 2.85 / n
            for i, (t, d) in enumerate(sdata["tools"]):
                y = top + i * row_h
                add_rounded_box(slide, 0.55, y, 8.90, row_h - 0.08, fill_rgb=(255, 255, 255), line_rgb=(218, 220, 224), line_pt=1, radius=0.05)
                add_rounded_box(slide, 0.72, y + 0.06, 2.95, row_h - 0.20, fill_rgb=(241, 243, 244), line_rgb=None, radius=0.05)
                add_textbox(slide, 0.80, y + 0.09, 2.80, row_h - 0.24, t, font_size=11, bold=True, color=ac, font_name="Roboto Mono")
                add_textbox(slide, 3.85, y + 0.05, 5.45, row_h - 0.14, d, font_size=10, bold=False, color=(32, 33, 36))
            add_rounded_box(slide, 0.55, 4.50, 8.90, 0.62, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.2, radius=0.04)
            add_textbox(slide, 0.72, 4.55, 8.60, 0.52, sdata["callout"], font_size=9.2, bold=True, color=(32, 33, 36))

        elif stype == "code_focus":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.70, 9.04, 0.45, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.48, 1.16, 5.30, 0.30, sdata["subtitle"], font_size=11.5, bold=True, color=(26, 115, 232))
            add_terminal_box(slide, 0.48, 1.52, 5.35, 3.55, sdata.get("lang", "python"), sdata["code"], font_size=8.8)
            add_rounded_box(slide, 6.02, 1.52, 3.50, 3.55, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.2, radius=0.04)
            add_textbox(slide, 6.22, 1.66, 3.10, 0.30, "The three control surfaces:", font_size=11, bold=True, color=(32, 33, 36))
            add_bullet_list_box(slide, 6.20, 2.02, 3.14, 2.95, None, [(k, v) for k, v in sdata["callouts"]], bullet_size=10)

        elif stype == "journey_storyboard":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.50, sdata["title"], font_size=23, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.04, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            n = len(sdata["steps"])
            top = 1.48
            row_h = 3.55 / n
            cmap = {"blue": (26, 115, 232), "green": (19, 115, 51), "yellow": (176, 96, 0)}
            for i, (tag, q, tool, res, color) in enumerate(sdata["steps"]):
                y = top + i * row_h
                line = cmap.get(color, (218, 220, 224))
                add_rounded_box(slide, 0.55, y, 8.90, row_h - 0.10, fill_rgb=(255, 255, 255), line_rgb=line, line_pt=1.5, radius=0.05)
                add_textbox(slide, 0.70, y + 0.04, 0.62, row_h - 0.18, tag, font_size=15, bold=True, color=line)
                add_textbox(slide, 1.38, y + 0.04, 4.05, row_h - 0.18, q, font_size=10.3, bold=True, color=(32, 33, 36))
                add_textbox(slide, 5.50, y + 0.04, 2.05, row_h - 0.18, tool, font_size=8.6, bold=False, color=(95, 99, 104), font_name="Roboto Mono")
                add_textbox(slide, 7.62, y + 0.04, 1.72, row_h - 0.18, res, font_size=8.8, bold=True, color=(32, 33, 36), align=PP_ALIGN.RIGHT)

        set_slide_notes(slide, sdata["notes"])

    prs.save(output_path)
    print(f"Saved PPTX: {output_path} ({len(prs.slides)} slides)")


# ---------------------------------------------------------------------------
# PART 2: BUILD INTERACTIVE HTML PRESENTATION DECK (index.html)
# ---------------------------------------------------------------------------
def render_slide_inner_html(s):
    stype = s["type"]
    num = s["num"]
    timer_html = ""
    if s.get("timer_seconds"):
        mins = s["timer_seconds"] // 60
        secs = s["timer_seconds"] % 60
        timer_html = f"""
        <div class="lab-timer-widget" data-seconds="{s['timer_seconds']}" id="timer-{num}">
          <span class="timer-label">⏱️ Hands-On Lab Timer:</span>
          <span class="timer-display" id="timer-disp-{num}">{mins:02d}:{secs:02d}</span>
          <button class="timer-btn" onclick="toggleLabTimer({num})">▶ Start / Pause</button>
          <button class="timer-btn secondary" onclick="resetLabTimer({num})">↺ Reset</button>
        </div>
        """

    if stype == "cover":
        title_html = html.escape(s["title"]).replace("\n", "<br/>")
        return f"""
        <div class="slide-canvas slide-cover">
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <div class="cover-left">
            <div class="pill-badge">{html.escape(s.get('badge', 'Workshop'))}</div>
            <h1 class="cover-title">{title_html}</h1>
            <p class="cover-subtitle">{html.escape(s['subtitle'])}</p>
            <div class="cover-meta">Rabimba Karanjai • Google Developer Expert (AI/ML)</div>
          </div>
          <div class="cover-right">
            <img src="assets/bg_cover_layers_cropped.png" alt="Google Cloud Layers"/>
          </div>
        </div>
        """

    if stype == "qr_hub":
        cards_html = ""
        for c in s["cards"]:
            cards_html += f"""
            <div class="qr-card">
              <div class="qr-icon-badge">&lt;/&gt;</div>
              <h3>{html.escape(c['title'])}</h3>
              <a href="{html.escape(c['url'])}" target="_blank" class="qr-link">{html.escape(c['url_text'])}</a>
              <p>{html.escape(c['desc'])}</p>
              <img class="qr-img" src="assets/{html.escape(c['qr'])}" alt="QR Code"/>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="qr-grid">{cards_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "speaker":
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="speaker-fan-bg">
            <img src="assets/bg_speaker_fan.png" alt="Fan Background"/>
          </div>
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <span class="prop-badge-abs">Google Developer Expert</span>
          <div class="speaker-content">
            <div class="speaker-photo-wrap">
              <img src="assets/{html.escape(s['photo'])}" alt="Rabimba Karanjai"/>
            </div>
            <div class="speaker-Bio-text">
              <h1>Rabimba<br/>Karanjai</h1>
              <p class="role-line">Google Developer Expert — AI &amp; ML</p>
              <p class="role-line">ML Scientist — PayPal</p>
              <div class="speaker-tags">
                <span class="tag-chip">Agentic Systems</span>
                <span class="tag-chip">Model Context Protocol</span>
                <span class="tag-chip">Google Cloud Run</span>
              </div>
            </div>
          </div>
        </div>
        """

    if stype == "thank_you":
        mid_html = ""
        if s.get("qr_mid"):
            mid_html = f"""
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_mid'])}" alt="LinkedIn QR"/>
                <span>{html.escape(s['qr_mid_label'])}</span>
              </div>
            """
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="speaker-fan-bg">
            <img src="assets/bg_speaker_fan.png" alt="Fan Background"/>
          </div>
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <span class="prop-badge-abs">Google Developer Expert</span>
          <div class="thankyou-right">
            <div class="thankyou-text">
              <h1>{html.escape(s['title'])}</h1>
              <p>{html.escape(s['subtitle']).replace(chr(10), '<br/>')}</p>
            </div>
            <div class="thankyou-qrs">
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_top'])}" alt="Codelab QR"/>
                <span>{html.escape(s['qr_top_label'])}</span>
              </div>
              {mid_html}
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_bottom'])}" alt="GitHub QR"/>
                <span>{html.escape(s['qr_bottom_label'])}</span>
              </div>
            </div>
          </div>
        </div>
        """

    if stype == "section_poll":
        p = s["poll"]
        opts = "".join(f"<li onclick=\"this.classList.toggle('voted')\">{html.escape(o)} <span class='vote-pill'>Click to Vote</span></li>" for o in p["options"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="section-poll-wrap">
            <img class="section-robot-icon" src="assets/{html.escape(s['icon'])}" alt="Agent Icon"/>
            <h2>{html.escape(s['title']).replace(chr(10), '<br/>')}</h2>
            <div class="interactive-poll-card">
              <div class="poll-q">{html.escape(p['question'])}</div>
              <ul class="poll-opts">{opts}</ul>
              <button class="reveal-btn" onclick="this.nextElementSibling.classList.toggle('visible')">✨ Reveal Takeaway</button>
              <div class="poll-answer">💡 {html.escape(p['answer'])}</div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "agent_triad":
        b0, b1, b2 = s["boxes"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="triad-headline">
            An AI coding agent is a system that uses a <span class="hl-blue">model</span> to reason, an <span class="hl-blue">agent harness</span> to plan &amp; execute, and <span class="hl-blue">MCP &amp; skills</span> to access authoritative knowledge and tools.
          </div>
          <div class="triad-row">
            <div class="triad-box">
              <img src="assets/{html.escape(b0['icon'])}" alt="Tools"/>
              <h3>{html.escape(b0['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box triad-center">
              <img src="assets/{html.escape(b1['icon'])}" alt="Agent"/>
              <h3>{html.escape(b1['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box">
              <img src="assets/{html.escape(b2['icon'])}" alt="Model"/>
              <h3>{html.escape(b2['label']).replace(chr(10), '<br/>')}</h3>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "objectives_card":
        b_html = "".join(f"<li><strong class='hl-blue'>• {html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="blue-outline-card">
            <p class="card-intro">{html.escape(s['intro'])}</p>
            <ul class="obj-list">{b_html}</ul>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "arch_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              <p class="body-p">{html.escape(s['intro'])}</p>
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right center-img-box">
              <img class="arch-img zoomable" src="assets/{html.escape(s['image'])}" alt="Architecture Diagram" onclick="openLightbox(this.src)"/>
              <span class="click-hint">🔍 Click diagram to enlarge full-screen</span>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "three_tech":
        cols_html = ""
        for c in s["cols"]:
            cols_html += f"""
            <div class="tech-col-card">
              <img src="assets/{html.escape(c['icon'])}" alt="Tech Icon"/>
              <h3>{html.escape(c['title']).replace(chr(10), '<br/>')}</h3>
              <p>{html.escape(c['body'])}</p>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="three-tech-grid">{cols_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "two_cards_quiz":
        lc, rc, q = s["left_card"], s["right_card"], s["quiz"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["items"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["items"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <h4>{html.escape(lc['subtitle'])}</h4>
              <ul class="clean-bullets">{li_l}</ul>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <h4>{html.escape(rc['subtitle'])}</h4>
              <ul class="clean-bullets">{li_r}</ul>
            </div>
          </div>
          <div class="quiz-banner">
            <div class="quiz-q-row">
              <span>{html.escape(q['question'])}</span>
              <button class="reveal-btn-sm" onclick="this.parentElement.nextElementSibling.classList.toggle('visible')">Reveal Answer</button>
            </div>
            <div class="quiz-ans-row">{html.escape(q['answer'])}</div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "lab_divider":
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="lab-divider-center">
            <h1>{html.escape(s['title'])}</h1>
            <div class="lab-sub-row">
              <img src="assets/ref_slide11_pic4.png" alt="Google G"/>
              <span>{html.escape(s['subtitle'])}</span>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "code_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        intro_p = f"<p class='body-p'>{html.escape(s['intro'])}</p>" if s.get("intro") else ""
        shot_html = ""
        if s.get("screenshot"):
            shot_html = f"""
            <div class="shot-preview-box">
              <img class="zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Codelab Screenshot" onclick="openLightbox(this.src)"/>
              <span class="click-hint">🔍 Click screenshot to zoom</span>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              {intro_p}
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right">
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s['code_title'])}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
              {shot_html}
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "stepper_split":
        steps_html = ""
        for snum, stitle, sdesc in s["steps"]:
            steps_html += f"""
            <div class="v-step-item">
              <div class="v-step-circle">{html.escape(snum)}</div>
              <div class="v-step-text">
                <h4>{html.escape(stitle)}</h4>
                <code>{html.escape(sdesc)}</code>
              </div>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left v-stepper-card">
              {steps_html}
            </div>
            <div class="col-right">
              <div class="callout-card">
                <span class="callout-pill">{html.escape(s['callout_badge'])}</span>
                <h4>{html.escape(s['callout_title'])}</h4>
                <p>{html.escape(s['callout_body'])}</p>
              </div>
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s['code_title'])}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "two_cards_code":
        lc, rc = s["left_card"], s["right_card"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["bullets"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <h4>{html.escape(lc['subtitle'])}</h4>
              <div class="terminal-card compact">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">Prompt / Snippet</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(lc['code'])}</code></pre>
              </div>
              <ul class="clean-bullets compact-list">{li_l}</ul>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <h4>{html.escape(rc['subtitle'])}</h4>
              <div class="terminal-card compact">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">Prompt / Snippet</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(rc['code'])}</code></pre>
              </div>
              <ul class="clean-bullets compact-list">{li_r}</ul>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "checkpoint_visual":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="split-2col">
            <div class="col-left">
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right center-img-box">
              <img class="arch-img zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Codelab Screenshot" onclick="openLightbox(this.src)"/>
              <p class="img-caption">{html.escape(s.get('caption', ''))} (Click to zoom)</p>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "four_steps":
        steps_html = ""
        for st in s["steps"]:
            hi_cls = "step-card-hi" if st.get("highlight") else ""
            steps_html += f"""
            <div class="four-step-card {hi_cls}">
              <div class="step-num-circle">{html.escape(st['num'])}</div>
              <h4>{html.escape(st['title']).replace(chr(10), '<br/>')}</h4>
              <p>{html.escape(st['body'])}</p>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
          <p class="body-p">{html.escape(s['intro'])}</p>
          <div class="four-steps-grid">{steps_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "verification_cards":
        lc, rc = s["left_card"], s["right_card"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <div class="query-box">
                <strong>User Query:</strong><br/>
                <span>{html.escape(lc['query'])}</span>
              </div>
              <div class="grounded-box">
                <strong class="hl-green">{html.escape(lc['result_title'])}</strong>
                <p>{html.escape(lc['result_body'])}</p>
                <small><strong>Verification Goal:</strong> {html.escape(lc['goal'])}</small>
              </div>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <div class="trap-box trap-red">
                <strong>{html.escape(rc['trap1_title'])}</strong>
                <div class="hl-green">{html.escape(rc['trap1_expected'])}</div>
                <p>{html.escape(rc['trap1_body'])}</p>
              </div>
              <div class="trap-box trap-yellow">
                <strong>{html.escape(rc['trap2_title'])}</strong>
                <div class="hl-green">{html.escape(rc['trap2_expected'])}</div>
                <p>{html.escape(rc['trap2_body'])}</p>
              </div>
            </div>
          </div>
            <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    # ---- NEW TYPES (Location Intelligence deck) ----

    if stype == "hero_media":
        media = s["image"]
        is_gif = media.lower().endswith(".gif")
        tag = f'<img src="assets/{html.escape(media)}" alt="demo"/>' if True else ""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="hero-media-wrap">
            {tag}
          </div>
          <p class="hero-caption">{html.escape(s.get('caption',''))}</p>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "diagram_build":
        steps_html = ""
        for i, st in enumerate(s["build_steps"]):
            steps_html += f"""
            <div class="build-step" data-step="{i}">
              <img src="assets/{html.escape(st['icon'])}" alt="icon"/>
              <div class="build-step-text"><h3>{html.escape(st['label'])}</h3><p>{html.escape(st['desc'])}</p></div>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="build-col">{steps_html}</div>
          <div class="build-summary">{html.escape(s['summary'])}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "split_worlds":
        def _world(w):
            pts = "".join(f"<li>{html.escape(p)}</li>" for p in w["points"])
            return f"""
            <div class="world-card world-{w['color']}">
              <img src="assets/{html.escape(w['icon'])}" alt="icon"/>
              <h3>{html.escape(w['heading'])}</h3>
              <ul>{pts}</ul>
            </div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="worlds-row">
            {_world(s['left'])}
            <div class="worlds-bridge">{html.escape(s['bridge'])}</div>
            {_world(s['right'])}
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "nxm":
        agents = "".join(f'<div class="nxm-node nxm-agent">{html.escape(a)}</div>' for a in s["agents"])
        servers = "".join(f'<div class="nxm-node nxm-server">{html.escape(x)}</div>' for x in s["servers"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="nxm-cols">
            <div class="nxm-col">
              <div class="nxm-caption">{html.escape(s['left_caption'])}</div>
              <div class="nxm-mesh">
                <div class="nxm-side">{agents}</div>
                <div class="nxm-tangle">✕ ✕ ✕<br/>✕ ✕ ✕</div>
                <div class="nxm-side">{servers}</div>
              </div>
            </div>
            <div class="nxm-col">
              <div class="nxm-caption">{html.escape(s['right_caption'])}</div>
              <div class="nxm-mesh">
                <div class="nxm-side">{agents}</div>
                <div class="nxm-hub">MCP</div>
                <div class="nxm-side">{servers}</div>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "tool_catalog":
        accent = s.get("accent","blue")
        rows = "".join(
            f'<div class="tool-row"><code class="tool-name">{html.escape(t)}</code><span class="tool-desc">{html.escape(d)}</span></div>'
            for t, d in s["tools"]
        )
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="tool-cat-head">
            <img src="assets/{html.escape(s['icon'])}" alt="icon"/>
            <div><h2 class="slide-h2">{html.escape(s['title'])}</h2><p class="body-p">{html.escape(s['subtitle'])}</p></div>
          </div>
          <div class="tool-list tool-accent-{accent}">{rows}</div>
          <div class="tool-callout">{html.escape(s['callout'])}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "code_focus":
        callouts = "".join(f"<li><code>{html.escape(k)}</code> — {html.escape(v)}</li>" for k, v in s["callouts"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s.get('lang','python'))}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
            </div>
            <div class="col-right">
              <div class="blue-outline-card">
                <p class="card-intro">The three control surfaces:</p>
                <ul class="obj-list">{callouts}</ul>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "journey_storyboard":
        rows = ""
        for tag, q, tool, res, color in s["steps"]:
            rows += f"""
            <div class="journey-row journey-{color}">
              <span class="journey-tag">{html.escape(tag)}</span>
              <span class="journey-q">{html.escape(q)}</span>
              <span class="journey-tool">{html.escape(tool)}</span>
              <span class="journey-res">{html.escape(res)}</span>
            </div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="journey-table">{rows}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    return ""


def get_slide_title(s):
    if "title" in s:
        return s["title"].replace("\n", " ")
    if "headline" in s:
        return "Anatomy of an AI Coding Agent"
    if "left_card" in s and "right_card" in s:
        return f"{s['left_card']['title']} & {s['right_card']['title']}"
    return f"Slide {s['num']}"


def build_html_deck(output_path):
    slides_dom = []
    notes_json = []
    for s in SLIDES_DATA:
        active = "active" if s["num"] == 1 else ""
        stitle = get_slide_title(s)
        slides_dom.append(
            f'<section class="slide {active}" data-slide="{s["num"]}" data-title="{html.escape(stitle)}" data-module="{html.escape(s["module"])}" data-time="{html.escape(s["time"])}">'
            f'{render_slide_inner_html(s)}'
            f'</section>'
        )
        notes_json.append({
            "num": s["num"],
            "title": stitle,
            "module": s["module"],
            "time": s["time"],
            "notes": s["notes"],
        })

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Location Intelligence ADK Agent — MCP servers for BigQuery &amp; Google Maps — Workshop Deck</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --g-blue: #1A73E8;
      --g-blue-dark: #174EA6;
      --g-blue-bg: #E8F0FE;
      --g-red: #EA4335;
      --g-red-dark: #C5221F;
      --g-red-bg: #FCE8E6;
      --g-yellow: #FBBC04;
      --g-yellow-bg: #FEF7E0;
      --g-green: #34A853;
      --g-green-dark: #137333;
      --g-dark: #202124;
      --g-gray: #5F6368;
      --g-border: #DADCE0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Google Sans', 'Roboto', system-ui, sans-serif;
      background: #111318;
      color: var(--g-dark);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      display: flex;
      flex-direction: column;
    }}
    /* Main viewport scaling 16:9 canvas */
    #deck-viewport {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
      padding: 12px;
    }}
    .slide {{
      display: none;
      width: min(96vw, calc((100vh - 64px) * 16 / 9));
      aspect-ratio: 16 / 9;
      background: #FFFFFF;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.55);
      position: relative;
      overflow: hidden;
    }}
    body.notes-open .slide {{
      width: min(94vw, calc((100vh - 245px) * 16 / 9));
    }}
    .slide.active {{ display: block; }}
    .slide-canvas {{
      width: 100%;
      height: 100%;
      position: relative;
      padding: 2.2% 4.2%;
      display: flex;
      flex-direction: column;
    }}
    /* Top & Bottom Master Branding */
    .slide-top-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.2%;
      min-height: 36px;
    }}
    .gcl-logo-sm {{ height: 34px; object-fit: contain; }}
    .gcl-logo {{ position: absolute; top: 4.5%; left: 4.5%; height: 46px; z-index: 5; }}
    .gcl-footer {{ position: absolute; bottom: 2.8%; left: 4.2%; height: 15px; opacity: 0.85; }}
    .prop-badge {{ font-size: 0.78rem; color: var(--g-gray); font-weight: 500; }}
    .prop-badge-abs {{ position: absolute; top: 4.5%; right: 4.2%; font-size: 0.78rem; color: var(--g-gray); z-index: 5; }}
    .module-pill {{
      background: #F1F3F4;
      color: var(--g-gray);
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
    }}

    /* Cover Slide */
    .slide-cover {{
      padding: 0;
      flex-direction: row;
      align-items: center;
    }}
    .cover-left {{
      width: 52%;
      padding: 8% 3% 4% 4.8%;
      z-index: 3;
    }}
    .pill-badge {{
      display: inline-block;
      background: var(--g-blue-bg);
      color: var(--g-blue);
      font-weight: 700;
      font-size: 0.9rem;
      padding: 6px 16px;
      border-radius: 999px;
      border: 1.5px solid var(--g-blue);
      margin-bottom: 18px;
    }}
    .cover-title {{
      font-size: clamp(1.7rem, 3.1vw, 3.1rem);
      line-height: 1.16;
      font-weight: 700;
      color: var(--g-dark);
      margin-bottom: 18px;
    }}
    .cover-subtitle {{
      font-size: clamp(0.95rem, 1.35vw, 1.3rem);
      color: var(--g-gray);
      line-height: 1.45;
      margin-bottom: 22px;
    }}
    .cover-meta {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--g-blue-dark);
    }}
    .cover-right {{
      width: 48%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }}
    .cover-right img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    /* QR Hub Slide */
    .center-title {{ text-align: center; font-size: clamp(1.5rem, 2.5vw, 2.4rem); font-weight: 700; margin-bottom: 4px; }}
    .center-subtitle {{ text-align: center; font-size: 1rem; color: var(--g-gray); margin-bottom: 18px; }}
    .qr-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2.2%;
      flex: 1;
      margin-bottom: 3.5%;
    }}
    .qr-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}
    .qr-icon-badge {{
      width: 40px; height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4285F4, #669DF6);
      color: #fff;
      font-family: 'Roboto Mono', monospace;
      font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      margin-bottom: 8px;
    }}
    .qr-card h3 {{ font-size: 1.05rem; margin-bottom: 4px; }}
    .qr-link {{ font-size: 0.84rem; color: var(--g-blue); font-weight: 600; text-decoration: underline; margin-bottom: 6px; word-break: break-all; }}
    .qr-card p {{ font-size: 0.82rem; color: var(--g-gray); margin-bottom: 10px; line-height: 1.35; }}
    .qr-img {{ width: 145px; height: 145px; object-fit: contain; margin-top: auto; border-radius: 8px; background: #fff; padding: 4px; border: 1px solid #eee; }}

    /* Speaker & Thank You Slide */
    .slide-speaker {{ padding: 0; flex-direction: row; align-items: center; }}
    .speaker-fan-bg {{ position: absolute; left: 0; top: 0; width: 48%; height: 100%; z-index: 1; }}
    .speaker-fan-bg img {{ width: 100%; height: 100%; object-fit: cover; }}
    .speaker-content {{
      position: relative; z-index: 3;
      display: flex; align-items: center;
      width: 100%; height: 100%;
      padding: 6% 5% 6% 7%;
      gap: 6%;
    }}
    .speaker-photo-wrap img {{
      width: clamp(200px, 27vw, 330px);
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 22px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.28);
      border: 4px solid #fff;
    }}
    .speaker-Bio-text h1 {{ font-size: clamp(2.2rem, 3.8vw, 3.8rem); line-height: 1.08; margin-bottom: 16px; }}
    .role-line {{ font-size: clamp(1.1rem, 1.6vw, 1.55rem); color: #3C4043; margin-bottom: 8px; font-weight: 500; }}
    .speaker-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }}
    .tag-chip {{ background: var(--g-blue-bg); color: var(--g-blue-dark); padding: 5px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; }}
    .thankyou-right {{
      margin-left: 46%;
      width: 54%;
      padding: 5% 4.5% 5% 2%;
      z-index: 3;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
    }}
    .thankyou-text h1 {{ font-size: clamp(2.4rem, 4.2vw, 4.2rem); margin-bottom: 12px; }}
    .thankyou-text p {{ font-size: 1.05rem; color: var(--g-gray); line-height: 1.5; }}
    .thankyou-qrs {{ display: flex; flex-direction: column; gap: 18px; }}
    .ty-qr-box {{ display: flex; flex-direction: column; align-items: center; text-align: center; background: #F8F9FA; padding: 10px; border-radius: 12px; border: 1px solid var(--g-border); width: 185px; }}
    .ty-qr-box img {{ width: 125px; height: 125px; margin-bottom: 6px; }}
    .ty-qr-box span {{ font-size: 0.72rem; color: var(--g-blue-dark); font-weight: 600; line-height: 1.25; }}

    /* Section Poll Slide */
    .section-poll-wrap {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; max-width: 88%; margin: 0 auto; }}
    .section-robot-icon {{ width: 64px; height: 64px; margin-bottom: 8px; }}
    .section-poll-wrap h2 {{ font-size: clamp(1.6rem, 2.6vw, 2.5rem); margin-bottom: 16px; line-height: 1.18; }}
    .interactive-poll-card {{
      width: 100%;
      background: var(--g-blue-bg);
      border: 2px solid var(--g-blue);
      border-radius: 14px;
      padding: 16px 22px;
      text-align: left;
    }}
    .poll-q {{ font-size: 1.05rem; font-weight: 700; color: var(--g-blue-dark); margin-bottom: 10px; }}
    .poll-opts {{ list-style: none; display: flex; flex-direction: column; gap: 7px; margin-bottom: 12px; }}
    .poll-opts li {{
      background: #fff;
      border: 1.5px solid #BBD6FB;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.94rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.15s;
    }}
    .poll-opts li:hover, .poll-opts li.voted {{ background: #D2E3FC; border-color: var(--g-blue); font-weight: 600; }}
    .vote-pill {{ font-size: 0.75rem; background: var(--g-blue); color: #fff; padding: 2px 9px; border-radius: 999px; }}
    .reveal-btn, .reveal-btn-sm {{
      background: var(--g-blue); color: #fff; border: none;
      padding: 7px 14px; border-radius: 8px; font-weight: 600;
      cursor: pointer; font-size: 0.85rem;
    }}
    .reveal-btn:hover, .reveal-btn-sm:hover {{ background: var(--g-blue-dark); }}
    .poll-answer, .quiz-ans-row {{
      display: none;
      margin-top: 10px;
      padding: 9px 12px;
      background: #E6F4EA;
      border-left: 4px solid var(--g-green);
      border-radius: 6px;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--g-green-dark);
    }}
    .poll-answer.visible, .quiz-ans-row.visible {{ display: block; }}

    /* Triad Slide */
    .triad-headline {{
      font-size: clamp(1.35rem, 2.2vw, 2.15rem);
      font-weight: 700;
      line-height: 1.28;
      max-width: 90%;
      margin: 1.5% auto 4% auto;
    }}
    .hl-blue {{ color: var(--g-blue); }}
    .hl-green {{ color: var(--g-green-dark); }}
    .triad-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex: 1;
      margin-bottom: 4%;
    }}
    .triad-box {{
      flex: 1;
      background: #F1F3F4;
      border: 1.5px solid var(--g-border);
      border-radius: 14px;
      padding: 28px 16px 22px 16px;
      text-align: center;
      position: relative;
    }}
    .triad-center {{ border: 2px solid var(--g-blue); background: var(--g-blue-bg); }}
    .triad-box img {{ width: 58px; height: 58px; margin-bottom: 10px; }}
    .triad-box h3 {{ font-size: 1.25rem; line-height: 1.3; }}
    .triad-arrow {{ font-size: 2rem; color: var(--g-gray); font-weight: 700; }}

    /* Standard Content & Split Layouts */
    .slide-h2 {{ font-size: clamp(1.35rem, 2.1vw, 2.05rem); font-weight: 700; margin-bottom: 8px; color: var(--g-dark); }}
    .sub-blue {{ font-size: clamp(1rem, 1.3vw, 1.22rem); color: var(--g-blue); font-weight: 700; margin-bottom: 8px; }}
    .body-p {{ font-size: 0.92rem; color: #3C4043; line-height: 1.45; margin-bottom: 10px; }}
    .blue-outline-card {{
      border: 2.5px solid var(--g-blue);
      border-radius: 16px;
      padding: 20px 26px;
      flex: 1;
      margin-bottom: 3.5%;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .card-intro {{ font-size: 1.05rem; font-weight: 500; margin-bottom: 14px; color: var(--g-dark); line-height: 1.4; }}
    .obj-list {{ list-style: none; display: flex; flex-direction: column; gap: 12px; font-size: 0.96rem; line-height: 1.42; }}
    .split-2col {{
      display: grid;
      grid-template-columns: 47% 51%;
      gap: 2%;
      flex: 1;
      margin-bottom: 3.2%;
      min-height: 0;
    }}
    .col-left, .col-right {{ display: flex; flex-direction: column; min-height: 0; }}
    .clean-bullets {{ list-style: none; display: flex; flex-direction: column; gap: 9px; font-size: 0.89rem; line-height: 1.38; color: #3C4043; }}
    .clean-bullets li strong {{ color: var(--g-blue-dark); }}
    .compact-list {{ gap: 6px; font-size: 0.84rem; margin-top: 8px; }}
    .center-img-box {{ align-items: center; justify-content: center; background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px; padding: 10px; }}
    .arch-img {{ max-width: 100%; max-height: 88%; object-fit: contain; border-radius: 8px; cursor: zoom-in; }}
    .click-hint, .img-caption {{ font-size: 0.76rem; color: var(--g-gray); margin-top: 5px; text-align: center; }}

    /* Three Tech Columns */
    .three-tech-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2.5%;
      flex: 1;
      margin: 1.5% 0 4% 0;
    }}
    .tech-col-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }}
    .tech-col-card img {{ width: 54px; height: 54px; object-fit: contain; margin-bottom: 14px; }}
    .tech-col-card h3 {{ font-size: 1.15rem; margin-bottom: 10px; line-height: 1.28; }}
    .tech-col-card p {{ font-size: 0.9rem; color: #3C4043; line-height: 1.45; }}

    /* Dual Cards & Quiz Banner */
    .dual-cards-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2.2%;
      flex: 1;
      min-height: 0;
      margin-bottom: 10px;
    }}
    .bordered-card {{
      border-radius: 14px;
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      min-height: 0;
      background: #fff;
    }}
    .card-blue {{ border: 2.5px solid var(--g-blue); }}
    .card-blue h3 {{ color: var(--g-blue); font-size: 1.18rem; margin-bottom: 2px; }}
    .card-red {{ border: 2.5px solid var(--g-red); }}
    .card-red h3 {{ color: var(--g-red-dark); font-size: 1.18rem; margin-bottom: 2px; }}
    .bordered-card h4 {{ font-size: 0.86rem; color: var(--g-gray); margin-bottom: 8px; font-weight: 600; }}
    .quiz-banner {{
      background: var(--g-yellow-bg);
      border: 1.5px solid var(--g-yellow);
      border-radius: 10px;
      padding: 8px 14px;
      margin-bottom: 2.8%;
    }}
    .quiz-q-row {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 0.86rem; font-weight: 700; color: #B06000; }}

    /* Lab Divider */
    .lab-divider-center {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .lab-divider-center h1 {{ font-size: clamp(2.4rem, 4vw, 3.8rem); margin-bottom: 18px; }}
    .lab-sub-row {{ display: flex; align-items: center; gap: 14px; font-size: 1.35rem; color: var(--g-blue); font-weight: 700; }}
    .lab-sub-row img {{ width: 36px; height: 36px; }}

    /* Terminal Code Box */
    .terminal-card {{
      background: var(--g-dark);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      border: 1px solid #3C4043;
      margin-bottom: 8px;
    }}
    .terminal-card.compact {{ max-height: 46%; }}
    .term-header {{
      background: #2D2E31;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .term-dots {{ display: flex; gap: 6px; }}
    .term-dots span {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .dot-r {{ background: #EA4335; }}
    .dot-y {{ background: #FBBC04; }}
    .dot-g {{ background: #34A853; }}
    .term-title {{ font-family: 'Roboto Mono', monospace; font-size: 0.75rem; color: #9AA0A6; }}
    .copy-btn {{
      background: #3C4043; color: #E8EAED; border: 1px solid #5F6368;
      border-radius: 5px; padding: 2px 8px; font-size: 0.72rem; cursor: pointer;
    }}
    .copy-btn:hover {{ background: var(--g-blue); border-color: var(--g-blue); }}
    .term-body {{
      padding: 10px 14px;
      color: #E8EAED;
      font-family: 'Roboto Mono', monospace;
      font-size: 0.76rem;
      line-height: 1.38;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-y: auto;
    }}
    .shot-preview-box {{
      flex: 1;
      min-height: 0;
      background: #F8F9FA;
      border: 1px solid var(--g-border);
      border-radius: 8px;
      padding: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    .shot-preview-box img {{ max-width: 100%; max-height: 135px; object-fit: contain; border-radius: 4px; cursor: zoom-in; }}

    /* Vertical Stepper & Callout */
    .v-stepper-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      justify-content: space-around;
    }}
    .v-step-item {{ display: flex; align-items: flex-start; gap: 14px; }}
    .v-step-circle {{
      width: 36px; height: 36px; border-radius: 50%;
      background: var(--g-blue); color: #fff; font-weight: 700;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .v-step-text h4 {{ font-size: 1rem; margin-bottom: 3px; }}
    .v-step-text code {{ font-family: 'Roboto Mono', monospace; font-size: 0.82rem; color: var(--g-green-dark); }}
    .callout-card {{
      background: #fff; border: 1.5px solid var(--g-border);
      border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
    }}
    .callout-pill {{
      display: inline-block; background: var(--g-red-bg); color: var(--g-red-dark);
      font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; margin-bottom: 6px;
    }}
    .callout-card h4 {{ font-size: 0.98rem; margin-bottom: 4px; }}
    .callout-card p {{ font-size: 0.83rem; color: #3C4043; line-height: 1.36; }}

    /* Four Steps Grid */
    .four-steps-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.8%;
      flex: 1;
      margin-bottom: 3.5%;
    }}
    .four-step-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
    }}
    .four-step-card.step-card-hi {{ border: 2.5px solid var(--g-blue); background: #fff; }}
    .step-num-circle {{
      width: 36px; height: 36px; border-radius: 50%;
      background: var(--g-blue-bg); color: var(--g-blue);
      font-weight: 700; display: flex; align-items: center; justify-content: center;
      margin-bottom: 12px;
    }}
    .step-card-hi .step-num-circle {{ background: var(--g-blue); color: #fff; }}
    .four-step-card h4 {{ font-size: 0.98rem; margin-bottom: 8px; line-height: 1.28; }}
    .step-card-hi h4 {{ color: var(--g-blue); }}
    .four-step-card p {{ font-size: 0.83rem; color: #3C4043; line-height: 1.4; }}

    /* Verification Cards */
    .query-box {{ background: #F1F3F4; padding: 10px 12px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 10px; }}
    .grounded-box {{ background: var(--g-blue-bg); border: 1px solid var(--g-blue); padding: 12px; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .trap-box {{ padding: 10px 12px; border-radius: 8px; font-size: 0.83rem; line-height: 1.35; margin-bottom: 8px; flex: 1; }}
    .trap-red {{ background: var(--g-red-bg); border: 1px solid var(--g-red); }}
    .trap-yellow {{ background: var(--g-yellow-bg); border: 1px solid var(--g-yellow); }}

    /* Lab Timer Widget */
    .title-with-timer {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px; }}
    .lab-timer-widget {{
      display: flex; align-items: center; gap: 8px;
      background: var(--g-blue-bg); border: 1.5px solid var(--g-blue);
      padding: 4px 12px; border-radius: 999px; font-size: 0.82rem;
    }}
    .timer-label {{ font-weight: 700; color: var(--g-blue-dark); }}
    .timer-display {{ font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 0.95rem; color: var(--g-red-dark); min-width: 48px; }}
    .timer-btn {{
      background: var(--g-blue); color: #fff; border: none;
      border-radius: 999px; padding: 3px 10px; font-size: 0.74rem; font-weight: 600; cursor: pointer;
    }}
    .timer-btn.secondary {{ background: #5F6368; }}

    /* Speaker Notes Teleprompter Drawer (Press S) */
    #notes-drawer {{
      display: none;
      height: 185px;
      background: #1E2028;
      border-top: 2px solid var(--g-blue);
      color: #E8EAED;
      padding: 12px 24px;
      overflow-y: auto;
      font-size: 0.95rem;
      line-height: 1.5;
    }}
    body.notes-open #notes-drawer {{ display: block; }}
    #notes-drawer-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 6px; font-size: 0.8rem; color: #8AB4F8; font-weight: 700;
    }}
    #notes-drawer-content {{ white-space: pre-wrap; font-family: 'Roboto', sans-serif; }}

    /* Bottom Presenter Control Bar */
    #presenter-bar {{
      height: 46px;
      background: #181A20;
      border-top: 1px solid #2D3139;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      color: #E8EAED;
      font-size: 0.84rem;
      user-select: none;
    }}
    .bar-group {{ display: flex; align-items: center; gap: 8px; }}
    .bar-btn {{
      background: #282C34; color: #E8EAED; border: 1px solid #3E4451;
      padding: 5px 11px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;
      cursor: pointer; transition: all 0.15s;
    }}
    .bar-btn:hover {{ background: var(--g-blue); border-color: var(--g-blue); }}
    .bar-btn.active-toggle {{ background: var(--g-blue); border-color: var(--g-blue); }}
    #progress-track {{ width: 140px; height: 6px; background: #2D3139; border-radius: 99px; overflow: hidden; }}
    #progress-fill {{ height: 100%; background: var(--g-blue); width: 3%; transition: width 0.2s; }}

    /* Slide Grid Modal (Press G) */
    #grid-modal, #lightbox-modal {{
      display: none;
      position: fixed; inset: 0;
      background: rgba(15, 17, 23, 0.92);
      z-index: 100;
      padding: 32px;
      overflow-y: auto;
    }}
    #grid-modal.open, #lightbox-modal.open {{ display: flex; flex-direction: column; }}
    .grid-cards {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .grid-item {{
      background: #20232A; border: 1.5px solid #3C4043; border-radius: 8px;
      padding: 12px; color: #E8EAED; cursor: pointer;
    }}
    .grid-item:hover, .grid-item.current {{ border-color: var(--g-blue); background: #263147; }}
    .grid-item-num {{ font-size: 0.75rem; color: #8AB4F8; font-weight: 700; margin-bottom: 4px; }}
    .grid-item-title {{ font-size: 0.88rem; font-weight: 600; }}
    #lightbox-modal {{ align-items: center; justify-content: center; cursor: zoom-out; }}
    #lightbox-img {{ max-width: 94vw; max-height: 90vh; border-radius: 10px; box-shadow: 0 12px 40px rgba(0,0,0,0.8); }}

    /* ---- NEW slide types (Location Intelligence) ---- */
    .hero-media-wrap {{
      flex: 1; display: flex; align-items: center; justify-content: center;
      background: #0d1117; border-radius: 12px; overflow: hidden; margin: 1% 0;
    }}
    .hero-media-wrap img {{ width: 100%; height: 100%; object-fit: contain; }}
    .hero-caption {{ text-align: center; font-size: 0.8rem; color: var(--g-gray); margin-bottom: 2%; }}

    .build-col {{ display: flex; flex-direction: column; gap: 2.2%; flex: 1; margin-top: 1%; }}
    .build-step {{
      display: flex; align-items: center; gap: 18px;
      background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px;
      padding: 2.4% 3%;
    }}
    .build-step img {{ width: 46px; height: 46px; object-fit: contain; flex: 0 0 auto; }}
    .build-step-text h3 {{ font-size: 1.1rem; font-weight: 700; color: var(--g-blue-dark); margin-bottom: 2px; }}
    .build-step-text p {{ font-size: 0.92rem; color: var(--g-gray); line-height: 1.35; }}
    .build-summary {{
      margin-top: 2%; text-align: center; font-weight: 700; font-size: 1.05rem;
      color: var(--g-green-dark); background: #E6F4EA; border-radius: 999px; padding: 10px 18px;
    }}

    .worlds-row {{ display: flex; align-items: stretch; gap: 2%; flex: 1; margin-top: 2%; }}
    .world-card {{
      flex: 1; border-radius: 14px; padding: 3%; border: 2px solid var(--g-border);
      display: flex; flex-direction: column;
    }}
    .world-card img {{ width: 52px; height: 52px; object-fit: contain; margin-bottom: 10px; }}
    .world-card h3 {{ font-size: 1.15rem; margin-bottom: 10px; }}
    .world-card ul {{ margin-left: 18px; font-size: 0.95rem; color: var(--g-dark); line-height: 1.6; }}
    .world-blue {{ border-color: var(--g-blue); background: var(--g-blue-bg); }}
    .world-blue h3 {{ color: var(--g-blue-dark); }}
    .world-green {{ border-color: var(--g-green); background: #E6F4EA; }}
    .world-green h3 {{ color: var(--g-green-dark); }}
    .worlds-bridge {{
      align-self: center; flex: 0 0 16%; text-align: center; font-weight: 700;
      font-size: 0.9rem; color: var(--g-dark);
      background: var(--g-yellow-bg); border: 2px dashed var(--g-yellow);
      border-radius: 12px; padding: 12px;
    }}

    .nxm-cols {{ display: flex; gap: 3%; flex: 1; margin-top: 1%; }}
    .nxm-col {{ flex: 1; display: flex; flex-direction: column; }}
    .nxm-caption {{ text-align: center; font-size: 0.9rem; font-weight: 600; color: var(--g-gray); margin-bottom: 8px; }}
    .nxm-mesh {{
      flex: 1; display: flex; align-items: center; justify-content: space-between;
      background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px; padding: 4%;
    }}
    .nxm-side {{ display: flex; flex-direction: column; gap: 12px; }}
    .nxm-node {{
      padding: 10px 14px; border-radius: 10px; font-weight: 600; font-size: 0.85rem; text-align: center;
      border: 1.5px solid var(--g-border); background: #fff;
    }}
    .nxm-agent {{ border-color: var(--g-blue); color: var(--g-blue-dark); }}
    .nxm-server {{ border-color: var(--g-green); color: var(--g-green-dark); }}
    .nxm-tangle {{ color: var(--g-red); font-size: 1.4rem; text-align: center; line-height: 1.1; }}
    .nxm-hub {{
      align-self: center; background: var(--g-blue); color: #fff; font-weight: 700;
      padding: 16px 22px; border-radius: 999px; font-size: 1.1rem;
      box-shadow: 0 6px 18px rgba(26,115,232,0.35);
    }}

    .tool-cat-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 1%; }}
    .tool-cat-head img {{ width: 54px; height: 54px; object-fit: contain; }}
    .tool-list {{ display: flex; flex-direction: column; gap: 1.4%; margin-top: 1%; }}
    .tool-row {{
      display: flex; align-items: center; gap: 16px;
      background: #fff; border: 1.5px solid var(--g-border); border-radius: 10px; padding: 1.4% 2%;
    }}
    .tool-name {{
      font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 0.95rem;
      background: #F1F3F4; padding: 4px 10px; border-radius: 6px; flex: 0 0 34%;
    }}
    .tool-accent-blue .tool-name {{ color: var(--g-blue-dark); }}
    .tool-accent-green .tool-name {{ color: var(--g-green-dark); }}
    .tool-desc {{ font-size: 0.9rem; color: var(--g-dark); }}
    .tool-callout {{
      margin-top: 2%; font-size: 0.92rem; font-weight: 600; color: var(--g-dark);
      background: var(--g-yellow-bg); border-left: 4px solid var(--g-yellow);
      border-radius: 8px; padding: 12px 16px;
    }}

    .journey-table {{ display: flex; flex-direction: column; gap: 1.6%; flex: 1; margin-top: 1%; }}
    .journey-row {{
      display: grid; grid-template-columns: 7% 44% 26% 23%; align-items: center;
      gap: 1.5%; padding: 1.5% 2%; border-radius: 10px; border: 1.5px solid var(--g-border); background: #fff;
    }}
    .journey-tag {{ font-weight: 800; font-size: 1rem; }}
    .journey-blue .journey-tag {{ color: var(--g-blue); }}
    .journey-green .journey-tag {{ color: var(--g-green); }}
    .journey-yellow .journey-tag {{ color: #B06000; }}
    .journey-q {{ font-size: 0.92rem; font-weight: 600; color: var(--g-dark); }}
    .journey-tool {{ font-family: 'Roboto Mono', monospace; font-size: 0.8rem; color: var(--g-gray); }}
    .journey-res {{ font-size: 0.82rem; font-weight: 700; color: var(--g-dark); text-align: right; }}
    .journey-blue {{ border-left: 5px solid var(--g-blue); }}
    .journey-green {{ border-left: 5px solid var(--g-green); }}
    .journey-yellow {{ border-left: 5px solid var(--g-yellow); }}
  </style>
</head>
<body>
  <div id="deck-viewport">
    {''.join(slides_dom)}
  </div>

  <!-- On-Screen Speaker Notes Teleprompter Drawer (Toggle with 'S') -->
  <div id="notes-drawer">
    <div id="notes-drawer-header">
      <span id="notes-slide-meta">🎤 SPEAKER NOTES &amp; TALK SCRIPT</span>
      <span>Tip: Press <strong>P</strong> to pop out Dual-Screen Presenter Console | Press <strong>S</strong> to hide drawer</span>
    </div>
    <div id="notes-drawer-content"></div>
  </div>

  <!-- Bottom Presenter Toolbar -->
  <div id="presenter-bar">
    <div class="bar-group">
      <button class="bar-btn" onclick="prevSlide()">◀ Prev</button>
      <span id="slide-counter" style="min-width: 72px; text-align:center; font-weight:700;">1 / {len(SLIDES_DATA)}</span>
      <button class="bar-btn" onclick="nextSlide()">Next ▶</button>
      <div id="progress-track"><div id="progress-fill"></div></div>
      <span id="module-indicator" style="color:#9AA0A6; font-size:0.78rem; margin-left:8px;"></span>
    </div>
    <div class="bar-group">
      <span id="talk-clock" style="font-family:'Roboto Mono',monospace; color:#FBBC04; font-weight:700;">⏱️ Talk Clock: 00:00 / 75:00</span>
      <button class="bar-btn" onclick="toggleTalkClock()" id="clock-btn">Start Clock</button>
      <button class="bar-btn" onclick="toggleNotesDrawer()" id="notes-btn">📝 Speaker Notes (S)</button>
      <button class="bar-btn" onclick="openPresenterPopup()">🖥️ Presenter View (P)</button>
      <button class="bar-btn" onclick="toggleGrid()">⊞ All Slides (G)</button>
      <button class="bar-btn" onclick="toggleFullscreen()">⛶ Fullscreen (F)</button>
    </div>
  </div>

  <!-- All-Slides Overview Grid Modal -->
  <div id="grid-modal">
    <div style="display:flex; justify-content:space-between; align-items:center; color:#fff;">
      <h2>All Workshop Slides — Click Any Slide to Jump</h2>
      <button class="bar-btn" onclick="toggleGrid()">✕ Close (ESC)</button>
    </div>
    <div class="grid-cards" id="grid-cards-container"></div>
  </div>

  <!-- Lightbox Modal for Diagrams & Screenshots -->
  <div id="lightbox-modal" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="Enlarged View"/>
  </div>

  <script>
    const SLIDE_NOTES = {json.dumps(notes_json)};
    const totalSlides = SLIDE_NOTES.length;
    let currentSlide = 1;
    const channel = new BroadcastChannel('location_intel_adk_mcp_sync');

    function showSlide(n, broadcast = true) {{
      if (n < 1) n = 1;
      if (n > totalSlides) n = totalSlides;
      currentSlide = n;
      document.querySelectorAll('.slide').forEach(el => {{
        el.classList.toggle('active', parseInt(el.dataset.slide) === currentSlide);
      }});
      document.getElementById('slide-counter').textContent = `${{currentSlide}} / ${{totalSlides}}`;
      document.getElementById('progress-fill').style.width = `${{(currentSlide / totalSlides) * 100}}%`;
      const meta = SLIDE_NOTES[currentSlide - 1];
      document.getElementById('module-indicator').textContent = `${{meta.module}} (${{meta.time}})`;
      document.getElementById('notes-slide-meta').textContent = `🎤 SLIDE ${{meta.num}}: ${{meta.title}} — ${{meta.time}}`;
      document.getElementById('notes-drawer-content').textContent = meta.notes;
      window.location.hash = `slide-${{currentSlide}}`;
      if (broadcast) {{
        channel.postMessage({{ type: 'SLIDE_CHANGE', slide: currentSlide }});
      }}
    }}

    function nextSlide() {{ showSlide(currentSlide + 1); }}
    function prevSlide() {{ showSlide(currentSlide - 1); }}

    function toggleNotesDrawer() {{
      document.body.classList.toggle('notes-open');
      document.getElementById('notes-btn').classList.toggle('active-toggle');
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen();
      }} else {{
        document.exitFullscreen();
      }}
    }}

    function openLightbox(src) {{
      document.getElementById('lightbox-img').src = src;
      document.getElementById('lightbox-modal').classList.add('open');
    }}
    function closeLightbox() {{
      document.getElementById('lightbox-modal').classList.remove('open');
    }}

    function copyCode(btn) {{
      const code = btn.closest('.terminal-card').querySelector('code').innerText;
      navigator.clipboard.writeText(code);
      const old = btn.textContent;
      btn.textContent = '✅ Copied!';
      setTimeout(() => btn.textContent = old, 1500);
    }}

    // Lab Checkpoint Timers
    const labIntervals = {{}};
    function toggleLabTimer(slideNum) {{
      const widget = document.getElementById(`timer-${{slideNum}}`);
      const disp = document.getElementById(`timer-disp-${{slideNum}}`);
      if (labIntervals[slideNum]) {{
        clearInterval(labIntervals[slideNum]);
        delete labIntervals[slideNum];
        return;
      }}
      let remaining = parseInt(widget.dataset.remaining || widget.dataset.seconds);
      labIntervals[slideNum] = setInterval(() => {{
        if (remaining > 0) remaining--;
        widget.dataset.remaining = remaining;
        const m = String(Math.floor(remaining / 60)).padStart(2, '0');
        const s = String(remaining % 60).padStart(2, '0');
        disp.textContent = `${{m}}:${{s}}`;
        if (remaining === 0) {{
          clearInterval(labIntervals[slideNum]);
          delete labIntervals[slideNum];
        }}
      }}, 1000);
    }}
    function resetLabTimer(slideNum) {{
      if (labIntervals[slideNum]) {{
        clearInterval(labIntervals[slideNum]);
        delete labIntervals[slideNum];
      }}
      const widget = document.getElementById(`timer-${{slideNum}}`);
      const total = parseInt(widget.dataset.seconds);
      widget.dataset.remaining = total;
      const m = String(Math.floor(total / 60)).padStart(2, '0');
      const s = String(total % 60).padStart(2, '0');
      document.getElementById(`timer-disp-${{slideNum}}`).textContent = `${{m}}:${{s}}`;
    }}

    // 75-Minute Overall Talk Clock
    let talkSeconds = 0;
    let talkTimer = null;
    function toggleTalkClock() {{
      const btn = document.getElementById('clock-btn');
      if (talkTimer) {{
        clearInterval(talkTimer);
        talkTimer = null;
        btn.textContent = 'Resume Clock';
      }} else {{
        btn.textContent = 'Pause Clock';
        talkTimer = setInterval(() => {{
          talkSeconds++;
          const m = String(Math.floor(talkSeconds / 60)).padStart(2, '0');
          const s = String(talkSeconds % 60).padStart(2, '0');
          document.getElementById('talk-clock').textContent = `⏱️ Talk Clock: ${{m}}:${{s}} / 75:00`;
        }}, 1000);
      }}
    }}

    // Slide Grid Overview
    function toggleGrid() {{
      const modal = document.getElementById('grid-modal');
      const container = document.getElementById('grid-cards-container');
      container.innerHTML = '';
      SLIDE_NOTES.forEach(s => {{
        const div = document.createElement('div');
        div.className = 'grid-item' + (s.num === currentSlide ? ' current' : '');
        div.innerHTML = `<div class="grid-item-num">Slide ${{s.num}} • ${{s.time}}</div><div class="grid-item-title">${{s.title}}</div>`;
        div.onclick = () => {{ showSlide(s.num); modal.classList.remove('open'); }};
        container.appendChild(div);
      }});
      modal.classList.toggle('open');
    }}

    // Dual-Screen Synchronized Presenter Popup (Press P)
    function openPresenterPopup() {{
      const win = window.open('speaker-notes.html?mode=presenter', 'PresenterConsole', 'width=980,height=760');
      setTimeout(() => channel.postMessage({{ type: 'SLIDE_CHANGE', slide: currentSlide }}), 500);
    }}

    channel.onmessage = (ev) => {{
      if (ev.data && ev.data.type === 'SLIDE_CHANGE') {{
        showSlide(ev.data.slide, false);
      }}
    }};

    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{ e.preventDefault(); nextSlide(); }}
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); prevSlide(); }}
      else if (e.key === 's' || e.key === 'S') {{ toggleNotesDrawer(); }}
      else if (e.key === 'p' || e.key === 'P') {{ openPresenterPopup(); }}
      else if (e.key === 'g' || e.key === 'G') {{ toggleGrid(); }}
      else if (e.key === 'f' || e.key === 'F') {{ toggleFullscreen(); }}
      else if (e.key === 'Escape') {{
        document.getElementById('grid-modal').classList.remove('open');
        closeLightbox();
      }}
    }});

    // Initialize from URL hash if present
    const m = window.location.hash.match(/slide-(\\d+)/);
    showSlide(m ? parseInt(m[1]) : 1);
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"Saved Interactive Web Deck: {output_path}")


# ---------------------------------------------------------------------------
# PART 3: BUILD STANDALONE SPEAKER NOTES CONSOLE (speaker-notes.html)
# ---------------------------------------------------------------------------
def build_speaker_notes_html(output_path):
    notes_cards_html = []
    notes_json = []
    for s in SLIDES_DATA:
        stitle = get_slide_title(s)
        code_val = s.get("code") or (s.get("left_card", {}).get("code", "") + ("\n\n" + s.get("right_card", {}).get("code", "") if s.get("right_card", {}).get("code") else ""))
        notes_json.append({
            "num": s["num"],
            "title": stitle,
            "module": s["module"],
            "time": s["time"],
            "notes": s["notes"],
            "code": code_val,
        })
        code_block = ""
        if code_val:
            code_block = f"""
            <div class="cmd-box">
              <div class="cmd-hdr"><span>Copyable Command / Prompt</span><button onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.innerText); this.textContent='✅ Copied!';">📋 Copy</button></div>
              <pre>{html.escape(code_val)}</pre>
            </div>
            """
        notes_cards_html.append(f"""
        <div class="note-card" id="note-slide-{s['num']}">
          <div class="note-hdr">
            <span class="badge-num">Slide {s['num']} / {len(SLIDES_DATA)}</span>
            <span class="badge-mod">{html.escape(s['module'])}</span>
            <span class="badge-time">⏱️ {html.escape(s['time'])}</span>
            <button class="jump-btn" onclick="syncToSlide({s['num']})">Sync Projector Here ▶</button>
          </div>
          <h2>{html.escape(stitle)}</h2>
          <div class="note-body">{html.escape(s['notes'])}</div>
          {code_block}
        </div>
        """)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Speaker Notes &amp; Teleprompter — Command and Control Workshop</title>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Google Sans', system-ui, sans-serif;
      background: #0F1117;
      color: #E8EAED;
      margin: 0;
      padding: 0;
    }}
    header {{
      position: sticky; top: 0; z-index: 50;
      background: #181B24;
      border-bottom: 2px solid #1A73E8;
      padding: 12px 24px;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 12px;
    }}
    .ctrl-row {{ display: flex; align-items: center; gap: 10px; }}
    button {{
      background: #1A73E8; color: #fff; border: none;
      padding: 7px 14px; border-radius: 6px; font-weight: 600; cursor: pointer;
    }}
    button:hover {{ background: #174EA6; }}
    #live-banner {{
      background: #1E2436; border: 2px solid #4285F4;
      margin: 18px 24px; padding: 18px 22px; border-radius: 12px;
    }}
    #live-banner h3 {{ color: #8AB4F8; margin-bottom: 6px; font-size: 1.2rem; }}
    #live-notes {{ white-space: pre-wrap; font-size: 1.15rem; line-height: 1.55; color: #FFF; }}
    #live-next {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid #3C4043; color: #FBBC04; font-weight: 600; }}
    .container {{ max-width: 980px; margin: 0 auto; padding: 12px 24px 60px 24px; }}
    .note-card {{
      background: #181B24; border: 1.5px solid #2D3242;
      border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
    }}
    .note-card.active-card {{ border-color: #4285F4; box-shadow: 0 0 0 2px rgba(66,133,244,0.35); }}
    .note-hdr {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }}
    .badge-num {{ background: #1A73E8; color: #fff; padding: 3px 10px; border-radius: 99px; font-weight: 700; font-size: 0.8rem; }}
    .badge-mod {{ color: #8AB4F8; font-size: 0.85rem; font-weight: 600; }}
    .badge-time {{ color: #FBBC04; font-size: 0.85rem; font-weight: 600; margin-left: auto; }}
    .jump-btn {{ background: #2D3242; font-size: 0.75rem; padding: 4px 10px; }}
    .note-card h2 {{ font-size: 1.25rem; margin-bottom: 10px; color: #fff; }}
    .note-body {{ white-space: pre-wrap; font-size: 1.02rem; line-height: 1.55; color: #D2D6DF; }}
    .cmd-box {{ margin-top: 12px; background: #0B0D12; border: 1px solid #3C4043; border-radius: 8px; overflow: hidden; }}
    .cmd-hdr {{ background: #20232D; padding: 5px 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #9AA0A6; }}
    .cmd-box pre {{ padding: 10px 12px; font-family: 'Roboto Mono', monospace; font-size: 0.82rem; white-space: pre-wrap; color: #81C995; margin: 0; }}
  </style>
</head>
<body>
  <header>
    <div>
      <strong>🎤 Live Speaker Console &amp; Full Talk Script</strong>
      <span style="color:#9AA0A6; font-size:0.85rem; margin-left:10px;">Synced with Main Presentation Window</span>
    </div>
    <div class="ctrl-row">
      <button onclick="stepSlide(-1)">◀ Prev Slide</button>
      <span id="console-counter" style="font-weight:700; min-width:80px; text-align:center;">Slide 1 / 32</span>
      <button onclick="stepSlide(1)">Next Slide ▶</button>
    </div>
  </header>

  <div id="live-banner">
    <h3 id="live-title">Current Slide: 1</h3>
    <div id="live-notes"></div>
    <div id="live-next">Next Slide: 2</div>
  </div>

  <div class="container">
    <h2 style="margin-bottom:14px; color:#8AB4F8;">All 32 Slides — Continuous Speaker Script &amp; Copy-Paste Prompts</h2>
    {''.join(notes_cards_html)}
  </div>

  <script>
    const NOTES = {json.dumps(notes_json)};
    let cur = 1;
    const channel = new BroadcastChannel('location_intel_adk_mcp_sync');

    function updateConsole(n) {{
      if (n < 1) n = 1;
      if (n > NOTES.length) n = NOTES.length;
      cur = n;
      const item = NOTES[cur - 1];
      const nextItem = NOTES[cur] || null;
      document.getElementById('console-counter').textContent = `Slide ${{cur}} / ${{NOTES.length}}`;
      document.getElementById('live-title').textContent = `LIVE ON SCREEN — Slide ${{item.num}}: ${{item.title}} (${{item.time}})`;
      document.getElementById('live-notes').textContent = item.notes;
      document.getElementById('live-next').textContent = nextItem ? `⏭️ UP NEXT — Slide ${{nextItem.num}}: ${{nextItem.title}} (${{nextItem.time}})` : `🎉 End of Deck`;
      document.querySelectorAll('.note-card').forEach(c => c.classList.remove('active-card'));
      const activeEl = document.getElementById(`note-slide-${{cur}}`);
      if (activeEl) {{
        activeEl.classList.add('active-card');
        activeEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}

    function syncToSlide(n) {{
      updateConsole(n);
      channel.postMessage({{ type: 'SLIDE_CHANGE', slide: n }});
    }}

    function stepSlide(delta) {{
      syncToSlide(cur + delta);
    }}

    channel.onmessage = (ev) => {{
      if (ev.data && ev.data.type === 'SLIDE_CHANGE') {{
        updateConsole(ev.data.slide);
      }}
    }};

    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); stepSlide(1); }}
      else if (e.key === 'ArrowLeft') {{ e.preventDefault(); stepSlide(-1); }}
    }});

    updateConsole(1);
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Saved Speaker Notes Console: {output_path}")


# ---------------------------------------------------------------------------
# PART 4: BUILD MARKDOWN RUNBOOK & VERBATIM SCRIPT (SPEAKER_NOTES_AND_SCRIPT.md)
# ---------------------------------------------------------------------------
def build_markdown_runbook(output_path):
    lines = [
        "# 🎤 Speaker Notes, Facilitator Runbook & Verbatim Talk Script",
        "",
        "## **Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps**",
        "- **Format**: GDE Talk + Interactive Hands-On Workshop (1 hr 15 mins / 75 minutes)",
        "- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)",
        "- **Base Codelab**: [https://codelabs.developers.google.com/adk-mcp-bigquery-maps](https://codelabs.developers.google.com/adk-mcp-bigquery-maps)",
        "",
        "---",
        "",
        "## ⚡ How to Present Directly from This Folder",
        "",
        "1. **Option A — Interactive Web Deck + Dual-Screen Presenter Console (Recommended)**:",
        "   - Run `./present.sh` in this folder (or open `index.html` in Chrome).",
        "   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!",
        "   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.",
        "   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.",
        "2. **Option B — Google Slides / PowerPoint Presenter View**:",
        "   - Upload `Location_Intelligence_ADK_MCP_Workshop.pptx` to Google Slides (File → Import slides / Open) or open in PowerPoint/Keynote.",
        "   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.",
        "3. **Option C — Tablet / Phone Companion**:",
        "   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through every slide's verbatim notes and copy-paste prompts.",
        "",
        "---",
        "",
        "## ⏱️ 75-Minute Pacing Schedule & Checkpoints",
        "",
        "| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **00:00 – 00:06** | 6 min | **Module 0: Welcome & Start Engines** | Slides 1–5 | Demo GIF + Scan QR + kick off setup scripts |",
        "| **00:06 – 00:26** | 20 min | **Module 1: Concepts (Agent / ADK / MCP / Tools)** | Slides 6–20 | 🎤 Poll + 🎯 Quiz + guardrails |",
        "| **00:26 – 00:36** | 10 min | **Module 2: Lab A — Setup** | Slides 21–25 | ✋ Checkpoint #1: `mcp_bakery` dataset (3m timer) |",
        "| **00:36 – 00:52** | 16 min | **Module 3: Lab B — Run the Agent** | Slides 26–32 | ✋ CP #2 macro SQL (5m) + ✋ CP #3 Maps (5m) + bonus |",
        "| **00:52 – 01:03** | 11 min | **Module 4: Troubleshoot, Cleanup, Playbook** | Slides 32–36 | Troubleshooting buffer + cleanup + recap |",
        "| **01:03 – 01:15** | 12 min | **Closing & Q&A** | Slides 37–38 | Open Q&A + live troubleshooting + cheat sheet |",
        "",
        "---",
        "",
        "## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts",
        "",
    ]

    for s in SLIDES_DATA:
        stitle = get_slide_title(s)
        lines.append(f"### Slide {s['num']}: {stitle}")
        lines.append(f"- **Module**: {s['module']}")
        lines.append(f"- **Pacing**: `{s['time']}`")
        lines.append("")
        lines.append("#### 🎙️ Speaker Notes:")
        lines.append("```text")
        lines.append(s["notes"])
        lines.append("```")
        code_val = s.get("code") or (s.get("left_card", {}).get("code", "") + ("\n\n" + s.get("right_card", {}).get("code", "") if s.get("right_card", {}).get("code") else ""))
        if code_val:
            lines.append("")
            lines.append(f"#### 💻 On-Slide Command / Prompt (`{s.get('code_title', 'Snippet')}`):")
            lines.append("```bash")
            lines.append(code_val)
            lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved Markdown Runbook: {output_path}")


if __name__ == "__main__":
    pptx_out = os.path.join(BASE_DIR, "Location_Intelligence_ADK_MCP_Workshop.pptx")
    html_out = os.path.join(BASE_DIR, "index.html")
    notes_html_out = os.path.join(BASE_DIR, "speaker-notes.html")
    md_out = os.path.join(BASE_DIR, "SPEAKER_NOTES_AND_SCRIPT.md")

    build_pptx(pptx_out)
    build_html_deck(html_out)
    build_speaker_notes_html(notes_html_out)
    build_markdown_runbook(md_out)
