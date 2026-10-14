# 🎤 Speaker Notes, Facilitator Runbook & Verbatim Talk Script

## **Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps**
- **Format**: GDE Talk + Interactive Hands-On Workshop (1 hr 15 mins / 75 minutes)
- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)
- **Base Codelab**: [https://codelabs.developers.google.com/adk-mcp-bigquery-maps](https://codelabs.developers.google.com/adk-mcp-bigquery-maps)

---

## ⚡ How to Present Directly from This Folder

1. **Option A — Interactive Web Deck + Dual-Screen Presenter Console (Recommended)**:
   - Run `./present.sh` in this folder (or open `index.html` in Chrome).
   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!
   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.
   - The bottom control bar is hidden from the audience by default and in fullscreen. Press **`B`** to toggle it (all functions also work via hotkeys: `S`/`P`/`G`/`F`/arrows).
   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.
2. **Option B — Google Slides / PowerPoint Presenter View**:
   - Upload `Location_Intelligence_ADK_MCP_Workshop.pptx` to Google Slides (File → Import slides / Open) or open in PowerPoint/Keynote.
   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.
3. **Option C — Tablet / Phone Companion**:
   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through every slide's verbatim notes and copy-paste prompts.

---

## ⏱️ 75-Minute Pacing Schedule & Checkpoints

| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 – 00:06** | 6 min | **Module 0: Welcome & Start Engines** | Slides 1–5 | Demo GIF + Scan QR + kick off setup scripts |
| **00:06 – 00:26** | 20 min | **Module 1: Concepts (Agent / ADK / MCP / Tools)** | Slides 6–20 | 🎤 Poll + 🎯 Quiz + guardrails |
| **00:26 – 00:36** | 10 min | **Module 2: Lab A — Setup** | Slides 21–25 | ✋ Checkpoint #1: `mcp_bakery` dataset (3m timer) |
| **00:36 – 00:52** | 16 min | **Module 3: Lab B — Run the Agent** | Slides 26–31 | ✋ CP #2 macro SQL (5m) + ✋ CP #3 Maps (5m) + bonus |
| **00:52 – 01:03** | 11 min | **Module 4: Troubleshoot, Cleanup, Playbook** | Slides 32–36 | Troubleshooting buffer + cleanup + recap |
| **01:03 – 01:15** | 12 min | **Closing & Q&A** | Slides 37–38 | Open Q&A + live troubleshooting + cheat sheet |

---

## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts

### Slide 1: Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps
- **Module**: Module 0 • Welcome
- **Pacing**: `00:00 – 00:02 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:00 - 00:02 (2 mins)
GOAL: High-energy welcome; name the payoff.

SAY THIS:
"Welcome, everyone! Today we're going to build a Location Intelligence agent — an AI that answers a real business question: where should I open my bakery, and how much should I charge? It will do that by reasoning over enterprise data in BigQuery AND the real world in Google Maps, at the same time."

"The best part? You won't write any BigQuery or Maps API boilerplate. Two Google-managed MCP servers hand the agent its tools over a single open protocol. You'll build the whole thing yourself in this room."
```

---

### Slide 2: This is what you'll have running in about 40 minutes
- **Module**: Module 0 • Welcome
- **Pacing**: `00:02 – 00:03 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:02 - 00:03 (1 min)
GOAL: Hook — show the finished product before any explanation.

SAY THIS:
"Before any slides: here is the exact agent you'll build. Watch the bottom — the user asks 'which zip code has the highest morning foot traffic', the agent writes SQL and runs it in BigQuery. Then 'is that area saturated with bakeries' — it switches to Google Maps and searches Places. One conversation, two totally different data worlds, joined by one agent."

"Keep this picture in your head. Every concept I explain for the next 20 minutes maps to something you just saw."
```

---

### Slide 3: Workshop Hub — scan these now
- **Module**: Module 0 • Welcome
- **Pacing**: `00:03 – 00:04 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:03 - 00:04 (1 min)
ENGAGEMENT CUE: 'Phones out — scan the left QR for the codelab. That page has every command and every prompt, so you never have to type from the projector.'

SAY THIS:
"Three links matter today. Left: the codelab — keep it open all session, it's your source of truth. Middle: your free Google Cloud credit — g.dev/credits/latw-bigquery-100 — redeem it now and create a project with billing on, because both services we use are pay-as-you-go. Right: my GitHub, where this deck and the full speaker script live if you want to rerun this workshop for your own GDG chapter."
```

---

### Slide 4: Rabimba Karanjai
- **Module**: Module 0 • Welcome
- **Pacing**: `00:04 – 00:05 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:04 - 00:05 (1 min)
SAY THIS:
"Quick intro — I'm Rabimba Karanjai, a Google Developer Expert in AI/ML, and by day an ML Scientist at PayPal where I build and break agentic systems. This is a hands-on room: if something fails — and with live APIs something always hiccups — shout it out. Debugging together is part of the workshop."
```

---

### Slide 5: Start your engines — setup runs while I talk
- **Module**: Module 0 • Welcome
- **Pacing**: `00:05 – 00:06 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:05 - 00:06 (1 min)
GOAL: Fire-and-forget provisioning so nobody waits on BigQuery loads later.

SAY THIS:
"Here's my favorite workshop trick: the slowest part of today is provisioning APIs and loading BigQuery tables — and it needs zero attention. So start it NOW, in the background. Activate Cloud Shell from the Cloud Console top bar, paste these commands, and let them run in a corner."

"While Google does the boring work, I'll spend 20 minutes explaining what an agent, ADK, and MCP actually are. When we come back to the terminal, everything will be green. Use the Copy button — don't type these by hand."

FACILITATOR: Watch the room. If more than ~30% look lost at 'Activate Cloud Shell', pause 60 extra seconds here — it's the single biggest dropout point.
```

#### 💻 On-Slide Command / Prompt (`Cloud Shell`):
```bash
# Verify auth + project
gcloud auth list
export PROJECT_ID=$(gcloud config get project)

# Get the code
git clone https://github.com/google/mcp.git
cd mcp/examples/launchmybakery

# Kick off BOTH setup scripts
./setup/setup_env.sh
./setup/setup_bigquery.sh
```

---

### Slide 6: Your friend is opening a sourdough bakery in Los Angeles. Where?
- **Module**: Module 1 • Concepts
- **Pacing**: `00:06 – 00:08 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:06 - 00:08 (2 mins)
GOAL: Frame the business problem; let the audience discover why a bare LLM fails.

SAY THIS:
"A friend wants to open a high-end sourdough bakery in LA. Wrong zip code = bankruptcy. So — how do you pick? Show of hands for A... B... C? Someone always says 'just ask ChatGPT.' Here's the trap: a language model has no idea what foot traffic looks like in 90403 this morning, or that three new bakeries opened there last month. It will confidently invent an answer. That's not intelligence, that's a hallucination with a business plan."

"Click D on screen. Real foot-traffic data lives in a database. Real competitors live on a map. Today's agent queries BOTH, then reasons over the combined evidence."
```

---

### Slide 7: Two data worlds, one question
- **Module**: Module 1 • Concepts
- **Pacing**: `00:08 – 00:09 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:08 - 00:09 (1 min)
SAY THIS:
"Look at the two columns. On the left, the private numbers every business guards: census demographics, what competitors charge for a loaf, your own sales history. That lives in BigQuery. On the right, public real-world facts that change daily: is there already a bakery on that block, how long is the drive to Restaurant Depot, will it rain on opening day. That lives in Google Maps."

"No single system answers both. The whole point of today is the bridge at the bottom — one agent that treats both as just... tools."
```

---

### Slide 8: What makes an LLM an Agent?
- **Module**: Module 1 • Concepts
- **Pacing**: `00:09 – 00:11 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:09 - 00:11 (2 mins)
GOAL: Demystify 'agent' in four reveals. In the web deck each press of → reveals the next block.

SAY THIS (per reveal):
"First: a model. Gemini 3.5 Flash — a brain that predicts text. Powerful, but it can only talk. [→] Give it instructions — a job description: 'you are a location-intelligence analyst; combine BigQuery and Maps.' [→] Give it tools — actual capabilities: run SQL, search places, compute a route. [→] And wrap it in a loop: the model reasons about what to do, calls a tool, observes the result, and reasons again."

"That loop is the whole magic trick. An agent isn't a bigger model — it's a model with hands and a while-loop."
```

---

### Slide 9: The three pillars we'll use today
- **Module**: Module 1 • Concepts
- **Pacing**: `00:11 – 00:12 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:11 - 00:12 (1 min)
SAY THIS:
"Three pillars. Gemini 3.5 Flash is the brain — we run it on Vertex AI so it's authenticated and billed through your Cloud project, which that setup script already switched on. ADK is the framework — you describe the agent in a few lines of Python and it handles the loop, tool dispatch, and a debug UI. And MCP is the connective tissue — the open protocol that lets ADK talk to BigQuery and Maps without us writing a single API wrapper. Next three slides take each in turn."
```

---

### Slide 10: An ADK agent in ~15 lines
- **Module**: Module 1 • Concepts
- **Pacing**: `00:12 – 00:13 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:12 - 00:13 (1 min)
SAY THIS:
"This is genuinely the whole agent — about fifteen lines. An LlmAgent needs three things: a model, an instruction, and tools. Read the instruction like a job description: it tells the agent which dataset it's allowed to touch — mcp_bakery and nothing else — which project to bill queries to, and to always include a Maps link when it talks about places."

"The instruction is your strongest control surface. In the bonus section you'll edit it live and watch the agent's behavior change."
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
root_agent = LlmAgent(
    model='gemini-3.5-flash',
    name='root_agent',
    instruction=f"""
      Help the user answer questions by strategically
      combining insights from two sources:
      1. **BigQuery toolset:** Access demographic (inc.
         foot traffic index), product pricing, and
         historical sales data in the mcp_bakery
         dataset. Do not use any other dataset.
         Run all query jobs from project id: {PROJECT_ID}.
      2. **Maps Toolset:** Use this for real-world
         location analysis, finding competition/places
         and calculating necessary travel routes.
         Include a hyperlink to an interactive map in
         your response where appropriate.
    """,
    tools=[maps_toolset, bigquery_toolset]
)
```

---

### Slide 11: MCP: from N×M integrations to N+M
- **Module**: Module 1 • Concepts
- **Pacing**: `00:13 – 00:15 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:13 - 00:15 (2 mins)
GOAL: The 'why' of MCP — the integration math.

SAY THIS:
"Before MCP, wiring an agent to a data source meant a bespoke adapter: read the API docs, hand-write a client, hand-write the tool schema, pray about auth. Three agents times three data sources is nine brittle adapters."

"MCP flips that. It's an open protocol — Anthropic created it, and it's now industry-wide, with Google as a founding member of the Agentic AI Foundation. A server exposes its capabilities as standard 'tools'; any MCP client discovers and calls them. Write the server once, write the client once, and N-plus-M replaces N-times-M. People call it 'USB-C for AI' and the analogy is exact: one connector, any device."

KEY VOCAB on this slide: Host = the app the user talks to (ADK web UI). Client = the connection inside the host. Server = the thing exposing tools (BigQuery, Maps).
```

---

### Slide 12: MCP anatomy: Host, Client, Server
- **Module**: Module 1 • Concepts
- **Pacing**: `00:15 – 00:16 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:15 - 00:16 (1 min)
SAY THIS:
"Three roles. The Host is the app you talk to — ADK's web UI. Inside it, a Client maintains one dedicated connection per server. The Server is where the tools live. And the transport is how bytes move: stdio for a server running as a subprocess on your laptop, or Streamable HTTP for a remote server."

"Today both our servers are remote and Google-hosted, so it's Streamable HTTP with an auth header. That's why you don't install BigQuery or Maps SDKs at all — you saw the repo: no BigQuery client code, no Places client code. Just two URLs."
```

---

### Slide 13: Google's managed, remote MCP servers
- **Module**: Module 1 • Concepts
- **Pacing**: `00:16 – 00:18 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:16 - 00:18 (2 mins)
GOAL: Position Google's managed servers as the enterprise-ready path.

SAY THIS:
"Last December, Google announced that its API infrastructure itself now speaks MCP. Instead of installing some community server and babysitting it, you point at a managed endpoint: bigquery.googleapis.com/mcp, mapstools.googleapis.com/mcp. Same URL everywhere on Earth."

"Two things to notice. First, MCP is opt-in per project — that's why setup_env.sh ran 'gcloud beta services mcp enable' for both services. Second, it's governed like the rest of Google Cloud: there's a dedicated IAM role — roles/mcp.toolUser — every tool call lands in audit logs, and Model Armor can screen for prompt injection. That governance story is exactly why enterprises can actually deploy this."
```

---

### Slide 14: BigQuery MCP server — the 6 tools
- **Module**: Module 1 • Concepts
- **Pacing**: `00:18 – 00:19 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:18 - 00:19 (1 min)
SAY THIS:
"What can the agent actually do in BigQuery? Six tools. It can list datasets, list tables, and read metadata — and then the two interesting ones: execute_sql runs arbitrary SQL, and execute_sql_readonly does the same with mutations blocked. Because it's full SQL, the agent can even call BigQuery's AI.FORECAST function — that's how it does the revenue projection you'll see later."

"Here's the subtle part — watch get_table_info. When the agent needs to write SQL, it first asks the server for the table schema, and the server returns the column descriptions that the setup script wrote: 'foot_traffic_index — index of estimated foot traffic based on commercial density.' The agent uses that text to decide which column to query. So your schema documentation literally becomes part of the prompt. Good descriptions, smarter agent."
```

---

### Slide 15: Maps Grounding Lite — the 5 tools
- **Module**: Module 1 • Concepts
- **Pacing**: `00:19 – 00:20 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:19 - 00:20 (1 min)
SAY THIS:
"The Maps side is called Grounding Lite — an MCP server over Google's geospatial data. Five tools. search_places finds businesses and returns an AI summary plus a Maps link for each. compute_routes gives distance and drive time — note, deliberately not turn-by-turn navigation. lookup_weather does what it says. And the two resolve tools turn fuzzy text — 'a bakery near the pier' — into stable Place IDs you can feed to other Maps APIs."

"One rule matters: attribution. When the agent's answer is grounded in Maps, the Google Maps source link must be shown. Remember our agent instruction said 'include a hyperlink to an interactive map'? That line is doing attribution compliance."
```

---

### Slide 16: Two servers, two auth patterns — tools.py
- **Module**: Module 1 • Concepts
- **Pacing**: `00:20 – 00:21 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:20 - 00:21 (1 min)
SAY THIS:
"Open tools.py and it's almost disappointingly simple — two functions, same pattern. Maps takes an API key in a header; the setup script created a restricted key that only works for the maps tools service. BigQuery is stricter: it's your enterprise data, so it wants OAuth. We pull a token from your Application Default Credentials and pass it as a Bearer header, plus x-goog-user-project so queries bill to your project."

"Now the one operational gotcha of the whole day — star this. That OAuth token lives about 60 minutes, and ADK does not refresh it for you. If your agent suddenly starts failing late in the workshop, re-run gcloud auth application-default login. Write it down."
```

#### 💻 On-Slide Command / Prompt (`adk_agent/mcp_bakery_app/tools.py (excerpt)`):
```bash
# --- Maps: API key header ---
MCPToolset(
  connection_params=StreamableHTTPConnectionParams(
    url="https://mapstools.googleapis.com/mcp",
    headers={"X-Goog-Api-Key": maps_api_key},
    timeout=30.0, sse_read_timeout=300.0))

# --- BigQuery: OAuth bearer from ADC ---
credentials, project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/bigquery"])
credentials.refresh(
    google.auth.transport.requests.Request())
HEADERS_WITH_OAUTH = {
    "Authorization": f"Bearer {credentials.token}",
    "x-goog-user-project": project_id}
MCPToolset(
  connection_params=StreamableHTTPConnectionParams(
    url="https://bigquery.googleapis.com/mcp",
    headers=HEADERS_WITH_OAUTH,
    timeout=30.0, sse_read_timeout=300.0))
```

---

### Slide 17: The reasoning journey: macro → micro → money
- **Module**: Module 1 • Concepts
- **Pacing**: `00:21 – 00:23 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:21 - 00:23 (2 mins)
GOAL: The narrative spine of the whole workshop — memorize this funnel.

SAY THIS:
"Here's the entire workshop as five questions. Notice the rhythm — it zooms from the whole city down to a loading dock. Question one is MACRO: across all of LA, where's the morning foot traffic? That's a BigQuery aggregate — the agent writes SQL, scans the foot_traffic table, and lands on zip 90403, Santa Monica. Question two goes MICRO: is that zip already crawling with bakeries? No database knows that — that's a live Maps search. Three: pricing — back to BigQuery, max price for a sourdough loaf, and Erewhon tops out around $18.50. Four: money — forecast December revenue off your best store using BigQuery's AI.FORECAST. Five: logistics — a compute_routes call to confirm the supplier run is under 30 minutes."

"Blue rows are BigQuery, green rows are Maps. The agent is choosing the right tool for each question with no router, no if-statements — the instruction plus the model's reasoning does it."
```

---

### Slide 18: The full architecture
- **Module**: Module 1 • Concepts
- **Pacing**: `00:23 – 00:24 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:23 - 00:24 (1 min)
SAY THIS:
"Everything we just covered, one diagram. User talks to the ADK web UI. The agent — Gemini 3.5 Flash on Vertex AI — reads the question and the instruction, decides it needs data, and the MCPToolset fires a signed HTTP call. BigQuery interprets the schema and runs SQL where the data lives — the rows never get shipped into the model, only the answer does. Maps grounds the same conversation in live places and routes. Then the agent fuses both into one answer."

"Screenshot this slide. In the lab, whenever you're lost, find yourself on this map."

NOTE: This codelab diagram says 'Gemini 3 Pro' — the actual code uses gemini-3.5-flash. If a sharp attendee asks, confirm: model ID is set in agent.py and swappable.
```

---

### Slide 19: Concept Check & Why not just…?
- **Module**: Module 1 • Concepts
- **Pacing**: `00:24 – 00:25 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:24 - 00:25 (1 min)
GOAL: Lock in tool selection intuition before hands-on.

SAY THIS:
"Sixty-second check. Weather at the site? Maps lookup_weather. December revenue forecast? BigQuery execute_sql calling AI.FORECAST. How does the agent know what columns exist? It calls list_table_ids and get_table_info first."

"And the right column kills the three things people always try instead: pasting CSVs into the prompt — stale and ungoverned; curling the Maps API — you're back to hand-rolled auth and parsing; fine-tuning — which teaches a model style, not today's facts. When in doubt: warehouse facts, BigQuery; real-world right-now, Maps."
```

---

### Slide 20: Taking this to production — the guardrails that matter
- **Module**: Module 1 • Concepts
- **Pacing**: `00:25 – 00:26 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:25 - 00:26 (1 min)
GOAL: Bridge from toy to enterprise; this is what makes it 'GDE-grade'.

SAY THIS:
"Quick reality check — today we use YOUR credentials because it's fast. In production you tighten it: grant only the three least-privilege roles; give the agent its own service account so every call is attributable; prefer execute_sql_readonly — or a deny policy on execute_sql — so the agent physically cannot DROP a table; keep the Maps key restricted to one service; put Model Armor in front of tool output so a poisoned web result can't hijack the agent; and alert on the audit logs. That's the list a security team will ask about — now you have answers."

With that — enough theory. Let's build it.
```

---

### Slide 21: Let's build this!
- **Module**: Module 2 • Lab A: Setup
- **Pacing**: `00:26 – 00:27 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:26 - 00:27 (1 min)
GOAL: Shift the room from listening to doing.

SAY THIS:
"Concepts done. From here it's all hands-on — three parts. Part A, we finish setup and verify the data landed. Part B, we boot the agent and say hello. Part C, the fun part: the full five-question business journey. If you started the scripts at the beginning, you're already ahead. Let's check on them."

FACILITATOR: From this point, keep the codelab page open on the projector when not on a slide — attendees should mirror you.
```

---

### Slide 22: Step 1: Project, auth & the code
- **Module**: Module 2 • Lab A: Setup
- **Pacing**: `00:27 – 00:29 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:27 - 00:29 (2 mins)
GOAL: Everyone authenticated with ADC set.

SAY THIS:
"Step one. Three checks. gcloud auth list — your account should say ACTIVE. Then export PROJECT_ID so every later command knows your project. And the important one: gcloud auth application-default login. That creates Application Default Credentials on this machine — remember, the BigQuery toolset turns that into the OAuth bearer token. Skip this and the agent fails at query time, not at startup, which confuses everyone."

WALK THE ROOM: the #1 failure here is people not having billing enabled because they skipped the credit redemption. Ask for a show of hands: 'Who sees their account as ACTIVE?'
```

#### 💻 On-Slide Command / Prompt (`Cloud Shell`):
```bash
gcloud auth list
gcloud config get project
export PROJECT_ID=$(gcloud config get project)

git clone https://github.com/google/mcp.git
cd mcp/examples/launchmybakery

# Required so ADK can call BigQuery via MCP
gcloud auth application-default login
```

---

### Slide 23: What those two setup scripts just did
- **Module**: Module 2 • Lab A: Setup
- **Pacing**: `00:29 – 00:31 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:29 - 00:31 (2 mins)
GOAL: Convert 'magic scripts' into understood infrastructure.

SAY THIS:
"So what did you actually run? setup_env.sh did two things — it enabled the four APIs, AND it flipped on the MCP endpoints themselves with gcloud beta services mcp enable; remember, MCP is opt-in. Then it minted a Maps API key locked to just the maps-tools service and dropped your .env. setup_bigquery.sh staged the four CSVs into a bucket, then created the mcp_bakery dataset with four tables. And here's that detail again: every column got an OPTIONS description. Those descriptions are what get_table_info will feed the agent so it can write sensible SQL."

CHECK: 'Everyone whose scripts finished — green check in chat / hand up. Still running? Fine, keep going, it'll catch up.'
```

---

### Slide 24: ✋ Checkpoint 1: Your data is live
- **Module**: Module 2 • Lab A: Setup
- **Pacing**: `00:31 – 00:33 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:31 - 00:33 (2 mins) — START THE 2-MIN LAB TIMER.
GOAL: First tangible win; everyone sees their own data.

SAY THIS:
"First checkpoint — make it real. Open the BigQuery console. You should see a dataset called mcp_bakery with four tables: demographics, bakery_prices, sales_history_weekly, foot_traffic. Click into foot_traffic and find the morning score column — that's the exact column the agent is about to query for question one."

"If mcp_bakery isn't there, nine times out of ten the PROJECT_ID export didn't stick — echo it, re-run the script. Hands up when you see the four tables!"
```

---

### Slide 25: Step 2: Install ADK in a virtualenv
- **Module**: Module 2 • Lab A: Setup
- **Pacing**: `00:33 – 00:36 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:33 - 00:36 (3 mins)
SAY THIS:
"Install time. Make a virtualenv — Cloud Shell's system Python is shared, don't pollute it. Then pip install quote google-adk bracket mcp unquote. That little [mcp] extra is what brings the MCP client; without it MCPToolset import fails. If the resolver gives you grief, the repo pins google-adk==1.28.0 as a known-good."

"Then cd into adk_agent. Important: adk web discovers agent apps by scanning the CURRENT directory, so where you run it from matters. If the UI later shows an empty dropdown, you're in the wrong folder."
```

#### 💻 On-Slide Command / Prompt (`Cloud Shell`):
```bash
python3 -m venv .venv
source .venv/bin/activate

# The [mcp] extra = MCP client support
pip install "google-adk[mcp]"

# adk web scans the current dir for agents
cd adk_agent/
```

---

### Slide 26: Step 3: Read the agent you'll run
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:36 – 00:38 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:36 - 00:38 (2 mins)
GOAL: Connect the concept slides to real files before running.

SAY THIS:
"Before we run anything, open it. Click 'Open Editor' in Cloud Shell and navigate into launchmybakery. Open agent.py — there's the LlmAgent from slide 10, word for word. Open tools.py — there's the API-key header and the OAuth header from slide 16. And check .env: you should see GOOGLE_GENAI_USE_VERTEXAI=1 and a MAPS_API_KEY, both written by the setup script. You're not writing code today — you're recognizing it, so that next week you can write your own."
```

---

### Slide 27: Step 4: Launch the agent UI
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:38 – 00:41 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:38 - 00:41 (3 mins)
GOAL: Everyone has the ADK web UI open.

SAY THIS:
"Launch it. From inside adk_agent, run adk web with allow_origins set to the cloudshell.dev regex — that flag exists because you're reaching the server through Cloud Shell's web proxy, and without it the WebSocket gets rejected. When you see 'Uvicorn running on 127.0.0.1:8000', click Web Preview in the top right, change the port to 8000, and preview."

"A chat UI opens. Top-left dropdown: pick mcp_bakery_app. If that dropdown is empty, stop — you're in the wrong directory. Ctrl-C, cd adk_agent, rerun. This trips up half the room every time."
```

#### 💻 On-Slide Command / Prompt (`Cloud Shell (inside adk_agent/)`):
```bash
adk web --allow_origins \
  'regex:https://.*\.cloudshell\.dev'

# Then in Cloud Shell:
#  Web Preview (top right)
#    → Change port → 8000
#    → Change and Preview
```

---

### Slide 28: ✋ Checkpoint 2: First tool call (macro)
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:41 – 00:44 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:41 - 00:44 (3 mins) — START THE 3-MIN TIMER.
GOAL: The 'wow' moment — the agent writes and runs its own SQL.

SAY THIS:
"First real question — copy it from the codelab, don't type it: 'I want to open a bakery in Los Angeles. Find the zip code with the highest morning foot traffic score.' Hit enter and DON'T just read the answer — open the Events / trace panel. You'll see the agent think: it calls get_table_info to learn the schema, then execute_sql with a query it wrote itself ordering by morning foot traffic. And 90403 — Santa Monica — floats to the top."

"You just watched a model turn English into SQL, run it against governed data, and reason over the result. If you got an auth error instead — say it with me — 60-minute token; re-run gcloud auth application-default login."
```

---

### Slide 29: ✋ Checkpoint 3: Validate on the ground (micro)
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:44 – 00:47 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:44 - 00:47 (3 mins)
GOAL: The pivot moment — same conversation, different server, conversational memory.

SAY THIS:
"Now the move that makes this more than a text-to-SQL demo. Follow up with: 'Can you search for Bakeries in that zip code to see if it's saturated?' Two things to notice. First, you never repeated the zip — the agent remembered 90403 from the conversation. Second, look at the trace: it did NOT touch BigQuery. It switched servers and called search_places on Maps."

"Same thread, two data worlds. And when the answer comes back with a Maps link — click it. That link isn't decoration, it's the attribution requirement we talked about, and the agent included it because the instruction told it to."
```

---

### Slide 30: Your turn: run the rest of the journey
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:47 – 00:50 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:47 - 00:50 (3 mins)
GOAL: Self-directed exploration; make it a game.

SAY THIS:
"Three more, and I want you to play a game: before you run each one, call the tool out loud. Pricing — 'max price for a Sourdough Loaf in LA Metro' — which server? BigQuery; Erewhon's at about eighteen-fifty, so our premium price lands around fifteen-to-eighteen. Forecasting — 'take my best store, forecast December, multiply by eighteen' — that's execute_sql running AI.FORECAST. Logistics — 'closest Restaurant Depot under thirty minutes' — Maps compute_routes."

"Run them in the SAME chat thread. The agent will carry context across all five. By the end you'll have a zip code, a saturation read, a price point, a revenue forecast, and a supply-chain check — a whole mini business case, in one conversation. GO."
```

---

### Slide 31: ⚡ Finished early? Break it (productively)
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:50 – 00:52 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:50 - 00:52 (2 mins)
GOAL: Keep fast finishers engaged while others catch up.

SAY THIS:
"If you're done, don't sit idle — break it, productively. Two challenges. One: edit the instruction in agent.py — say 'position the brand as budget-friendly' — save, let adk web hot-reload, and re-ask the pricing question. One sentence changes the whole recommendation; that's prompt-as-control-surface. Two: ask about the weather on opening day. You never wrote a weather tool — lookup_weather was just there in the Maps server. That's the power of a tool catalog."

FACILITATOR: This slide is your pressure-release valve. Keep it up while stragglers finish Checkpoint 3.
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
# agent.py — edit the instruction, e.g.:
"Position the brand as budget-friendly
 and always cite the source table."
# save → adk web reloads → re-ask Q3

# Ask about the weather on opening day
"Weather in 90403 this Saturday?"
   → Maps lookup_weather

# Safety: force read-only SQL
# MCPToolset(tool_filter=['execute_sql_readonly'])
# or an IAM deny on execute_sql
```

---

### Slide 32: Quick fixes — the 6 ways today breaks
- **Module**: Module 3 • Lab B: Run It
- **Pacing**: `00:52 – 00:55 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:52 - 00:55 (3 mins) — buffer / catch-up window.
GOAL: Clear every blocker so the room ends on a win.

SAY THIS:
"This is the slide to photograph. Every failure today is one of these six. Auth error after working fine? 60-minute token — re-login. 403 that says not enabled? The MCP endpoint flag from setup_env. Empty dropdown? Wrong directory. Web preview won't load? You dropped the allow_origins flag. Maps failing but BigQuery fine? Check the key in .env. Anything about billing? You need the credit redeemed."

FACILITATOR: Use this whole block as flexible time. If the room is ahead, invite people to try their own city. If behind, this is your catch-up.
```

---

### Slide 33: Clean up — don't donate your credits back
- **Module**: Module 4 • Wrap-Up
- **Pacing**: `00:55 – 00:57 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:55 - 00:57 (2 mins)
GOAL: Good cloud hygiene; protect the credits we just handed out.

SAY THIS:
"Last responsible step: clean up. Ctrl+C to stop the server, then run cleanup_env.sh from the repo root. It deletes the mcp_bakery dataset, the staging bucket, and that API key. Your project stays, so if you want to run this again — or demo it to your team on Monday — the setup scripts recreate everything in about four minutes. Don't be the person who burns their credits on a forgotten BigQuery table."
```

#### 💻 On-Slide Command / Prompt (`Cloud Shell (repo root)`):
```bash
# Ctrl+C to stop adk web, then:
cd ~/mcp/examples/launchmybakery

chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh

# Deletes: mcp_bakery dataset,
#  the staging bucket, and the API key.
```

---

### Slide 34: Your Location-Intelligence Agent playbook
- **Module**: Module 4 • Wrap-Up
- **Pacing**: `00:57 – 01:00 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:57 - 01:00 (3 mins)
GOAL: Crystallize the four takeaways so they survive the parking lot.

SAY THIS:
"If you remember four things. One: ground, don't guess — a bare model invents foot-traffic numbers; a grounded one queries them. Two: one agent, many tools — you never wrote a BigQuery or Maps client; two MCP toolsets gave one agent both worlds. Three: your schema is the prompt — the agent read our column descriptions to write its own SQL, so documenting your data is now an AI feature, not busywork. Four: govern by default — managed servers mean IAM, audit logs, read-only SQL and Model Armor come along for free."

"Ground, tools, schema, governance. Say it back to me on the way out."
```

---

### Slide 35: Where to take this next
- **Module**: Module 4 • Wrap-Up
- **Pacing**: `01:00 – 01:02 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:00 - 01:02 (2 mins)
SAY THIS:
"Three on-ramps. First, deploy it — adk web is a debug UI, so for real users containerize and push to Cloud Run or Agent Engine with a service account. Second, more servers — the google/mcp repo lists every managed server: GCE, GKE, Spanner, Developer Knowledge; the wiring you learned today is identical. Third, the real homework — point this at your own data. Write honest column descriptions, scope the instruction to your dataset, and start on execute_sql_readonly until you trust it."
```

---

### Slide 36: Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps
- **Module**: Module 4 • Closing
- **Pacing**: `01:02 – 01:03 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:02 - 01:03 (1 min)
SAY THIS:
"Look back at the GIF from the first minute. That agent — the one that queries BigQuery, searches Maps, forecasts revenue, checks drive time — you just built it, yourself, with your own project. Not a demo I showed you. Yours."
```

---

### Slide 37: Thank you!
- **Module**: Module 4 • Closing & Q&A
- **Pacing**: `01:03 – 01:15 (12 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:03 - 01:15 (remaining time — Q&A).
SAY THIS:
"Thank you! Everything is open: the codelab is free and stays up — take it, fork it, run this same workshop at your own GDG. Top QR is the codelab, bottom is my repo with this deck and the full speaker script. And if you want to compare notes on agents in production — the middle QR is my LinkedIn; I answer."

"The rest of our time is yours — questions, and if anyone's still fighting a red error, bring it up now and we'll fix it live."

FACILITATOR: Keep the troubleshooting slide (G key) one keystroke away during Q&A. Budget remaining clock — the runbook pacing table gives you slack back if concepts ran long.
```

---

### Slide 38: Cheat sheet — every command from today
- **Module**: Appendix • Reference
- **Pacing**: `Reference Slide`

#### 🎙️ Speaker Notes:
```text
REFERENCE SLIDE — not presented live.
Every command from the workshop in one place. Point attendees here if they re-run the lab later; it is also the fastest 'second screen' reference while facilitating.
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
export PROJECT_ID=$(gcloud config get project)
git clone https://github.com/google/mcp.git
cd mcp/examples/launchmybakery
gcloud auth application-default login
./setup/setup_env.sh
./setup/setup_bigquery.sh

python3 -m venv .venv && source .venv/bin/activate
pip install "google-adk[mcp]"
cd adk_agent/
adk web --allow_origins \
  'regex:https://.*\.cloudshell\.dev'

# later, from the repo root:
cd ~/mcp/examples/launchmybakery
chmod +x cleanup/cleanup_env.sh
./cleanup/cleanup_env.sh
```

---
