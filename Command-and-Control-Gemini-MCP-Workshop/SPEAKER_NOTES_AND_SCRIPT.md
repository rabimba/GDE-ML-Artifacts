# 🎤 Speaker Notes, Facilitator Runbook & Verbatim Talk Script

## **Command and control: Orchestrate app development with Gemini and MCP**
- **Format**: Interactive Hands-On Workshop (1 hr 15 mins / 75 minutes)
- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)
- **Base Codelab**: [https://codelabs.developers.google.com/gemini-mcp-agy](https://codelabs.developers.google.com/gemini-mcp-agy)

---

## ⚡ How to Present Directly from This Folder

1. **Option A — Interactive Web Deck + Dual-Screen Presenter Console (Recommended)**:
   - Run `./present.sh` in this folder (or open `index.html` in Chrome).
   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!
   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.
   - Press **`G`** for the 32-slide grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.
2. **Option B — Google Slides / PowerPoint Presenter View**:
   - Upload `Command_and_Control_Gemini_MCP_Workshop.pptx` to Google Slides (File → Import slides / Open) or open in PowerPoint/Keynote.
   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.
3. **Option C — Tablet / Phone Companion**:
   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through all 32 slides' verbatim notes and copy-paste prompts.

---

## ⏱️ 75-Minute Pacing Schedule & Checkpoints

| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 – 00:10** | 10 min | **Module 0: Welcome & Onboarding** | Slides 1–4 | Scan Codelab QR + Start Cloud Shell |
| **00:10 – 00:20** | 10 min | **Module 1: Concepts & Architecture** | Slides 5–10 | 🎤 Poll #1 (Hallucinations) + 🎯 Quiz #2 (MCP vs Skills) |
| **00:20 – 00:30** | 10 min | **Module 2: Lab Step 1 — Hello AGY CLI** | Slides 11–14 | ✋ Checkpoint #1: `cat-trivia.js` ASCII Cat (3m timer) |
| **00:30 – 00:45** | 15 min | **Module 3: Lab Step 2 — Developer Knowledge MCP** | Slides 15–18 | 🎤 Quiz #3 (Nano Banana 2) + ✋ Checkpoint #2: Kitten PNG (5m timer) |
| **00:45 – 01:02** | 17 min | **Module 4: Lab Step 3 — Skills & `/planning` Mode** | Slides 19–25 | 🎯 Quiz #4 (`/fast` vs `/planning`) + ✋ Checkpoint #3: `/artifact` Review |
| **01:02 – 01:10** | 8 min | **Module 5: Lab Step 4 — Cloud Run & Guardrails** | Slides 26–27 | ✋ Checkpoint #4: Live Cloud Run + 🎤 Break the Dog Guardrail! |
| **01:10 – 01:15** | 5 min | **Module 6: Playbook, Cheat Sheet & Q&A** | Slides 28–32 | 4-Step Playbook Recap + Open Q&A |

---

## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts

### Slide 1: Command and control: Orchestrate app development with Gemini and MCP
- **Module**: Module 0 • Welcome & Onboarding
- **Pacing**: `00:00 – 00:02 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:00 - 00:02 (2 mins)
GOAL: High-energy welcome and set the core premise of the workshop.

SAY THIS:
"Welcome everyone! Over the next 75 minutes, we are going to do something that would have sounded impossible just two years ago: we are going to architect, build, test, and deploy a complete, full-stack multimodal cloud application to Google Cloud Run—with a reactive web frontend and a dual-model AI agent backend—without writing a single line of code by hand."

"Instead of acting as typists, today you are taking 'Command and Control'. You'll learn how to orchestrate Google Antigravity (AGY) using Gemini 3.5 Flash, ground it in live official docs with the Google Developer Knowledge MCP server, and equip it with specialized Agent Skills."
```

---

### Slide 2: Workshop Hub & Essential Links
- **Module**: Module 0 • Welcome & Onboarding
- **Pacing**: `00:02 – 00:05 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:02 - 00:05 (3 mins)
ENGAGEMENT CUE: Pause for 30 seconds and make sure everyone scans the left QR code or types codelabs.developers.google.com/gemini-mcp-agy.

SAY THIS:
"First things first—grab your phones or open a browser tab and head to the link on the left card: codelabs.developers.google.com/gemini-mcp-agy. Keep this tab open throughout the session! All the prompts and JSON snippets we'll use are right there so you don't have to type long paragraphs from the projector."

"Second card: your free Google Cloud credit — g.dev/credits/latw-mcp-010. Redeem it NOW, because we deploy to Cloud Run at the end and that needs billing enabled on your project."

"Quick show of hands: who has the Codelab open on their screen right now? Awesome. Go ahead and start initializing your Google Cloud project and Cloud Shell in the background while I introduce myself and our mission."
```

---

### Slide 3: Rabimba Karanjai
- **Module**: Module 0 • Welcome & Onboarding
- **Pacing**: `00:05 – 00:07 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:05 - 00:07 (2 mins)
GOAL: Quick personal introduction and establish credibility & approachability.

SAY THIS:
"A quick bit about me—I'm Rabimba Karanjai. I'm a Google Developer Expert in AI & Machine Learning and an ML Scientist at PayPal. I spend my days building and evaluating agentic systems and developer tooling—and when I'm not orchestrating agents, as you can see from the photo, I love being on the racetrack!"

"Speaking of racing: think of today's workshop like being the race engineer on the pit wall. Gemini is the engine, Antigravity is the chassis and harness, and MCP and Skills are your live telemetry. This is a super interactive workshop—if you hit a snag or have a question at any point, raise your hand or shout it out!"
```

---

### Slide 4: Today's 75-Minute Mission
- **Module**: Module 0 • Welcome & Onboarding
- **Pacing**: `00:07 – 00:10 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:07 - 00:10 (3 mins)
GOAL: Walk through the 4-part roadmap and announce the 'Zero Manual Code' challenge.

SAY THIS:
"Here is our 75-minute game plan. We have one fun rule today: Hands off the code editor! Your challenge is to build the entire Cat Delivery System—backend, frontend, Dockerfile, and Cloud Run deployment—purely by steering Antigravity through prompts, MCP tools, Skills, and artifact reviews."

"We'll start with a quick 10-minute conceptual foundation, then jump straight into four hands-on sprints: Step 1 is getting cozy with AGY CLI; Step 2 is wiring up the Google Developer Knowledge MCP server; Step 3 is installing Agent Skills and using Planning Mode; and Step 4 is shipping to Cloud Run and testing our guardrails live."
```

---

### Slide 5: From Code Autocomplete to Command & Control
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:10 – 00:12 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:10 - 00:12 (2 mins)
INTERACTIVE POLL #1: Get the room laughing and raising hands.

SAY THIS:
"Before we type our first command, let's do a quick sanity check. Raise your hand if you've ever asked an AI coding assistant to write code for a new Google Cloud or Vertex AI feature, and it confidently gave you an import statement from 2023 that throws an ImportError!"

(Click Reveal in Web Deck / Read takeaway)
"Almost every hand in the room! And what do we usually do next? We go to the docs, copy 5,000 words of markdown, and paste it into the chat window. Today we stop doing manual copy-paste RAG. Let's look at how an orchestrated coding agent actually works."
```

---

### Slide 6: Anatomy of an AI Coding Agent
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:12 – 00:14 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:12 - 00:14 (2 mins)
GOAL: Define the three pillars of our workshop: Model, Agent Harness, and Tools/MCP/Skills.

SAY THIS:
"Just like any AI agent is composed of a Model, an Agent loop, and Tools, an AI Coding Agent has three distinct parts:
1. On the right, the Model—today we'll use Gemini 3.5 Flash for fast, token-efficient reasoning, plus Gemini 3.1 Flash Image (also known as Nano Banana 2) for image generation.
2. In the center, the Agent Harness—Google Antigravity. Think of the harness as the engine that manages planning, file editing, terminal execution, artifacts, and human-in-the-loop permissions. We'll use Antigravity both as our CLI coding agent AND via the Antigravity Python SDK inside our app!
3. On the left, Tools & Knowledge—specifically the Model Context Protocol (MCP) and Agent Skills."
```

---

### Slide 7: Objectives & Workshop Outcomes
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:14 – 00:15 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:14 - 00:15 (1 min)
GOAL: Set clear learning outcomes.

SAY THIS:
"Here are the four concrete outcomes you'll walk away with today:
First, mastering Antigravity CLI's two operating modes: Fast mode and Planning mode, plus reviewing and commenting on artifacts.
Second, connecting the Google Developer Knowledge MCP server so your agent queries live official Google docs.
Third, installing reusable Agent Skills and Plugins using progressive disclosure.
And fourth, orchestrating a production deployment to Google Cloud Run with automated acceptance testing."
```

---

### Slide 8: Core Architecture
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:15 – 00:17 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:15 - 00:17 (2 mins)
GOAL: Explain the two-tier diagram clearly so attendees don't confuse Antigravity CLI with the Antigravity SDK inside the app.

SAY THIS:
"Look closely at this architecture diagram because there's a cool meta-pattern happening today. We have two tiers:
In Tier 1 at the top, YOU are in Cloud Shell Editor talking to Antigravity CLI (`agy`). `agy` uses the Developer Knowledge MCP server and two installed skills—the Antigravity Python SDK skill and Chrome's Modern Web Guidance plugin—to write our application.
In Tier 2 at the bottom is the application `agy` builds for us: the Cat Delivery System running on Cloud Run! Inside that single container, FastAPI serves a static Lit & Vite chat frontend and runs a backend agent built with the Antigravity SDK. That root agent uses Gemini 3.5 Flash to chat with the user, enforce our hilarious business rule—ABSOLUTELY NO DOGS, steer dog requests to cats, though capybaras are allowed—and calls Gemini 3.1 Flash Image (Nano Banana 2) to generate custom cat pictures."
```

---

### Slide 9: Key Technologies & Concepts We'll Use!
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:17 – 00:18 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:17 - 00:18 (1 min)
GOAL: Quick visual summary of the 3 tech stacks before the interactive quiz.

SAY THIS:
"So our toolkit comes down to three pillars: Google Antigravity (both the CLI and the Python SDK), Open Context Standards (Model Context Protocol and Agent Skills), and Google Cloud's serverless AI stack (Gemini 3.5 Flash, Nano Banana 2, and Cloud Run)."
```

---

### Slide 10: Model Context Protocol (MCP) & Agent Skills & Plugins
- **Module**: Module 1 • Concepts & Architecture
- **Pacing**: `00:18 – 00:20 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:18 - 00:20 (2 mins)
INTERACTIVE QUIZ #2: Ask the room to vote between MCP Server vs Agent Skill!

SAY THIS:
"People always ask me: 'Rabimba, when do I use an MCP server versus an Agent Skill?' Look at these two cards:
- MCP (on the left) is for live, external queries and actions—like searching Google's massive, constantly updated Developer Documentation database.
- Agent Skills (on the right) use an open standard (agentskills.io) built around a magic concept called Progressive Disclosure. Instead of stuffing ten thousand tokens of instructions into your system prompt, Antigravity only reads the 2-line description of each skill at startup. When—and only when—a task matches that skill, the agent reads the full `SKILL.md` file on demand."

"So pop quiz for the room: if you have a 15-page team architecture guide and you don't want it burning 20,000 tokens on every turn, which one do you use? Shout it out! ... Exactly: an Agent Skill!"
```

---

### Slide 11: Let's build this!
- **Module**: Module 2 • Lab Step 1: Hello Antigravity CLI
- **Pacing**: `00:20 – 00:21 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:20 - 00:21 (1 min)
TRANSITION TO HANDS-ON LAB 1.

SAY THIS:
"Theory time is over—time to get our hands on the keyboard! Everyone switch over to your Google Cloud Console tab and Codelab Step 2 & 3."
```

---

### Slide 12: Step 1: Open Cloud Shell Editor Terminal
- **Module**: Module 2 • Lab Step 1: Hello Antigravity CLI
- **Pacing**: `00:21 – 00:24 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:21 - 00:24 (3 mins)
CRITICAL FACILITATOR TIP: Emphasize clicking 'Open Editor' and using Terminal > New Terminal (Ctrl + `). If someone runs `agy` in the raw non-editor Cloud Shell pane, the TUI menus look garbled.

SAY THIS:
"Pay super close attention to Step 2 here—this will save you a ton of headache! Once Cloud Shell connects, click the 'Open Editor' button on the top bar. Inside the Cloud Shell Editor, go to the top menu and click Terminal -> New Terminal (or press Ctrl + backtick). Why? Because Antigravity has a rich interactive terminal UI with diff viewers and menus that render much cleaner inside the Editor's terminal."

"Once your terminal is open, run `mkdir -p ~/hello-agy && cd ~/hello-agy` and type `agy`!"
```

#### 💻 On-Slide Command / Prompt (`terminal — Cloud Shell Editor (Ctrl + `)`):
```bash
# Create a working directory for our warm-up exercise
mkdir -p ~/hello-agy && cd ~/hello-agy

# Launch Antigravity CLI
agy
```

---

### Slide 13: Step 2: Authenticate Antigravity CLI
- **Module**: Module 2 • Lab Step 1: Hello Antigravity CLI
- **Pacing**: `00:24 – 00:27 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:24 - 00:27 (3 mins)
GOAL: Walk everyone through the 3 authentication prompts inside `agy`.

SAY THIS:
"The first time `agy` launches, it asks how you want to authenticate:
1. Select 'Use a Google Cloud project'.
2. It will print a URL. Open it and sign in with the SAME Google account you used to redeem your credit code—that's the project we want to bill to. If you're already signed into a work org account in this browser, open the link in an incognito tab so you can pick the right account. Copy the authorization code back into `agy`.
3. Next, paste your Google Cloud Project ID, and when it asks for Google Cloud Location, select `global`. Why `global`? Because frontier preview endpoints like Gemini 3.5 and Gemini 3.1 Flash Image route through the global endpoint on Vertex AI."
```

#### 💻 On-Slide Command / Prompt (`agy — First-Time Authentication Flow`):
```bash
? How would you like to authenticate?
> 1. Use a Google Cloud project

Paste authorization code: [PASTE_CODE_HERE]
Enter Google Cloud Project ID: [YOUR_PROJECT_ID]
Select Google Cloud Location: > global
```

---

### Slide 14: ✋ Checkpoint 1: Generate & Run Cat Trivia
- **Module**: Module 2 • Lab Step 1: Hello Antigravity CLI
- **Pacing**: `00:27 – 00:30 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:27 - 00:30 (3 mins)
LAB CHECKPOINT #1 (Start the 3-minute timer on screen!).

SAY THIS:
"Now that you're inside `agy`, paste our first prompt: `Write a simple node script that returns cat trivia and run it for me`.
Watch what happens: `agy` writes `cat-trivia.js`, and before it runs `node cat-trivia.js`, it stops and asks your permission! Notice you can allow it once, allow for this session, or persist to `settings.json`. Choose `1. Yes`."

"Once you see the ASCII cat and trivia fact on your screen, ask `Explain the code you generated please`, and then press `Ctrl+D` twice to exit back to the terminal. Raise your hand once you've got your ASCII cat fact!"
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
Write a simple node script that returns cat trivia and run it for me

Explain the code you generated please

# When finished, exit AGY CLI:
# Press Ctrl+D twice
```

---

### Slide 15: Inside ~/.gemini: AGY Configuration Layout
- **Module**: Module 3 • Lab Step 2: Developer Knowledge MCP
- **Pacing**: `00:30 – 00:33 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:30 - 00:33 (3 mins)
GOAL: Demystify `~/.gemini` so attendees understand where `brain/`, `mcp_config.json`, `skills/`, and `GEMINI.md` live.

SAY THIS:
"Let's move to Codelab Step 4! Everything Antigravity knows about your global setup lives in a clean hidden directory: `~/.gemini`.
- `antigravity-cli/brain/` is where your conversation history and artifacts—like plans and task lists—are stored.
- `config/mcp_config.json` is where we register MCP servers.
- `skills/` and `config/plugins/` hold our reusable skills and plugins.
- And `GEMINI.md` holds global rules you want enforced everywhere."
```

#### 💻 On-Slide Command / Prompt (`~/.gemini — Directory Hierarchy`):
```bash
~/.gemini
├── antigravity/
├── antigravity-cli/
│   ├── brain/            # Conversations and artifacts
│   └── settings.json     # CLI settings
├── config/
│   ├── plugins/          # Global / shared plugins
│   └── mcp_config.json   # Global / shared MCP config
├── skills/               # Global / shared skills
│   └── {skill_name}/
│       └── SKILL.md      # Skill definition
└── GEMINI.md             # Global rules
```

---

### Slide 16: Step 3: Configure Developer Knowledge MCP
- **Module**: Module 3 • Lab Step 2: Developer Knowledge MCP
- **Pacing**: `00:33 – 00:37 (4 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:33 - 00:37 (4 mins)
CRITICAL FACILITATOR TIP: Remind attendees to replace `[[PROJECT_ID]]` (including the double brackets!) with their actual Project ID.

SAY THIS:
"Let's wire up the Developer Knowledge MCP server right now:
First, in your bash terminal, enable the API: `gcloud services enable developerknowledge.googleapis.com`.
Second, create and open the config file: `mkdir -p ~/.gemini/config && cloudshell edit ~/.gemini/config/mcp_config.json`.
Third, paste the JSON from Codelab Step 4—and WATCH OUT for line 13: replace `[[PROJECT_ID]]` (remove the square brackets too!) with your actual Google Cloud Project ID.
Finally, launch `agy` and type `/mcp`. You should see `google-developer-knowledge` listed and connected!"
```

#### 💻 On-Slide Command / Prompt (`~/.gemini/config/mcp_config.json`):
```bash
{
  "mcpServers": {
    "google-developer-knowledge": {
      "url": "https://developerknowledge.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
      },
      "timeout": 30000,
      "headers": {
        "X-goog-user-project": "[[PROJECT_ID]]"
      }
    }
  }
}
```

---

### Slide 17: 🎤 The "Nano Banana 2" Challenge
- **Module**: Module 3 • Lab Step 2: Developer Knowledge MCP
- **Pacing**: `00:37 – 00:40 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:37 - 00:40 (3 mins)
INTERACTIVE QUESTION #3: Ask the audience what 'Nano Banana 2' is!

SAY THIS:
"Now let's prove why MCP is a game-changer. How many of you have heard the codename 'Nano Banana 2'? It's the nickname for Gemini 3.1 Flash Image!
If you ask an ungrounded coding assistant to 'use Nano Banana 2 on Vertex AI', it has no idea what model ID to pass or which SDK method to call.
Let's watch what happens when we tell `agy` to use the `google-developer-knowledge` MCP server! Run the commands on the right to create `~/nano-banana-kitten`, run `uv init`, launch `agy`, and paste that prompt."
```

#### 💻 On-Slide Command / Prompt (`terminal & agy prompt — Nano Banana 2 Test`):
```bash
# 1. Exit agy (Ctrl+D twice) & enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# 2. Create project & initialize uv
mkdir -p ~/nano-banana-kitten && cd ~/nano-banana-kitten
uv init
agy

# 3. Paste this prompt into agy:
Write a script that uses Nano Banana 2 through Vertex AI to generate a picture of a cute kitten, and run the script for me. Use the google-developer-knowledge MCP when researching.
```

---

### Slide 18: ✋ Checkpoint 2: Inspect Thinking (Ctrl+O) & Kitten Output
- **Module**: Module 3 • Lab Step 2: Developer Knowledge MCP
- **Pacing**: `00:40 – 00:45 (5 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:40 - 00:45 (5 mins)
LAB CHECKPOINT #2 (Start the 5-minute timer on screen!).

SAY THIS:
"While `agy` is working, press `Ctrl+O` inside the terminal! `Ctrl+O` expands Antigravity's intermediate thinking and tool calls. You can literally watch it search the Developer Knowledge MCP server for 'Nano Banana 2', discover that it's Gemini 3.1 Flash Image, read the official Vertex AI Python snippet, install the dependencies with `uv`, and generate the image."

"Once it finishes, click on the generated `.png` file in your Cloud Shell Editor explorer to see your kitten! Give me a thumbs up or raise your hand when your kitten is on screen!"
```

---

### Slide 19: Installing Skills via Skills CLI & Installing Antigravity Plugins
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:45 – 00:47 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:45 - 00:47 (2 mins)
GOAL: Explain Codelab Step 5 — why we add both the `google-antigravity-sdk` skill and the `modern-web-guidance` plugin.

SAY THIS:
"Now we're ready for the main event: Codelab Step 5—building the full-stack Cat Delivery System! To make sure Antigravity nails both the backend agent harness and the Lit/Vite web frontend on the first try, we're going to give it two superpowers:
1. On the left, we'll use `npx skills add` to install the official `google-antigravity-sdk` skill from GitHub.
2. On the right, we'll use `agy plugin install` to install the Google Chrome team's `modern-web-guidance` plugin."
```

---

### Slide 20: Step 4: Install Skills & Plugins for Cat Delivery
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:47 – 00:50 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:47 - 00:50 (3 mins)
GOAL: Have everyone run the 4 commands and verify `/skills` inside `agy`.

SAY THIS:
"Make sure you've exited `agy` (`Ctrl+D` twice) so you're back in bash. Now copy and run these three terminal commands from Codelab Step 5:
1. Create `~/cat-delivery` and run `uv init && uv add fastapi uvicorn`.
2. Run the `npx skills add` command to pull the `google-antigravity-sdk` skill from GitHub.
3. Run `agy plugin install https://github.com/GoogleChrome/modern-web-guidance`.
Then launch `agy` and type `/skills`. You'll see a menu just like the screenshot on the right showing both skills ready for progressive activation!"
```

#### 💻 On-Slide Command / Prompt (`terminal — Setup ~/cat-delivery & Install Skills`):
```bash
# 1. Create workspace and install base backend dependencies
mkdir -p ~/cat-delivery && cd ~/cat-delivery
uv init && uv add fastapi uvicorn

# 2. Install the official Antigravity Python SDK skill
npx skills add Google-Antigravity/antigravity-sdk-python \
  --skill google-antigravity-sdk --agent antigravity-cli --yes

# 3. Install the Chrome team's modern-web-guidance plugin
agy plugin install https://github.com/GoogleChrome/modern-web-guidance

# 4. Launch agy and check installed skills
agy
/skills
```

---

### Slide 21: 🎯 Operating Modes (/fast vs /planning) & /model
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:50 – 00:52 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:50 - 00:52 (2 mins)
INTERACTIVE POLL #4: Ask attendees when they'd use High thinking + /planning vs Low thinking + /fast.

SAY THIS:
"Inside `agy`, type `/model`. You'll see models with '(Low)', '(Medium)', or '(High)' in parentheses. That's the **thinking level**—how much reasoning budget the model spends before responding. For our workshop today, choose **Gemini 3.5 Flash (Low)**—it's blazingly fast and super token-efficient. In production, a great pattern is using a High-thinking model during `/planning` and switching to Flash (Low) for implementation!"

"Next, type `/planning` to put Antigravity into Planning Mode."
```

#### 💻 On-Slide Command / Prompt (`agy — Configure Model & Planning Mode`):
```bash
# 1. Open model selector and choose Gemini 3.5 Flash (Low)
/model

# 2. Switch to Planning Mode for our full-stack build
/planning

# (You can switch back to Fast Mode anytime with /fast)
```

---

### Slide 22: Step 5: Generate the Implementation Plan
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:52 – 00:55 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:52 - 00:55 (3 mins)
GOAL: Everyone pastes the Cat Delivery System prompt into `agy` while in `/planning` mode.

SAY THIS:
"With `/planning` active, copy the full prompt from Codelab Step 5 and hit Enter! Look at how structured yet natural this prompt is:
- First, the product vision and guardrail: 'ABSOLUTELY NO DOGS - steer the user towards cats if necessary. P.S.: capybaras are allowed.'
- Second, the exact tech stack: `uv`, Backend using Antigravity SDK, Frontend using Lit & Vite in light mode, Gemini 3.5 Flash for the root agent, and Gemini 3.1 Flash Image for image generation.
- Third, explicit architectural TODOs: backend serves the static frontend, define the frontend-backend contract first, and use Google Cloud Project auth."
```

#### 💻 On-Slide Command / Prompt (`agy (/planning mode) — Full-Stack Specification Prompt`):
```bash
Create an application named "Cat Delivery System". This application will be an agent that generates cat pictures using Gemini 3.1 Flash Image (aka Nano Banana 2). The user will interact with the agent whenever it feels the need for a cat picture in their life, whether it be to make them smile, laugh or just brighten their day. Cat pictures can take any form the user desires: anime, cartoon, photorealistic, 3D render, etc. The only rule is ABSOLUTELY NO DOGS - steer the user towards cats if necessary. P.S.: capybaras are allowed.

The tech stack should be as follows:
- uv package manager
- Backend: agent using Antigravity SDK
- Frontend: simple chat window, light mode, lit / vite
- Model: Gemini 3.5 Flash for the root agent, Gemini 3.1 Flash Image for image generation

TODO:
- backend should serve a static frontend
- define the contract between frontend and backend before starting implementation
- use Google Cloud Project auth
```

---

### Slide 23: Under the Hood: Autonomous Research Phase
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:55 – 00:57 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:55 - 00:57 (2 mins)
GOAL: Point out the TUI output showing MCP + Skills working together.

SAY THIS:
"Look at your terminal while `agy` researches! You'll see it invoke BOTH the `google-developer-knowledge` MCP server AND the `google-antigravity-sdk` / `modern-web-guidance` skills we just installed. Once it finishes thinking, it stops and prompts you to review the plan—and notice the bottom-right corner says `1 artifact`!"
```

---

### Slide 24: Human-in-the-Loop Review with /artifact
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:57 – 00:59 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:57 - 00:59 (2 mins)
GOAL: Teach attendees how `/artifact` and line-by-line commenting (`C` key) work.

SAY THIS:
"This is where 'Command and Control' really shines. Type `/artifact` and hit Enter to open `implementation_plan.md`.
- Use your Up and Down arrow keys to scroll through the architecture plan.
- Check the API contract between the Lit frontend and FastAPI backend, and scroll down to the 'Verification Plan' section—that's how the agent knows what tests must pass before it can claim the job is done.
- Try pressing the `C` key on any line! You can leave inline review comments just like a GitHub PR review.
- When you're ready, press `ESC` and then `Y` (or Approve) to unleash Antigravity to build the entire app!"
```

---

### Slide 25: ✋ Checkpoint 3: Autonomous Implementation & Artifacts
- **Module**: Module 4 • Lab Step 3: Agent Skills & /planning Mode
- **Pacing**: `00:59 – 01:02 (3 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 00:59 - 01:02 (3 mins)
LAB CHECKPOINT #3 (Start the 4-minute timer while AGY builds the app!).

SAY THIS:
"Once you hit `Y` to approve the plan, sit back and watch Antigravity orchestrate the entire full-stack build! It will ask for confirmation to run `uv`, `npm`, and test commands.
Notice that the artifact counter in the bottom right increases from `1 artifact` to `3 artifacts`:
- `implementation_plan.md` is your blueprint.
- `task.md` is the live checklist the agent updates as it completes backend, frontend, and integration tasks.
- And when it finishes, it generates `walkthrough.md` summarizing everything it built and verified!"
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
# Typical generated structure in ~/cat-delivery:
cat-delivery/
├── backend/
│   ├── agent.py      # AGY SDK + Nano Banana 2 tool
│   └── main.py       # FastAPI + static file mount
├── frontend/
│   ├── src/          # Lit web components chat UI
│   └── vite.config.js
└── pyproject.toml

# Run /artifact after implementation completes:
1. implementation_plan.md  (Approved Blueprint)
2. task.md                 (Live Checklist [x])
3. walkthrough.md          (Validation Summary)
```

---

### Slide 26: Step 6: Deploy to Cloud Run in /fast Mode
- **Module**: Module 5 • Lab Step 4: Cloud Run Deployment & Verification
- **Pacing**: `01:02 – 01:06 (4 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:02 - 01:06 (4 mins)
GOAL: Switch to `/fast` mode and deploy the Cat Delivery System to Cloud Run (Codelab Step 6).

SAY THIS:
"Now our app is built locally—let's ship it to production on Google Cloud Run! This is Codelab Step 6.
Since deploying an already-architected app is a straightforward operational task, we don't need a separate planning cycle. Type `/fast` to switch Antigravity back to Fast Mode, and paste the deployment prompt on the right."

"Look at the bottom of that prompt: **Acceptance Criteria**. That is one of the most powerful pro-tips you'll learn today. Because we specify that the Frontend and Backend must be live and respond with no errors, Antigravity won't just run `gcloud run deploy` and walk away—it will actually test and audit the live Cloud Run endpoint, and if a port or Dockerfile path needs fixing, it will self-heal and redeploy automatically!"
```

#### 💻 On-Slide Command / Prompt (`agy (/fast mode) — Cloud Run Deployment Prompt`):
```bash
/fast

Deploy the agent and frontend to Cloud Run.

TODO:
- backend should serve a static frontend
- frontend and backend are deployed in the same container

Acceptance Criteria
- Agent is deployed to cloud run
- Frontend is live and renders with no errors
- Backend is live and responds to requests with no errors
```

---

### Slide 27: ✋ Checkpoint 4: Live "Break the Guardrail" Challenge!
- **Module**: Module 5 • Lab Step 4: Cloud Run Deployment & Verification
- **Pacing**: `01:06 – 01:10 (4 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:06 - 01:10 (4 mins)
INTERACTIVE CHALLENGE #5: Open the live Cloud Run URL and take prompt suggestions from the audience!

SAY THIS:
"Once `agy` prints your live `https://cat-delivery-...run.app` URL, click it to open your deployed Cat Delivery System!
Let's run three verification tests together:
1. First, ask for your favorite style of cat—cyberpunk, Studio Ghibli, pixel art, oil painting.
2. Second, try to trick it into generating a dog! Say 'I really want a golden retriever' or 'Draw a wolf that barks'. Watch Gemini 3.5 Flash politely refuse and steer you back toward cats!
3. Third, test the secret loophole from our prompt: ask for a capybara! Because we told `agy` 'P.S.: capybaras are allowed', the agent happily delivers a capybara!"
```

---

### Slide 28: Your Agentic Orchestration Playbook
- **Module**: Module 6 • Playbook, Troubleshooting & Wrap-Up
- **Pacing**: `01:10 – 01:12 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:10 - 01:12 (2 mins)
GOAL: Synthesize the 4 core lessons of the workshop.

SAY THIS:
"Pause and think about what you just accomplished in under an hour: you orchestrated a Python FastAPI + Antigravity SDK backend, a Lit + Vite web frontend, multimodal image generation with Nano Banana 2, and a serverless Cloud Run deployment—with zero manual coding.
When you go back to work on Monday, remember this 4-step Command & Control playbook:
1. Ground with MCP (`mcp_config.json`).
2. Equip with Progressive Skills (`SKILL.md`).
3. Architect first with `/planning` and `/artifact` inline comments (`C`).
4. Ship and audit with explicit Acceptance Criteria."
```

---

### Slide 29: Quick Reference: AGY CLI Commands & Shortcuts
- **Module**: Module 6 • Bonus Reference & Cheat Sheet
- **Pacing**: `Reference Slide (1/2)`

#### 🎙️ Speaker Notes:
```text
TIMING: Reference / Backup Slide (1 min or keep on screen during Q&A)
GOAL: Provide a single cheat sheet of all slash commands, hotkeys, and troubleshooting tips.

SAY THIS:
"I've included two bonus cheat-sheet slides in the deck for you to keep. This first one has every slash command (`/planning`, `/fast`, `/artifact`, `/model`, `/mcp`, `/skills`), hotkey (`Ctrl+O`, `Ctrl+D`, `C`), and common Cloud Shell troubleshooting fix."
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
/planning   # Switch to Planning Mode (creates plan artifact)
/fast       # Switch to Fast Mode (immediate execution)
/artifact   # Open & review implementation_plan.md / task.md
/model      # Switch model & thinking level (Low/Med/High)
/mcp        # Verify connected MCP servers & tools
/skills     # List discovered workspace, plugin & global skills
Ctrl + O    # Expand/collapse intermediate agent thinking
Ctrl + D x2 # Exit AGY CLI cleanly back to bash

# Fix 1: TUI menu looks garbled in Cloud Shell
-> Click 'Open Editor' and use Terminal > New Terminal (Ctrl+`)

# Fix 2: google-developer-knowledge MCP fails to connect
-> Check ~/.gemini/config/mcp_config.json: ensure [[PROJECT_ID]]
   was replaced with your real Project ID (no brackets!)
-> Ensure API is enabled:
   gcloud services enable developerknowledge.googleapis.com
```

---

### Slide 30: Going Further: Authoring Your Own Skill & Rules
- **Module**: Module 6 • Bonus Reference & Cheat Sheet
- **Pacing**: `Reference Slide (2/2)`

#### 🎙️ Speaker Notes:
```text
TIMING: Reference / Bonus Slide
GOAL: Show attendees how easy it is to write their own `SKILL.md` and `GEMINI.md` in their own repositories.

SAY THIS:
"And this second bonus slide shows how you can create your own skills and rules in 60 seconds! Just drop a `SKILL.md` file with YAML frontmatter (`name` and `description`) into `.agents/skills/` in your Git repo, or add a `GEMINI.md` file at the root of your project to enforce team-wide conventions."
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
---
name: cloud-run-security-audit
description: >-
  Audits FastAPI and Cloud Run services for least-privilege IAM,
  non-root Dockerfiles, and CORS safety. Activate before deploy.
---

# Cloud Run Security Audit Procedure
1. Verify Dockerfile runs as a non-root user.
2. Check that Vertex AI uses ADC (no hardcoded API keys).
3. Run smoke tests against /healthz before rollout.

# Project Engineering Guidelines (GEMINI.md)

- **Package Manager**: Always use `uv` (never raw `pip`).
- **Python Style**: Type-annotate all FastAPI endpoints.
- **Frontend**: Use Lit web components with Vite.
- **Testing**: Run `uv run pytest` after modifying backend code.
```

---

### Slide 31: Command and control: Orchestrate app development with Gemini and MCP
- **Module**: Module 6 • Closing
- **Pacing**: `01:12 – 01:13 (1 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:12 - 01:13 (1 min)
GOAL: Celebrate everyone completing the workshop!

SAY THIS:
"Give yourselves a huge round of applause! You have officially mastered Command and Control with Gemini, MCP, and Google Antigravity."
```

---

### Slide 32: Thank you!
- **Module**: Module 6 • Closing & Q&A
- **Pacing**: `01:13 – 01:15 (2 min)`

#### 🎙️ Speaker Notes:
```text
TIMING: 01:13 - 01:15 (2 mins + Open Q&A)
GOAL: Share final QR codes and open the floor for Q&A.

SAY THIS:
"Thank you all so much for building with me today! The top QR code links to the Codelab so you can replay or share it with your team, and the bottom QR code goes to my GitHub (`github.com/rabimba/GDE-ML-Artifacts`) where today's slides and runbook live. And the middle QR is my LinkedIn—if you take this pattern back to your team, I'd genuinely love to hear how it goes. We have a few minutes left—what questions do you have?"
```

---
