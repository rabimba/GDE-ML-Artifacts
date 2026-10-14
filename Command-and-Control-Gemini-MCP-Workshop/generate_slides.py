#!/usr/bin/env python3
"""
Generator for "Command and control: Orchestrate app development with Gemini and MCP"
Builds:
1. Command_and_Control_Gemini_MCP_Workshop.pptx (32 slides using Google Cloud Labs master layouts + full speaker notes)
2. index.html (Interactive Web Presentation Deck with Dual-Screen Presenter Console [P], Teleprompter [S], Live Quizzes & Lab Timers)
3. speaker-notes.html (Standalone continuous-scroll & mobile/tablet-friendly Speaker Notes & Script)
4. SPEAKER_NOTES_AND_SCRIPT.md (Complete Markdown Facilitator Runbook & Verbatim Speaker Script)
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
REF_PPTX = "/home/rabimba/.gemini/antigravity-cli/brain/631d0684-bfc9-4fa0-af51-b386e00dd702/scratch/coffee_agent_slides.pptx"

# ---------------------------------------------------------------------------
# COMPLETE 32-SLIDE DATA & VERBATIM SPEAKER NOTES
# ---------------------------------------------------------------------------
SLIDES_DATA = [
    # SLIDE 1
    {
        "num": 1,
        "module": "Module 0 • Welcome & Onboarding",
        "time": "00:00 – 00:02 (2 min)",
        "type": "cover",
        "title": "Command and control:\nOrchestrate app development\nwith Gemini and MCP",
        "subtitle": "Hands-On Workshop • Build & Deploy Full-Stack Agentic Apps with Zero Manual Code",
        "badge": "75-Min Interactive Workshop",
        "notes": (
            "TIMING: 00:00 - 00:02 (2 mins)\n"
            "GOAL: High-energy welcome and set the core premise of the workshop.\n\n"
            "SAY THIS:\n"
            "\"Welcome everyone! Over the next 75 minutes, we are going to do something that would have sounded impossible just two years ago: we are going to architect, build, test, and deploy a complete, full-stack multimodal cloud application to Google Cloud Run—with a reactive web frontend and a dual-model AI agent backend—without writing a single line of code by hand.\"\n\n"
            "\"Instead of acting as typists, today you are taking 'Command and Control'. You'll learn how to orchestrate Google Antigravity (AGY) using Gemini 3.5 Flash, ground it in live official docs with the Google Developer Knowledge MCP server, and equip it with specialized Agent Skills.\""
        ),
    },
    # SLIDE 2
    {
        "num": 2,
        "module": "Module 0 • Welcome & Onboarding",
        "time": "00:02 – 00:05 (3 min)",
        "type": "qr_hub",
        "title": "Workshop Hub & Essential Links",
        "subtitle": "Scan or open the Codelab now so you can follow along step-by-step",
        "cards": [
            {
                "title": "1. Workshop Codelab (Start Here)",
                "url_text": "codelabs.developers.google.com/gemini-mcp-agy",
                "url": "https://codelabs.developers.google.com/gemini-mcp-agy",
                "desc": "Full step-by-step instructions, prompts, and Cloud Shell setup for today's lab.",
                "qr": "qr_codelab.png",
            },
            {
                "title": "2. Google Antigravity Docs",
                "url_text": "antigravity.google/docs",
                "url": "https://antigravity.google/docs",
                "desc": "Official documentation for AGY CLI, IDE, MCP servers, Skills, Plugins, and Hooks.",
                "qr": "qr_agy_docs.png",
            },
            {
                "title": "3. Slides, Runbook & GDE Artifacts",
                "url_text": "github.com/rabimba/GDE-ML-Artifacts",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts",
                "desc": "Today's slides, copy-paste prompt sheet, and Antigravity SDK reference code.",
                "qr": "qr_rabimba_github.png",
            },
        ],
        "notes": (
            "TIMING: 00:02 - 00:05 (3 mins)\n"
            "ENGAGEMENT CUE: Pause for 30 seconds and make sure everyone scans the left QR code or types codelabs.developers.google.com/gemini-mcp-agy.\n\n"
            "SAY THIS:\n"
            "\"First things first—grab your phones or open a browser tab and head to the link on the left card: codelabs.developers.google.com/gemini-mcp-agy. Keep this tab open throughout the session! All the prompts and JSON snippets we'll use are right there so you don't have to type long paragraphs from the projector.\"\n\n"
            "\"Quick show of hands: who has the Codelab open on their screen right now? Awesome. Go ahead and start initializing your Google Cloud project and Cloud Shell in the background while I introduce myself and our mission.\""
        ),
    },
    # SLIDE 3
    {
        "num": 3,
        "module": "Module 0 • Welcome & Onboarding",
        "time": "00:05 – 00:07 (2 min)",
        "type": "speaker",
        "title": "Rabimba\nKaranjai",
        "subtitle": "Google Developer Expert (AI & ML)\nML Scientist - PayPal",
        "photo": "ref_slide4_pic2.jpg",
        "notes": (
            "TIMING: 00:05 - 00:07 (2 mins)\n"
            "GOAL: Quick personal introduction and establish credibility & approachability.\n\n"
            "SAY THIS:\n"
            "\"A quick bit about me—I'm Rabimba Karanjai. I'm a Google Developer Expert in AI & Machine Learning and an ML Scientist at PayPal. I spend my days building and evaluating agentic systems and developer tooling—and when I'm not orchestrating agents, as you can see from the photo, I love being on the racetrack!\"\n\n"
            "\"Speaking of racing: think of today's workshop like being the race engineer on the pit wall. Gemini is the engine, Antigravity is the chassis and harness, and MCP and Skills are your live telemetry. This is a super interactive workshop—if you hit a snag or have a question at any point, raise your hand or shout it out!\""
        ),
    },
    # SLIDE 4
    {
        "num": 4,
        "module": "Module 0 • Welcome & Onboarding",
        "time": "00:07 – 00:10 (3 min)",
        "type": "four_steps",
        "title": "Today's 75-Minute Mission",
        "subtitle": "How we'll go from an empty Cloud Shell to a deployed production agent with zero manual coding",
        "intro": "We will build the \"Cat Delivery System\" through 4 progressive hands-on checkpoints. Every module pairs a core agentic engineering pattern with immediate hands-on execution.",
        "steps": [
            {
                "num": "1",
                "title": "Hello AGY CLI\n(00:20 – 00:30)",
                "body": "Launch & authenticate Antigravity CLI inside Cloud Shell Editor. Generate, run, and inspect our first Node.js cat trivia script.",
                "highlight": False,
            },
            {
                "num": "2",
                "title": "Developer Knowledge MCP\n(00:30 – 00:45)",
                "body": "Eliminate documentation cutoffs! Connect Google's official MCP server and generate kitten art with Nano Banana 2.",
                "highlight": False,
            },
            {
                "num": "3",
                "title": "Skills & /planning Mode\n(00:45 – 01:02)",
                "body": "Install the Antigravity SDK Skill & Chrome Web Plugin. Use /planning and /artifact to architect the Cat Delivery System.",
                "highlight": False,
            },
            {
                "num": "4",
                "title": "Cloud Run & Guardrails\n(01:02 – 01:15)",
                "body": "Switch to /fast mode to containerize and deploy to Cloud Run, then try to break our 'Strictly No Dogs (Capybaras OK)' guardrail!",
                "highlight": True,
            },
        ],
        "notes": (
            "TIMING: 00:07 - 00:10 (3 mins)\n"
            "GOAL: Walk through the 4-part roadmap and announce the 'Zero Manual Code' challenge.\n\n"
            "SAY THIS:\n"
            "\"Here is our 75-minute game plan. We have one fun rule today: Hands off the code editor! Your challenge is to build the entire Cat Delivery System—backend, frontend, Dockerfile, and Cloud Run deployment—purely by steering Antigravity through prompts, MCP tools, Skills, and artifact reviews.\"\n\n"
            "\"We'll start with a quick 10-minute conceptual foundation, then jump straight into four hands-on sprints: Step 1 is getting cozy with AGY CLI; Step 2 is wiring up the Google Developer Knowledge MCP server; Step 3 is installing Agent Skills and using Planning Mode; and Step 4 is shipping to Cloud Run and testing our guardrails live.\""
        ),
    },
    # SLIDE 5
    {
        "num": 5,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:10 – 00:12 (2 min)",
        "type": "section_poll",
        "title": "From Code Autocomplete\nto Command & Control",
        "icon": "ref_slide5_pic1.png",
        "poll": {
            "question": "🎤 Quick Show of Hands: How many of you have asked an AI coding assistant to use a brand-new SDK or model, and watched it confidently invent a method that doesn't exist?",
            "options": [
                "🙋 Every single week! (The 'Hallucinated SDK' trap)",
                "🙋 It used an outdated v0.1 API from 2023!",
                "🙋 I ended up copy-pasting 10 pages of docs into the chat prompt!",
            ],
            "answer": "Why does this happen? Because even frontier LLMs have static training cutoffs and no native awareness of your team's architecture—unless we give them authoritative tools (MCP) and structured workflows (Skills).",
        },
        "notes": (
            "TIMING: 00:10 - 00:12 (2 mins)\n"
            "INTERACTIVE POLL #1: Get the room laughing and raising hands.\n\n"
            "SAY THIS:\n"
            "\"Before we type our first command, let's do a quick sanity check. Raise your hand if you've ever asked an AI coding assistant to write code for a new Google Cloud or Vertex AI feature, and it confidently gave you an import statement from 2023 that throws an ImportError!\"\n\n"
            "(Click Reveal in Web Deck / Read takeaway)\n"
            "\"Almost every hand in the room! And what do we usually do next? We go to the docs, copy 5,000 words of markdown, and paste it into the chat window. Today we stop doing manual copy-paste RAG. Let's look at how an orchestrated coding agent actually works.\""
        ),
    },
    # SLIDE 6
    {
        "num": 6,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:12 – 00:14 (2 min)",
        "type": "agent_triad",
        "headline": "An AI coding agent is a system that uses a model to reason, an agent harness to plan & execute, and MCP & skills to access authoritative knowledge and tools.",
        "boxes": [
            {"label": "MCP & Skills\n(Context & Tools)", "icon": "ref_slide6_pic9.png"},
            {"label": "Antigravity\n(Agent Harness)", "icon": "ref_slide6_pic8.png"},
            {"label": "Gemini Models\n(Reasoning & Media)", "icon": "ref_slide6_pic12.png"},
        ],
        "notes": (
            "TIMING: 00:12 - 00:14 (2 mins)\n"
            "GOAL: Define the three pillars of our workshop: Model, Agent Harness, and Tools/MCP/Skills.\n\n"
            "SAY THIS:\n"
            "\"Just like any AI agent is composed of a Model, an Agent loop, and Tools, an AI Coding Agent has three distinct parts:\n"
            "1. On the right, the Model—today we'll use Gemini 3.5 Flash for fast, token-efficient reasoning, plus Gemini 3.1 Flash Image (also known as Nano Banana 2) for image generation.\n"
            "2. In the center, the Agent Harness—Google Antigravity. Think of the harness as the engine that manages planning, file editing, terminal execution, artifacts, and human-in-the-loop permissions. We'll use Antigravity both as our CLI coding agent AND via the Antigravity Python SDK inside our app!\n"
            "3. On the left, Tools & Knowledge—specifically the Model Context Protocol (MCP) and Agent Skills.\""
        ),
    },
    # SLIDE 7
    {
        "num": 7,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:14 – 00:15 (1.5 min)",
        "type": "objectives_card",
        "title": "Objectives & Workshop Outcomes",
        "intro": "By the end of this hands-on workshop, you will orchestrate Antigravity to build and deploy the \"Cat Delivery System\" while mastering four modern agentic development skills:",
        "bullets": [
            (
                "Dual-Mode Orchestration (/fast vs /planning)",
                "Learn when to use /fast mode for immediate scripts and deployments versus /planning mode with interactive /artifact reviews for full-stack architectures.",
            ),
            (
                "Authoritative Grounding via Developer Knowledge MCP",
                "Connect Antigravity CLI directly to Google's official documentation server (developerknowledge.googleapis.com/mcp) so it writes up-to-date Vertex AI code on the first try.",
            ),
            (
                "Progressive Disclosure with Agent Skills & Plugins",
                "Install specialized skills (google-antigravity-sdk) and plugins (GoogleChrome/modern-web-guidance) that load into context only when needed.",
            ),
            (
                "End-to-End Cloud Run Deployment & Auditing",
                "Package a Lit + Vite frontend and FastAPI + Antigravity SDK backend into a single container, deploy to Cloud Run, and verify acceptance criteria automatically.",
            ),
        ],
        "notes": (
            "TIMING: 00:14 - 00:15 (1.5 mins)\n"
            "GOAL: Set clear learning outcomes.\n\n"
            "SAY THIS:\n"
            "\"Here are the four concrete outcomes you'll walk away with today:\n"
            "First, mastering Antigravity CLI's two operating modes: Fast mode and Planning mode, plus reviewing and commenting on artifacts.\n"
            "Second, connecting the Google Developer Knowledge MCP server so your agent queries live official Google docs.\n"
            "Third, installing reusable Agent Skills and Plugins using progressive disclosure.\n"
            "And fourth, orchestrating a production deployment to Google Cloud Run with automated acceptance testing.\""
        ),
    },
    # SLIDE 8
    {
        "num": 8,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:15 – 00:17 (2 min)",
        "type": "arch_split",
        "title": "Core Architecture",
        "subtitle": "Flow of the \"Cat Delivery System\" — An Agent Building an Agent",
        "intro": "Today's workshop features a two-tier agentic architecture: we use Antigravity CLI (Tier 1) to build and deploy a Cloud Run application powered by the Antigravity SDK (Tier 2).",
        "bullets": [
            (
                "Orchestration Layer (AGY CLI)",
                "Runs in Cloud Shell Editor, combining Developer Knowledge MCP + installed Skills to plan, write, and deploy the app.",
            ),
            (
                "Web Frontend (Lit + Vite)",
                "Clean, light-mode reactive chat interface bundled and served statically by our Python backend.",
            ),
            (
                "Agent Runtime (FastAPI + AGY SDK)",
                "Uses Gemini 3.5 Flash as the root agent with strict persona instructions: ABSOLUTELY NO DOGS (Capybaras allowed!).",
            ),
            (
                "Image Generation (Nano Banana 2)",
                "Invokes Gemini 3.1 Flash Image on Vertex AI to generate anime, 3D, or photorealistic cats on demand.",
            ),
        ],
        "image": "cat_delivery_architecture.png",
        "notes": (
            "TIMING: 00:15 - 00:17 (2 mins)\n"
            "GOAL: Explain the two-tier diagram clearly so attendees don't confuse Antigravity CLI with the Antigravity SDK inside the app.\n\n"
            "SAY THIS:\n"
            "\"Look closely at this architecture diagram because there's a cool meta-pattern happening today. We have two tiers:\n"
            "In Tier 1 at the top, YOU are in Cloud Shell Editor talking to Antigravity CLI (`agy`). `agy` uses the Developer Knowledge MCP server and two installed skills—the Antigravity Python SDK skill and Chrome's Modern Web Guidance plugin—to write our application.\n"
            "In Tier 2 at the bottom is the application `agy` builds for us: the Cat Delivery System running on Cloud Run! Inside that single container, FastAPI serves a static Lit & Vite chat frontend and runs a backend agent built with the Antigravity SDK. That root agent uses Gemini 3.5 Flash to chat with the user, enforce our hilarious business rule—ABSOLUTELY NO DOGS, steer dog requests to cats, though capybaras are allowed—and calls Gemini 3.1 Flash Image (Nano Banana 2) to generate custom cat pictures.\""
        ),
    },
    # SLIDE 9
    {
        "num": 9,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:17 – 00:18 (1 min)",
        "type": "three_tech",
        "title": "Key Technologies & Concepts We'll Use!",
        "cols": [
            {
                "icon": "ref_slide9_pic7.png",
                "title": "Google Antigravity\n(CLI & Python SDK)",
                "body": "Google's AI-first agentic development platform. We'll use the terminal CLI (`agy`) to orchestrate code, and the Python SDK (`google-antigravity`) as the runtime harness for our app.",
            },
            {
                "icon": "ref_slide9_pic9.jpg",
                "title": "Developer Knowledge\nMCP & Agent Skills",
                "body": "Open standards for extending agents. MCP connects `agy` to live Google documentation APIs, while Agent Skills (`SKILL.md`) provide progressive, on-demand procedural expertise.",
            },
            {
                "icon": "ref_slide9_pic8.png",
                "title": "Gemini 3.5 Flash, Nano\nBanana 2 & Cloud Run",
                "body": "Gemini 3.5 Flash powers fast agent reasoning, Gemini 3.1 Flash Image (Nano Banana 2) generates images, and Cloud Run hosts our container serverlessly.",
            },
        ],
        "notes": (
            "TIMING: 00:17 - 00:18 (1 min)\n"
            "GOAL: Quick visual summary of the 3 tech stacks before the interactive quiz.\n\n"
            "SAY THIS:\n"
            "\"So our toolkit comes down to three pillars: Google Antigravity (both the CLI and the Python SDK), Open Context Standards (Model Context Protocol and Agent Skills), and Google Cloud's serverless AI stack (Gemini 3.5 Flash, Nano Banana 2, and Cloud Run).\""
        ),
    },
    # SLIDE 10
    {
        "num": 10,
        "module": "Module 1 • Concepts & Architecture",
        "time": "00:18 – 00:20 (2 min)",
        "type": "two_cards_quiz",
        "left_card": {
            "color": "blue",
            "title": "Model Context Protocol (MCP)",
            "subtitle": "Live External Tools & Authoritative Data",
            "items": [
                (
                    "What It Is",
                    "An open protocol connecting AI agents to external APIs, databases, and documentation servers via standardized tool calls.",
                ),
                (
                    "Google Developer Knowledge MCP",
                    "Hosted at developerknowledge.googleapis.com/mcp. Lets coding agents search & fetch live docs for Cloud, Vertex AI, Firebase, Android, and Maps.",
                ),
                (
                    "Best For",
                    "Dynamic lookups, querying live systems, and ensuring SDK/API usage is 100% current.",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Agent Skills & Plugins",
            "subtitle": "Progressive Disclosure of Workflows (agentskills.io)",
            "items": [
                (
                    "What They Are",
                    "Lightweight folders containing a SKILL.md instruction file (plus optional scripts/templates) that teach an agent how to perform specialized tasks.",
                ),
                (
                    "Progressive Disclosure",
                    "At startup, ONLY the skill's name & short description are in the prompt. The full SKILL.md is loaded ONLY when the agent activates it—saving massive tokens!",
                ),
                (
                    "Plugins",
                    "Bundle Skills + MCP servers + Rules + Hooks into a single installable package.",
                ),
            ],
        },
        "quiz": {
            "question": "🎯 Quick Quiz: You want your agent to follow your team's 15-page FastAPI + Lit architecture guide without wasting 20,000 tokens on every single chat turn. Do you use an MCP Server or an Agent Skill?",
            "answer": "✅ Agent Skill (SKILL.md)! Because of Progressive Disclosure, the 15-page guide stays on disk costing ~30 tokens of metadata until you actually ask the agent to build a FastAPI/Lit app!",
        },
        "notes": (
            "TIMING: 00:18 - 00:20 (2 mins)\n"
            "INTERACTIVE QUIZ #2: Ask the room to vote between MCP Server vs Agent Skill!\n\n"
            "SAY THIS:\n"
            "\"People always ask me: 'Rabimba, when do I use an MCP server versus an Agent Skill?' Look at these two cards:\n"
            "- MCP (on the left) is for live, external queries and actions—like searching Google's massive, constantly updated Developer Documentation database.\n"
            "- Agent Skills (on the right) use an open standard (agentskills.io) built around a magic concept called Progressive Disclosure. Instead of stuffing ten thousand tokens of instructions into your system prompt, Antigravity only reads the 2-line description of each skill at startup. When—and only when—a task matches that skill, the agent reads the full `SKILL.md` file on demand.\"\n\n"
            "\"So pop quiz for the room: if you have a 15-page team architecture guide and you don't want it burning 20,000 tokens on every turn, which one do you use? Shout it out! ... Exactly: an Agent Skill!\""
        ),
    },
    # SLIDE 11
    {
        "num": 11,
        "module": "Module 2 • Lab Step 1: Hello Antigravity CLI",
        "time": "00:20 – 00:21 (1 min)",
        "type": "lab_divider",
        "title": "Let's build this!",
        "subtitle": "Lab Step 1 — Setting Up Cloud Shell Editor & Authenticating Antigravity CLI (agy)",
        "notes": (
            "TIMING: 00:20 - 00:21 (1 min)\n"
            "TRANSITION TO HANDS-ON LAB 1.\n\n"
            "SAY THIS:\n"
            "\"Theory time is over—time to get our hands on the keyboard! Everyone switch over to your Google Cloud Console tab and Codelab Step 2 & 3.\""
        ),
    },
    # SLIDE 12
    {
        "num": 12,
        "module": "Module 2 • Lab Step 1: Hello Antigravity CLI",
        "time": "00:21 – 00:24 (3 min)",
        "type": "code_split",
        "title": "Step 1: Open Cloud Shell Editor Terminal",
        "subtitle": "Critical Workaround for Clean TUI Rendering",
        "intro": "While Cloud Shell comes with Antigravity pre-installed, the default Cloud Shell bottom pane doesn't render advanced TUI menus properly. Always use the terminal inside Cloud Shell Editor!",
        "bullets": [
            (
                "1. Activate Cloud Shell",
                "Click the 'Activate Cloud Shell' icon (>_) in the top-right toolbar of the Google Cloud Console.",
            ),
            (
                "2. Click 'Open Editor'",
                "Click the pencil/editor icon on the Cloud Shell toolbar (and maximize the window) to launch the Cloud Shell Editor.",
            ),
            (
                "3. Open Integrated Terminal",
                "Use menu Terminal > New Terminal or press Ctrl + ` (Control + backtick) to open the bash prompt inside the editor.",
            ),
        ],
        "code_title": "terminal — Cloud Shell Editor (Ctrl + `)",
        "code": (
            "# Create a working directory for our warm-up exercise\n"
            "mkdir -p ~/hello-agy && cd ~/hello-agy\n\n"
            "# Launch Antigravity CLI\n"
            "agy"
        ),
        "screenshot": "codelab_307efeaef3537ba3.png",
        "notes": (
            "TIMING: 00:21 - 00:24 (3 mins)\n"
            "CRITICAL FACILITATOR TIP: Emphasize clicking 'Open Editor' and using Terminal > New Terminal (Ctrl + `). If someone runs `agy` in the raw non-editor Cloud Shell pane, the TUI menus look garbled.\n\n"
            "SAY THIS:\n"
            "\"Pay super close attention to Step 2 here—this will save you a ton of headache! Once Cloud Shell connects, click the 'Open Editor' button on the top bar. Inside the Cloud Shell Editor, go to the top menu and click Terminal -> New Terminal (or press Ctrl + backtick). Why? Because Antigravity has a rich interactive terminal UI with diff viewers and menus that render much cleaner inside the Editor's terminal.\"\n\n"
            "\"Once your terminal is open, run `mkdir -p ~/hello-agy && cd ~/hello-agy` and type `agy`!\""
        ),
    },
    # SLIDE 13
    {
        "num": 13,
        "module": "Module 2 • Lab Step 1: Hello Antigravity CLI",
        "time": "00:24 – 00:27 (3 min)",
        "type": "stepper_split",
        "title": "Step 2: Authenticate Antigravity CLI",
        "steps": [
            ("01", "Select Auth Mode", "Choose 'Use a Google Cloud project'"),
            ("02", "Complete OAuth Flow", "Open link in incognito tab & paste auth code"),
            ("03", "Set Project & Location", "Enter your PROJECT_ID & choose 'global'"),
        ],
        "callout_badge": "AUTHENTICATION CHECKLIST",
        "callout_title": "Use Incognito & Select 'global' Location",
        "callout_body": (
            "Copy the OAuth URL shown in agy and open it in a new tab of your SAME incognito window so you log in with your workshop student credentials. When prompted for location, select 'global'."
        ),
        "code_title": "agy — First-Time Authentication Flow",
        "code": (
            "? How would you like to authenticate?\n"
            "> 1. Use a Google Cloud project\n\n"
            "Paste authorization code: [PASTE_CODE_HERE]\n"
            "Enter Google Cloud Project ID: [YOUR_PROJECT_ID]\n"
            "Select Google Cloud Location: > global"
        ),
        "screenshot": "codelab_c307f5f610adb95a.png",
        "notes": (
            "TIMING: 00:24 - 00:27 (3 mins)\n"
            "GOAL: Walk everyone through the 3 authentication prompts inside `agy`.\n\n"
            "SAY THIS:\n"
            "\"The first time `agy` launches, it asks how you want to authenticate:\n"
            "1. Select 'Use a Google Cloud project'.\n"
            "2. It will print a URL. Copy that link, paste it into another tab in your SAME incognito browser window, sign in with your lab account, and copy the authorization code back into `agy`.\n"
            "3. Next, paste your Google Cloud Project ID, and when it asks for Google Cloud Location, select `global`. Why `global`? Because frontier preview endpoints like Gemini 3.5 and Gemini 3.1 Flash Image route through the global endpoint on Vertex AI.\""
        ),
    },
    # SLIDE 14
    {
        "num": 14,
        "module": "Module 2 • Lab Step 1: Hello Antigravity CLI",
        "time": "00:27 – 00:30 (3 min)",
        "type": "two_cards_code",
        "title": "✋ Checkpoint 1: Generate & Run Cat Trivia",
        "timer_seconds": 180,
        "left_card": {
            "color": "blue",
            "title": "1. Prompt & Approve Tool Execution",
            "subtitle": "Human-in-the-Loop Permission Model",
            "code": (
                "Write a simple node script that returns cat trivia and run it for me"
            ),
            "bullets": [
                (
                    "Autonomous Coding",
                    "AGY writes cat-trivia.js fetching random facts from catfact.ninja/fact with ASCII art.",
                ),
                (
                    "Permission Gate",
                    "Before running shell commands (`node cat-trivia.js`), AGY pauses and asks for permission. Select `1. Yes`.",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "2. Inspect Output & Ask for Explanation",
            "subtitle": "Conversational Code Understanding",
            "code": (
                "Explain the code you generated please\n\n"
                "# When finished, exit AGY CLI:\n"
                "# Press Ctrl+D twice"
            ),
            "bullets": [
                (
                    "ASCII Cat & Trivia Output",
                    "AGY executes the script, captures stdout, and displays your cat fact right in the TUI.",
                ),
                (
                    "Clean Exit",
                    "After reading the code explanation, press `Ctrl+D` twice to exit `agy` back to bash.",
                ),
            ],
        },
        "notes": (
            "TIMING: 00:27 - 00:30 (3 mins)\n"
            "LAB CHECKPOINT #1 (Start the 3-minute timer on screen!).\n\n"
            "SAY THIS:\n"
            "\"Now that you're inside `agy`, paste our first prompt: `Write a simple node script that returns cat trivia and run it for me`.\n"
            "Watch what happens: `agy` writes `cat-trivia.js`, and before it runs `node cat-trivia.js`, it stops and asks your permission! Notice you can allow it once, allow for this session, or persist to `settings.json`. Choose `1. Yes`.\"\n\n"
            "\"Once you see the ASCII cat and trivia fact on your screen, ask `Explain the code you generated please`, and then press `Ctrl+D` twice to exit back to the terminal. Raise your hand once you've got your ASCII cat fact!\""
        ),
    },
    # SLIDE 15
    {
        "num": 15,
        "module": "Module 3 • Lab Step 2: Developer Knowledge MCP",
        "time": "00:30 – 00:33 (3 min)",
        "type": "code_split",
        "title": "Inside ~/.gemini: AGY Configuration Layout",
        "subtitle": "Where Antigravity Stores Brains, MCP Servers, Skills & Rules",
        "intro": "Before we connect the Google Developer Knowledge MCP server, let's look at how Antigravity organizes its global configuration inside your home directory (`~/.gemini`).",
        "bullets": [
            (
                "antigravity-cli/brain/",
                "Persists conversation transcripts and generated artifacts (implementation_plan.md, task.md, walkthrough.md).",
            ),
            (
                "config/mcp_config.json",
                "Global registry of Model Context Protocol (MCP) servers available across all your workspaces.",
            ),
            (
                "skills/ & config/plugins/",
                "Houses installed Agent Skills (`SKILL.md`) and multi-capability Plugins.",
            ),
            (
                "Enable the API",
                "Run `gcloud services enable developerknowledge.googleapis.com` to activate the MCP endpoint on your project.",
            ),
        ],
        "code_title": "~/.gemini — Directory Hierarchy",
        "code": (
            "~/.gemini\n"
            "├── antigravity/\n"
            "├── antigravity-cli/\n"
            "│   ├── brain/            # Conversations and artifacts\n"
            "│   └── settings.json     # CLI settings\n"
            "├── config/\n"
            "│   ├── plugins/          # Global / shared plugins\n"
            "│   └── mcp_config.json   # Global / shared MCP config\n"
            "├── skills/               # Global / shared skills\n"
            "│   └── {skill_name}/\n"
            "│       └── SKILL.md      # Skill definition\n"
            "└── GEMINI.md             # Global rules"
        ),
        "notes": (
            "TIMING: 00:30 - 00:33 (3 mins)\n"
            "GOAL: Demystify `~/.gemini` so attendees understand where `brain/`, `mcp_config.json`, `skills/`, and `GEMINI.md` live.\n\n"
            "SAY THIS:\n"
            "\"Let's move to Codelab Step 4! Everything Antigravity knows about your global setup lives in a clean hidden directory: `~/.gemini`.\n"
            "- `antigravity-cli/brain/` is where your conversation history and artifacts—like plans and task lists—are stored.\n"
            "- `config/mcp_config.json` is where we register MCP servers.\n"
            "- `skills/` and `config/plugins/` hold our reusable skills and plugins.\n"
            "- And `GEMINI.md` holds global rules you want enforced everywhere.\""
        ),
    },
    # SLIDE 16
    {
        "num": 16,
        "module": "Module 3 • Lab Step 2: Developer Knowledge MCP",
        "time": "00:33 – 00:37 (4 min)",
        "type": "code_split",
        "title": "Step 3: Configure Developer Knowledge MCP",
        "subtitle": "Connecting AGY to Official Google Documentation",
        "intro": "By adding `google-developer-knowledge` to `~/.gemini/config/mcp_config.json`, Antigravity gains direct search & retrieval tools over official Google Cloud, Vertex AI, Firebase, and Android docs.",
        "bullets": [
            (
                "1. Enable Developer Knowledge API",
                "Run: `gcloud services enable developerknowledge.googleapis.com`",
            ),
            (
                "2. Edit ~/.gemini/config/mcp_config.json",
                "Run: `mkdir -p ~/.gemini/config && cloudshell edit ~/.gemini/config/mcp_config.json`",
            ),
            (
                "3. Replace [[PROJECT_ID]]",
                "IMPORTANT: Replace `[[PROJECT_ID]]` in `X-goog-user-project` with your actual Google Cloud Project ID!",
            ),
            (
                "4. Verify in AGY with /mcp",
                "Launch `agy` and run `/mcp` to confirm `google-developer-knowledge` is active.",
            ),
        ],
        "code_title": "~/.gemini/config/mcp_config.json",
        "code": (
            "{\n"
            '  "mcpServers": {\n'
            '    "google-developer-knowledge": {\n'
            '      "url": "https://developerknowledge.googleapis.com/mcp",\n'
            '      "authProviderType": "google_credentials",\n'
            '      "oauth": {\n'
            '        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]\n'
            '      },\n'
            '      "timeout": 30000,\n'
            '      "headers": {\n'
            '        "X-goog-user-project": "[[PROJECT_ID]]"\n'
            '      }\n'
            '    }\n'
            '  }\n'
            "}"
        ),
        "screenshot": "codelab_f104490ade24fa5e.png",
        "notes": (
            "TIMING: 00:33 - 00:37 (4 mins)\n"
            "CRITICAL FACILITATOR TIP: Remind attendees to replace `[[PROJECT_ID]]` (including the double brackets!) with their actual Project ID.\n\n"
            "SAY THIS:\n"
            "\"Let's wire up the Developer Knowledge MCP server right now:\n"
            "First, in your bash terminal, enable the API: `gcloud services enable developerknowledge.googleapis.com`.\n"
            "Second, create and open the config file: `mkdir -p ~/.gemini/config && cloudshell edit ~/.gemini/config/mcp_config.json`.\n"
            "Third, paste the JSON from Codelab Step 4—and WATCH OUT for line 13: replace `[[PROJECT_ID]]` (remove the square brackets too!) with your actual Google Cloud Project ID.\n"
            "Finally, launch `agy` and type `/mcp`. You should see `google-developer-knowledge` listed and connected!\""
        ),
    },
    # SLIDE 17
    {
        "num": 17,
        "module": "Module 3 • Lab Step 2: Developer Knowledge MCP",
        "time": "00:37 – 00:40 (3 min)",
        "type": "code_split",
        "title": "🎤 The \"Nano Banana 2\" Challenge",
        "subtitle": "Why Ungrounded Agents Fail vs. How MCP Succeeds",
        "intro": "Let's test our new MCP server with a prompt that mentions \"Nano Banana 2\"—the nickname for Google's Gemini 3.1 Flash Image generation model.",
        "bullets": [
            (
                "🎤 Pop Quiz for the Room",
                "What happens if you ask a standard LLM (without MCP) to 'Write a Vertex AI script using Nano Banana 2'?",
            ),
            (
                "Without MCP: Hallucination!",
                "The model either thinks 'Nano Banana 2' is a fictional fruit API or guesses an obsolete `vertexai.preview.vision_models` call.",
            ),
            (
                "With Developer Knowledge MCP",
                "AGY searches official Google docs for 'Nano Banana 2', discovers it maps to `gemini-3.1-flash-image-preview` via the `google-genai` SDK, and writes working code!",
            ),
        ],
        "code_title": "terminal & agy prompt — Nano Banana 2 Test",
        "code": (
            "# 1. Exit agy (Ctrl+D twice) & enable Vertex AI API\n"
            "gcloud services enable aiplatform.googleapis.com\n\n"
            "# 2. Create project & initialize uv\n"
            "mkdir -p ~/nano-banana-kitten && cd ~/nano-banana-kitten\n"
            "uv init\n"
            "agy\n\n"
            "# 3. Paste this prompt into agy:\n"
            "Write a script that uses Nano Banana 2 through Vertex AI to generate a picture of a cute kitten, and run the script for me. Use the google-developer-knowledge MCP when researching."
        ),
        "notes": (
            "TIMING: 00:37 - 00:40 (3 mins)\n"
            "INTERACTIVE QUESTION #3: Ask the audience what 'Nano Banana 2' is!\n\n"
            "SAY THIS:\n"
            "\"Now let's prove why MCP is a game-changer. How many of you have heard the codename 'Nano Banana 2'? It's the nickname for Gemini 3.1 Flash Image!\n"
            "If you ask an ungrounded coding assistant to 'use Nano Banana 2 on Vertex AI', it has no idea what model ID to pass or which SDK method to call.\n"
            "Let's watch what happens when we tell `agy` to use the `google-developer-knowledge` MCP server! Run the commands on the right to create `~/nano-banana-kitten`, run `uv init`, launch `agy`, and paste that prompt.\""
        ),
    },
    # SLIDE 18
    {
        "num": 18,
        "module": "Module 3 • Lab Step 2: Developer Knowledge MCP",
        "time": "00:40 – 00:45 (5 min)",
        "type": "checkpoint_visual",
        "title": "✋ Checkpoint 2: Inspect Thinking (Ctrl+O) & Kitten Output",
        "timer_seconds": 300,
        "bullets": [
            (
                "Press Ctrl+O in AGY",
                "Expands intermediate thinking steps! Watch AGY call `google-developer-knowledge` search & fetch tools to look up `gemini-3.1-flash-image`.",
            ),
            (
                "Autonomous Dependency Management",
                "AGY automatically adds `google-genai` / `pillow` via `uv add`, writes the Python script, and executes it.",
            ),
            (
                "Self-Healing on Errors",
                "If an environment variable or project flag is needed, AGY reads the traceback, fixes the script, and re-runs until the image is saved!",
            ),
            (
                "View Your Kitten! =^_^=",
                "Click the generated `.png` file in the Cloud Shell Editor file tree on the left to see your AI-generated kitten.",
            ),
        ],
        "screenshot": "codelab_8c74ee97ffb3caf3.png",
        "caption": "Cloud Shell Editor showing the generated kitten image alongside AGY's terminal execution.",
        "notes": (
            "TIMING: 00:40 - 00:45 (5 mins)\n"
            "LAB CHECKPOINT #2 (Start the 5-minute timer on screen!).\n\n"
            "SAY THIS:\n"
            "\"While `agy` is working, press `Ctrl+O` inside the terminal! `Ctrl+O` expands Antigravity's intermediate thinking and tool calls. You can literally watch it search the Developer Knowledge MCP server for 'Nano Banana 2', discover that it's Gemini 3.1 Flash Image, read the official Vertex AI Python snippet, install the dependencies with `uv`, and generate the image.\"\n\n"
            "\"Once it finishes, click on the generated `.png` file in your Cloud Shell Editor explorer to see your kitten! Give me a thumbs up or raise your hand when your kitten is on screen!\""
        ),
    },
    # SLIDE 19
    {
        "num": 19,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:45 – 00:47 (2 min)",
        "type": "two_cards_quiz",
        "left_card": {
            "color": "blue",
            "title": "Installing Skills via Skills CLI",
            "subtitle": "Open Marketplace & GitHub Repos (npx skills)",
            "items": [
                (
                    "Why We Need Skills Here",
                    "Official docs great for APIs, but building an agent with the Antigravity SDK requires opinionated multi-file patterns and harness conventions.",
                ),
                (
                    "GitHub Skill Installation",
                    "Using Vercel's `npx skills add` CLI, we can install any skill directly from a GitHub repo containing a `skills/` folder.",
                ),
                (
                    "google-antigravity-sdk Skill",
                    "Teaches `agy` how to properly instantiate, configure, and stream from the Antigravity Python SDK.",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Installing Antigravity Plugins",
            "subtitle": "Cohesive Bundles via `agy plugin install`",
            "items": [
                (
                    "What's Inside a Plugin?",
                    "A single package that can bundle Skills (`SKILL.md`), MCP servers (`mcp_config.json`), Rules (`GEMINI.md`), and Hooks (`hooks.json`).",
                ),
                (
                    "Chrome's modern-web-guidance",
                    "Written by the Google Chrome team—teaches `agy` modern web best practices for Lit, Vite, responsive layouts, and clean UI architecture.",
                ),
                (
                    "Inspecting Loaded Skills",
                    "Run `/skills` inside `agy` at any time to inspect all discovered workspace, plugin, and global skills.",
                ),
            ],
        },
        "quiz": {
            "question": "💡 Security Tip: Skills and Plugins can contain executable helper scripts and lifecycle hooks. What is the #1 rule when installing skills from open marketplaces like skills.sh?",
            "answer": "🔒 Always verify the publisher and only install skills/plugins from reputable, trusted repositories (like Google-Antigravity or GoogleChrome)!",
        },
        "notes": (
            "TIMING: 00:45 - 00:47 (2 mins)\n"
            "GOAL: Explain Codelab Step 5 — why we add both the `google-antigravity-sdk` skill and the `modern-web-guidance` plugin.\n\n"
            "SAY THIS:\n"
            "\"Now we're ready for the main event: Codelab Step 5—building the full-stack Cat Delivery System! To make sure Antigravity nails both the backend agent harness and the Lit/Vite web frontend on the first try, we're going to give it two superpowers:\n"
            "1. On the left, we'll use `npx skills add` to install the official `google-antigravity-sdk` skill from GitHub.\n"
            "2. On the right, we'll use `agy plugin install` to install the Google Chrome team's `modern-web-guidance` plugin.\""
        ),
    },
    # SLIDE 20
    {
        "num": 20,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:47 – 00:50 (3 min)",
        "type": "code_split",
        "title": "Step 4: Install Skills & Plugins for Cat Delivery",
        "subtitle": "Equipping AGY with Backend SDK & Modern Web Expertise",
        "intro": "Exit `agy` (`Ctrl+D` twice) and run these commands in your terminal to initialize the `~/cat-delivery` project and install both skills.",
        "bullets": [
            (
                "1. Initialize Project with uv",
                "Create `~/cat-delivery`, run `uv init`, and add `fastapi` and `uvicorn`.",
            ),
            (
                "2. Add Antigravity SDK Skill",
                "Runs `npx skills add Google-Antigravity/antigravity-sdk-python` targeting `--agent antigravity-cli`.",
            ),
            (
                "3. Install Chrome Web Plugin",
                "Runs `agy plugin install https://github.com/GoogleChrome/modern-web-guidance`.",
            ),
            (
                "4. Verify with /skills",
                "Launch `agy` and type `/skills` to confirm both skills appear in the menu!",
            ),
        ],
        "code_title": "terminal — Setup ~/cat-delivery & Install Skills",
        "code": (
            "# 1. Create workspace and install base backend dependencies\n"
            "mkdir -p ~/cat-delivery && cd ~/cat-delivery\n"
            "uv init && uv add fastapi uvicorn\n\n"
            "# 2. Install the official Antigravity Python SDK skill\n"
            "npx skills add Google-Antigravity/antigravity-sdk-python \\\n"
            "  --skill google-antigravity-sdk --agent antigravity-cli --yes\n\n"
            "# 3. Install the Chrome team's modern-web-guidance plugin\n"
            "agy plugin install https://github.com/GoogleChrome/modern-web-guidance\n\n"
            "# 4. Launch agy and check installed skills\n"
            "agy\n"
            "/skills"
        ),
        "screenshot": "codelab_cfdb4b5212fa94e1.png",
        "notes": (
            "TIMING: 00:47 - 00:50 (3 mins)\n"
            "GOAL: Have everyone run the 4 commands and verify `/skills` inside `agy`.\n\n"
            "SAY THIS:\n"
            "\"Make sure you've exited `agy` (`Ctrl+D` twice) so you're back in bash. Now copy and run these three terminal commands from Codelab Step 5:\n"
            "1. Create `~/cat-delivery` and run `uv init && uv add fastapi uvicorn`.\n"
            "2. Run the `npx skills add` command to pull the `google-antigravity-sdk` skill from GitHub.\n"
            "3. Run `agy plugin install https://github.com/GoogleChrome/modern-web-guidance`.\n"
            "Then launch `agy` and type `/skills`. You'll see a menu just like the screenshot on the right showing both skills ready for progressive activation!\""
        ),
    },
    # SLIDE 21
    {
        "num": 21,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:50 – 00:52 (2 min)",
        "type": "code_split",
        "title": "🎯 Operating Modes (/fast vs /planning) & /model",
        "subtitle": "Matching Agent Autonomy & Thinking Level to Task Complexity",
        "intro": "Before we prompt `agy` to build the full application, we need to configure two key levers: the **Operating Mode** and the **Model Thinking Level**.",
        "bullets": [
            (
                "/fast Mode (Immediate Execution)",
                "Starts writing files and running commands immediately. Best for simple, self-contained tasks (like our cat-trivia script or deploying an already-built app).",
            ),
            (
                "/planning Mode (Design First)",
                "Researches the problem first and produces an `implementation_plan.md` artifact for you to review, comment on, and approve before writing code.",
            ),
            (
                "/model & Thinking Levels",
                "Run `/model` and select **Gemini 3.5 Flash (Low)**. 'Low' thinking gives super-fast responses and great token economics; 'High' spends more tokens reasoning deeply.",
            ),
        ],
        "code_title": "agy — Configure Model & Planning Mode",
        "code": (
            "# 1. Open model selector and choose Gemini 3.5 Flash (Low)\n"
            "/model\n\n"
            "# 2. Switch to Planning Mode for our full-stack build\n"
            "/planning\n\n"
            "# (You can switch back to Fast Mode anytime with /fast)"
        ),
        "screenshot": "codelab_db085a557b145806.png",
        "notes": (
            "TIMING: 00:50 - 00:52 (2 mins)\n"
            "INTERACTIVE POLL #4: Ask attendees when they'd use High thinking + /planning vs Low thinking + /fast.\n\n"
            "SAY THIS:\n"
            "\"Inside `agy`, type `/model`. You'll see models with '(Low)', '(Medium)', or '(High)' in parentheses. That's the **thinking level**—how much reasoning budget the model spends before responding. For our workshop today, choose **Gemini 3.5 Flash (Low)**—it's blazingly fast and super token-efficient. In production, a great pattern is using a High-thinking model during `/planning` and switching to Flash (Low) for implementation!\"\n\n"
            "\"Next, type `/planning` to put Antigravity into Planning Mode.\""
        ),
    },
    # SLIDE 22
    {
        "num": 22,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:52 – 00:55 (3 min)",
        "type": "code_split",
        "title": "Step 5: Generate the Implementation Plan",
        "subtitle": "Prompting the \"Cat Delivery System\" in /planning Mode",
        "intro": "Make sure you are in `/planning` mode, then send this specification prompt to `agy`. Notice how we specify the persona rules, tech stack, and contract-first TODOs!",
        "bullets": [
            (
                "Persona & Guardrail Rule",
                "Generates cat pictures in any style (anime, cartoon, photorealistic, 3D). Rule: ABSOLUTELY NO DOGS—steer toward cats! P.S.: Capybaras are allowed.",
            ),
            (
                "Dual-Model Spec",
                "Gemini 3.5 Flash for the root conversational agent + Gemini 3.1 Flash Image (Nano Banana 2) for image generation.",
            ),
            (
                "Contract-First Architecture",
                "Requires `agy` to define the contract between the Lit/Vite frontend and Antigravity SDK backend before coding.",
            ),
        ],
        "code_title": "agy (/planning mode) — Full-Stack Specification Prompt",
        "code": (
            'Create an application named "Cat Delivery System". This application will be an agent that generates cat pictures using Gemini 3.1 Flash Image (aka Nano Banana 2). The user will interact with the agent whenever it feels the need for a cat picture in their life, whether it be to make them smile, laugh or just brighten their day. Cat pictures can take any form the user desires: anime, cartoon, photorealistic, 3D render, etc. The only rule is ABSOLUTELY NO DOGS - steer the user towards cats if necessary. P.S.: capybaras are allowed.\n\n'
            "The tech stack should be as follows:\n"
            "- uv package manager\n"
            "- Backend: agent using Antigravity SDK\n"
            "- Frontend: simple chat window, light mode, lit / vite\n"
            "- Model: Gemini 3.5 Flash for the root agent, Gemini 3.1 Flash Image for image generation\n\n"
            "TODO:\n"
            "- backend should serve a static frontend\n"
            "- define the contract between frontend and backend before starting implementation\n"
            "- use Google Cloud Project auth"
        ),
        "notes": (
            "TIMING: 00:52 - 00:55 (3 mins)\n"
            "GOAL: Everyone pastes the Cat Delivery System prompt into `agy` while in `/planning` mode.\n\n"
            "SAY THIS:\n"
            "\"With `/planning` active, copy the full prompt from Codelab Step 5 and hit Enter! Look at how structured yet natural this prompt is:\n"
            "- First, the product vision and guardrail: 'ABSOLUTELY NO DOGS - steer the user towards cats if necessary. P.S.: capybaras are allowed.'\n"
            "- Second, the exact tech stack: `uv`, Backend using Antigravity SDK, Frontend using Lit & Vite in light mode, Gemini 3.5 Flash for the root agent, and Gemini 3.1 Flash Image for image generation.\n"
            "- Third, explicit architectural TODOs: backend serves the static frontend, define the frontend-backend contract first, and use Google Cloud Project auth.\""
        ),
    },
    # SLIDE 23
    {
        "num": 23,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:55 – 00:57 (2 min)",
        "type": "checkpoint_visual",
        "title": "Under the Hood: Autonomous Research Phase",
        "bullets": [
            (
                "Skills Activated on Demand",
                "Watch the TUI: `agy` automatically activates `google-antigravity-sdk` and `modern-web-guidance` skills to learn the exact SDK & Lit/Vite patterns.",
            ),
            (
                "Live MCP Queries",
                "Simultaneously queries `google-developer-knowledge` MCP to verify Gemini 3.1 Flash Image parameters and Vertex AI auth.",
            ),
            (
                "Zero Premature Coding",
                "Because we're in `/planning` mode, `agy` does NOT start randomly creating files—it synthesizes everything into a formal `implementation_plan.md` artifact.",
            ),
            (
                "Look for '1 artifact' Badge",
                "When research completes, look at the bottom-right corner of the terminal for `1 artifact` and the `/artifact` hint!",
            ),
        ],
        "screenshot": "codelab_15194975b2519818.png",
        "caption": "AGY invoking both the Developer Knowledge MCP server and installed Agent Skills during the planning research phase.",
        "notes": (
            "TIMING: 00:55 - 00:57 (2 mins)\n"
            "GOAL: Point out the TUI output showing MCP + Skills working together.\n\n"
            "SAY THIS:\n"
            "\"Look at your terminal while `agy` researches! You'll see it invoke BOTH the `google-developer-knowledge` MCP server AND the `google-antigravity-sdk` / `modern-web-guidance` skills we just installed. Once it finishes thinking, it stops and prompts you to review the plan—and notice the bottom-right corner says `1 artifact`!\""
        ),
    },
    # SLIDE 24
    {
        "num": 24,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:57 – 00:59 (2 min)",
        "type": "four_steps",
        "title": "Human-in-the-Loop Review with /artifact",
        "subtitle": "How to Inspect, Comment On, and Approve `implementation_plan.md`",
        "intro": "In Antigravity, supporting documents (`implementation_plan.md`, `task.md`, `walkthrough.md`) are called **Artifacts**. You can review and annotate them line-by-line right in the CLI!",
        "steps": [
            {
                "num": "1",
                "title": "Run /artifact",
                "body": "Type `/artifact` in the prompt. Select `implementation_plan.md` from the list and press Enter to open the interactive viewer.",
                "highlight": False,
            },
            {
                "num": "2",
                "title": "Check API Contract & Verification",
                "body": "Scroll with arrow keys (`↑`/`↓`). Verify the Frontend ↔ Backend JSON contract and check the 'Verification Plan' section at the bottom.",
                "highlight": False,
            },
            {
                "num": "3",
                "title": "Add Inline Comments (Press C)",
                "body": "Want to tweak an endpoint, port, or UI detail? Navigate to any line and press `C` to attach a comment directly to that line!",
                "highlight": False,
            },
            {
                "num": "4",
                "title": "Approve & Execute (ESC → Y)",
                "body": "When happy with the plan, press `ESC` to exit the viewer and press `Y` to send your approval/comments to the agent and start coding!",
                "highlight": True,
            },
        ],
        "notes": (
            "TIMING: 00:57 - 00:59 (2 mins)\n"
            "GOAL: Teach attendees how `/artifact` and line-by-line commenting (`C` key) work.\n\n"
            "SAY THIS:\n"
            "\"This is where 'Command and Control' really shines. Type `/artifact` and hit Enter to open `implementation_plan.md`.\n"
            "- Use your Up and Down arrow keys to scroll through the architecture plan.\n"
            "- Check the API contract between the Lit frontend and FastAPI backend, and scroll down to the 'Verification Plan' section—that's how the agent knows what tests must pass before it can claim the job is done.\n"
            "- Try pressing the `C` key on any line! You can leave inline review comments just like a GitHub PR review.\n"
            "- When you're ready, press `ESC` and then `Y` (or Approve) to unleash Antigravity to build the entire app!\""
        ),
    },
    # SLIDE 25
    {
        "num": 25,
        "module": "Module 4 • Lab Step 3: Agent Skills & /planning Mode",
        "time": "00:59 – 01:02 (3 min)",
        "type": "two_cards_code",
        "title": "✋ Checkpoint 3: Autonomous Implementation & Artifacts",
        "timer_seconds": 240,
        "left_card": {
            "color": "blue",
            "title": "What AGY Builds Automatically",
            "subtitle": "Backend (AGY SDK + FastAPI) & Frontend (Lit + Vite)",
            "code": (
                "# Typical generated structure in ~/cat-delivery:\n"
                "cat-delivery/\n"
                "├── backend/\n"
                "│   ├── agent.py      # AGY SDK + Nano Banana 2 tool\n"
                "│   └── main.py       # FastAPI + static file mount\n"
                "├── frontend/\n"
                "│   ├── src/          # Lit web components chat UI\n"
                "│   └── vite.config.js\n"
                "└── pyproject.toml"
            ),
            "bullets": [
                (
                    "Backend Harness",
                    "Wires Gemini 3.5 Flash root agent + custom Vertex AI `gemini-3.1-flash-image` tool.",
                ),
                (
                    "Frontend Build",
                    "Scaffolds Lit components, runs `npm install && npm run build`, and mounts `dist/` in FastAPI.",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Tracking Progress via /artifact",
            "subtitle": "3 Living Artifacts in ~/.gemini/antigravity-cli/brain/",
            "code": (
                "# Run /artifact after implementation completes:\n"
                "1. implementation_plan.md  (Approved Blueprint)\n"
                "2. task.md                 (Live Checklist [x])\n"
                "3. walkthrough.md          (Validation Summary)"
            ),
            "bullets": [
                (
                    "task.md",
                    "Created automatically to track every implementation and test step.",
                ),
                (
                    "walkthrough.md",
                    "Generated once coding & local verification finish, documenting what was built and tested.",
                ),
            ],
        },
        "notes": (
            "TIMING: 00:59 - 01:02 (3 mins)\n"
            "LAB CHECKPOINT #3 (Start the 4-minute timer while AGY builds the app!).\n\n"
            "SAY THIS:\n"
            "\"Once you hit `Y` to approve the plan, sit back and watch Antigravity orchestrate the entire full-stack build! It will ask for confirmation to run `uv`, `npm`, and test commands.\n"
            "Notice that the artifact counter in the bottom right increases from `1 artifact` to `3 artifacts`:\n"
            "- `implementation_plan.md` is your blueprint.\n"
            "- `task.md` is the live checklist the agent updates as it completes backend, frontend, and integration tasks.\n"
            "- And when it finishes, it generates `walkthrough.md` summarizing everything it built and verified!\""
        ),
    },
    # SLIDE 26
    {
        "num": 26,
        "module": "Module 5 • Lab Step 4: Cloud Run Deployment & Verification",
        "time": "01:02 – 01:06 (4 min)",
        "type": "stepper_split",
        "title": "Step 6: Deploy to Cloud Run in /fast Mode",
        "steps": [
            ("01", "Switch to /fast Mode", "Deployment doesn't need a new design doc"),
            ("02", "Single-Container Build", " Dockerfile bundles Lit dist/ + FastAPI backend"),
            ("03", "Audit Against Criteria", "AGY deploys to Cloud Run & verifies live URL"),
        ],
        "callout_badge": "ACCEPTANCE-DRIVEN DEPLOYMENT",
        "callout_title": "Why Include Acceptance Criteria in Your Prompt?",
        "callout_body": (
            "By giving AGY explicit Acceptance Criteria ('Frontend is live and renders with no errors', 'Backend responds with no errors'), the agent won't stop at `gcloud run deploy`—it will curl/test the live Cloud Run URL and fix any container startup issues automatically!"
        ),
        "code_title": "agy (/fast mode) — Cloud Run Deployment Prompt",
        "code": (
            "/fast\n\n"
            "Deploy the agent and frontend to Cloud Run.\n\n"
            "TODO:\n"
            "- backend should serve a static frontend\n"
            "- frontend and backend are deployed in the same container\n\n"
            "Acceptance Criteria\n"
            "- Agent is deployed to cloud run\n"
            "- Frontend is live and renders with no errors\n"
            "- Backend is live and responds to requests with no errors"
        ),
        "notes": (
            "TIMING: 01:02 - 01:06 (4 mins)\n"
            "GOAL: Switch to `/fast` mode and deploy the Cat Delivery System to Cloud Run (Codelab Step 6).\n\n"
            "SAY THIS:\n"
            "\"Now our app is built locally—let's ship it to production on Google Cloud Run! This is Codelab Step 6.\n"
            "Since deploying an already-architected app is a straightforward operational task, we don't need a separate planning cycle. Type `/fast` to switch Antigravity back to Fast Mode, and paste the deployment prompt on the right.\"\n\n"
            "\"Look at the bottom of that prompt: **Acceptance Criteria**. That is one of the most powerful pro-tips you'll learn today. Because we specify that the Frontend and Backend must be live and respond with no errors, Antigravity won't just run `gcloud run deploy` and walk away—it will actually test and audit the live Cloud Run endpoint, and if a port or Dockerfile path needs fixing, it will self-heal and redeploy automatically!\""
        ),
    },
    # SLIDE 27
    {
        "num": 27,
        "module": "Module 5 • Lab Step 4: Cloud Run Deployment & Verification",
        "time": "01:06 – 01:10 (4 min)",
        "type": "verification_cards",
        "title": "✋ Checkpoint 4: Live \"Break the Guardrail\" Challenge!",
        "timer_seconds": 180,
        "left_card": {
            "title": "01. Happy Path: Custom Cat Delivery",
            "query": '"I just survived a production outage—send me an anime cyberpunk cat hacker to cheer me up!"',
            "result_title": "✔ Grounded Multimodal Response:",
            "result_body": (
                "Root agent (Gemini 3.5 Flash) responds with an encouraging message, invokes the Nano Banana 2 (Gemini 3.1 Flash Image) tool, and renders a neon cyberpunk cat right in the Lit chat UI!"
            ),
            "goal": "Confirms single-container static UI serving, backend Antigravity SDK harness, and Vertex AI image synthesis work end-to-end on Cloud Run.",
        },
        "right_card": {
            "title": "02 & 03. Guardrail & Easter Egg Tests",
            "trap1_title": "02. The Dog Trap (\"Generate a cute golden retriever puppy\")",
            "trap1_expected": "Expected: Polite Refusal + Steer to Cats!",
            "trap1_body": (
                "\"I'm strictly a Cat Delivery System—no dogs allowed! How about an adorable golden fluffy Maine Coon kitten instead?\" (Generates cat!)"
            ),
            "trap2_title": "03. The Capybara Loophole (\"Can I get a capybara in a yuzu hot spring?\")",
            "trap2_expected": "Result: Allowed by System Prompt Exception!",
            "trap2_body": (
                "Agent honors the 'P.S.: capybaras are allowed' clause in its system instructions and generates a chill capybara image via Nano Banana 2!"
            ),
        },
        "notes": (
            "TIMING: 01:06 - 01:10 (4 mins)\n"
            "INTERACTIVE CHALLENGE #5: Open the live Cloud Run URL and take prompt suggestions from the audience!\n\n"
            "SAY THIS:\n"
            "\"Once `agy` prints your live `https://cat-delivery-...run.app` URL, click it to open your deployed Cat Delivery System!\n"
            "Let's run three verification tests together:\n"
            "1. First, ask for your favorite style of cat—cyberpunk, Studio Ghibli, pixel art, oil painting.\n"
            "2. Second, try to trick it into generating a dog! Say 'I really want a golden retriever' or 'Draw a wolf that barks'. Watch Gemini 3.5 Flash politely refuse and steer you back toward cats!\n"
            "3. Third, test the secret loophole from our prompt: ask for a capybara! Because we told `agy` 'P.S.: capybaras are allowed', the agent happily delivers a capybara!\""
        ),
    },
    # SLIDE 28
    {
        "num": 28,
        "module": "Module 6 • Playbook, Troubleshooting & Wrap-Up",
        "time": "01:10 – 01:12 (2 min)",
        "type": "four_steps",
        "title": "Your Agentic Orchestration Playbook",
        "subtitle": "4 Repeatable Patterns for Production Engineering with Antigravity",
        "intro": "We just built, tested, and deployed a full-stack cloud application without writing a single line of code manually. Here is the 4-step playbook you can take back to your team tomorrow:",
        "steps": [
            {
                "num": "1",
                "title": "Ground with MCP",
                "body": "Never let coding agents guess APIs. Connect `google-developer-knowledge` (and your internal MCP servers) for live, authoritative docs.",
                "highlight": False,
            },
            {
                "num": "2",
                "title": "Equip with Skills",
                "body": "Package SDK conventions & team workflows as `SKILL.md` files (`npx skills` / `agy plugin`) for token-efficient progressive disclosure.",
                "highlight": False,
            },
            {
                "num": "3",
                "title": "Plan & Comment First",
                "body": "Use `/planning` + `/artifact` (press `C` to comment) to lock in API contracts and verification plans before a single file is modified.",
                "highlight": False,
            },
            {
                "num": "4",
                "title": "Audit with Criteria",
                "body": "Switch to `/fast` for deployment and always include explicit Acceptance Criteria so the agent verifies and self-heals its own release.",
                "highlight": True,
            },
        ],
        "notes": (
            "TIMING: 01:10 - 01:12 (2 mins)\n"
            "GOAL: Synthesize the 4 core lessons of the workshop.\n\n"
            "SAY THIS:\n"
            "\"Pause and think about what you just accomplished in under an hour: you orchestrated a Python FastAPI + Antigravity SDK backend, a Lit + Vite web frontend, multimodal image generation with Nano Banana 2, and a serverless Cloud Run deployment—with zero manual coding.\n"
            "When you go back to work on Monday, remember this 4-step Command & Control playbook:\n"
            "1. Ground with MCP (`mcp_config.json`).\n"
            "2. Equip with Progressive Skills (`SKILL.md`).\n"
            "3. Architect first with `/planning` and `/artifact` inline comments (`C`).\n"
            "4. Ship and audit with explicit Acceptance Criteria.\""
        ),
    },
    # SLIDE 29
    {
        "num": 29,
        "module": "Module 6 • Bonus Reference & Cheat Sheet",
        "time": "Reference Slide (1/2)",
        "type": "two_cards_code",
        "title": "Quick Reference: AGY CLI Commands & Shortcuts",
        "left_card": {
            "color": "blue",
            "title": "Essential Slash Commands & Hotkeys",
            "subtitle": "Keep this cheat sheet handy during & after the lab",
            "code": (
                "/planning   # Switch to Planning Mode (creates plan artifact)\n"
                "/fast       # Switch to Fast Mode (immediate execution)\n"
                "/artifact   # Open & review implementation_plan.md / task.md\n"
                "/model      # Switch model & thinking level (Low/Med/High)\n"
                "/mcp        # Verify connected MCP servers & tools\n"
                "/skills     # List discovered workspace, plugin & global skills\n"
                "Ctrl + O    # Expand/collapse intermediate agent thinking\n"
                "Ctrl + D x2 # Exit AGY CLI cleanly back to bash"
            ),
            "bullets": [
                (
                    "Inside /artifact Viewer",
                    "Use `↑`/`↓` to scroll, `C` to add a line comment, `ESC` then `Y` to submit.",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Common Workshop Troubleshooting Fixes",
            "subtitle": "Instant Solutions for Cloud Shell & Vertex AI",
            "code": (
                "# Fix 1: TUI menu looks garbled in Cloud Shell\n"
                "-> Click 'Open Editor' and use Terminal > New Terminal (Ctrl+`)\n\n"
                "# Fix 2: google-developer-knowledge MCP fails to connect\n"
                "-> Check ~/.gemini/config/mcp_config.json: ensure [[PROJECT_ID]]\n"
                "   was replaced with your real Project ID (no brackets!)\n"
                "-> Ensure API is enabled:\n"
                "   gcloud services enable developerknowledge.googleapis.com"
            ),
            "bullets": [
                (
                    "Vertex AI Location",
                    "Ensure `global` location is selected for Gemini 3.5 Flash & Gemini 3.1 Flash Image.",
                ),
            ],
        },
        "notes": (
            "TIMING: Reference / Backup Slide (1 min or keep on screen during Q&A)\n"
            "GOAL: Provide a single cheat sheet of all slash commands, hotkeys, and troubleshooting tips.\n\n"
            "SAY THIS:\n"
            "\"I've included two bonus cheat-sheet slides in the deck for you to keep. This first one has every slash command (`/planning`, `/fast`, `/artifact`, `/model`, `/mcp`, `/skills`), hotkey (`Ctrl+O`, `Ctrl+D`, `C`), and common Cloud Shell troubleshooting fix.\""
        ),
    },
    # SLIDE 30
    {
        "num": 30,
        "module": "Module 6 • Bonus Reference & Cheat Sheet",
        "time": "Reference Slide (2/2)",
        "type": "two_cards_code",
        "title": "Going Further: Authoring Your Own Skill & Rules",
        "left_card": {
            "color": "blue",
            "title": "Create a Custom Workspace Skill",
            "subtitle": ".agents/skills/my-team-skill/SKILL.md",
            "code": (
                "---\n"
                "name: cloud-run-security-audit\n"
                "description: >-\n"
                "  Audits FastAPI and Cloud Run services for least-privilege IAM,\n"
                "  non-root Dockerfiles, and CORS safety. Activate before deploy.\n"
                "---\n\n"
                "# Cloud Run Security Audit Procedure\n"
                "1. Verify Dockerfile runs as a non-root user.\n"
                "2. Check that Vertex AI uses ADC (no hardcoded API keys).\n"
                "3. Run smoke tests against /healthz before rollout."
            ),
            "bullets": [
                (
                    "Zero Config Discovery",
                    "Place in `.agents/skills/<name>/SKILL.md` in your repo to share with your whole team via Git!",
                ),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Enforce Project Rules with GEMINI.md",
            "subtitle": "Hierarchical Context Rules (GEMINI.md / AGENTS.md)",
            "code": (
                "# Project Engineering Guidelines (GEMINI.md)\n\n"
                "- **Package Manager**: Always use `uv` (never raw `pip`).\n"
                "- **Python Style**: Type-annotate all FastAPI endpoints.\n"
                "- **Frontend**: Use Lit web components with Vite.\n"
                "- **Testing**: Run `uv run pytest` after modifying backend code."
            ),
            "bullets": [
                (
                    "Rules vs. Skills",
                    "Use `GEMINI.md` for always-on guardrails & coding conventions; use `SKILL.md` for on-demand multi-step playbooks.",
                ),
            ],
        },
        "notes": (
            "TIMING: Reference / Bonus Slide\n"
            "GOAL: Show attendees how easy it is to write their own `SKILL.md` and `GEMINI.md` in their own repositories.\n\n"
            "SAY THIS:\n"
            "\"And this second bonus slide shows how you can create your own skills and rules in 60 seconds! Just drop a `SKILL.md` file with YAML frontmatter (`name` and `description`) into `.agents/skills/` in your Git repo, or add a `GEMINI.md` file at the root of your project to enforce team-wide conventions.\""
        ),
    },
    # SLIDE 31
    {
        "num": 31,
        "module": "Module 6 • Closing",
        "time": "01:12 – 01:13 (1 min)",
        "type": "cover",
        "title": "Command and control:\nOrchestrate app development\nwith Gemini and MCP",
        "subtitle": "Built & Deployed with Google Antigravity, Developer Knowledge MCP, Agent Skills & Cloud Run",
        "badge": "Congratulations! 🎉",
        "notes": (
            "TIMING: 01:12 - 01:13 (1 min)\n"
            "GOAL: Celebrate everyone completing the workshop!\n\n"
            "SAY THIS:\n"
            "\"Give yourselves a huge round of applause! You have officially mastered Command and Control with Gemini, MCP, and Google Antigravity.\""
        ),
    },
    # SLIDE 32
    {
        "num": 32,
        "module": "Module 6 • Closing & Q&A",
        "time": "01:13 – 01:15 (2 min)",
        "type": "thank_you",
        "title": "Thank you!",
        "subtitle": "Questions, Feedback & Let's Connect!\nRabimba Karanjai • GDE AI/ML • @rabimba",
        "qr_top": "qr_codelab.png",
        "qr_top_label": "Workshop Codelab: codelabs.developers.google.com/gemini-mcp-agy",
        "qr_bottom": "qr_rabimba_github.png",
        "qr_bottom_label": "Slides & Artifacts: github.com/rabimba/GDE-ML-Artifacts",
        "notes": (
            "TIMING: 01:13 - 01:15 (2 mins + Open Q&A)\n"
            "GOAL: Share final QR codes and open the floor for Q&A.\n\n"
            "SAY THIS:\n"
            "\"Thank you all so much for building with me today! The top QR code links to the Codelab so you can replay or share it with your team, and the bottom QR code goes to my GitHub (`github.com/rabimba/GDE-ML-Artifacts`) where today's slides and runbook live. We have a few minutes left—what questions do you have?\""
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
            add_image_fit(slide, sdata["qr_top"], 8.15, 0.45, 1.45, 1.45)
            add_textbox(slide, 7.60, 1.92, 2.25, 0.45, "Workshop Codelab\ngemini-mcp-agy", font_size=8.5, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)
            add_image_fit(slide, sdata["qr_bottom"], 8.15, 3.35, 1.45, 1.45)
            add_textbox(slide, 7.60, 4.82, 2.25, 0.45, "Slides & Runbook\nGDE-ML-Artifacts", font_size=8.5, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)

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
                sy = 1.60 + idx * 1.15
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.78), Inches(sy), Inches(0.42), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(26, 115, 232)
                pill.line.fill.background()
                add_textbox(slide, 0.78, sy + 0.06, 0.42, 0.30, snum, font_size=11, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)
                add_textbox(slide, 1.32, sy - 0.04, 3.15, 0.30, stitle, font_size=12.5, bold=True, color=(32, 33, 36))
                add_textbox(slide, 1.32, sy + 0.24, 3.15, 0.45, sdesc, font_size=10, bold=False, color=(19, 115, 51), font_name="Roboto Mono")
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
            <img src="assets/bg_cover_layers.png" alt="Google Cloud Layers"/>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
          <span class="prop-badge-abs">Proprietary + Confidential</span>
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
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="speaker-fan-bg">
            <img src="assets/bg_speaker_fan.png" alt="Fan Background"/>
          </div>
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <span class="prop-badge-abs">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
            <span class="prop-badge">Proprietary + Confidential</span>
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
  <title>Command and control: Orchestrate app development with Gemini and MCP — Workshop Deck</title>
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
      <h2>All 32 Workshop Slides — Click Any Slide to Jump</h2>
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
    const channel = new BroadcastChannel('command_control_workshop_sync');

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
    const channel = new BroadcastChannel('command_control_workshop_sync');

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
        "## **Command and control: Orchestrate app development with Gemini and MCP**",
        "- **Format**: Interactive Hands-On Workshop (1 hr 15 mins / 75 minutes)",
        "- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)",
        "- **Base Codelab**: [https://codelabs.developers.google.com/gemini-mcp-agy](https://codelabs.developers.google.com/gemini-mcp-agy)",
        "",
        "---",
        "",
        "## ⚡ How to Present Directly from This Folder",
        "",
        "1. **Option A — Interactive Web Deck + Dual-Screen Presenter Console (Recommended)**:",
        "   - Run `./present.sh` in this folder (or open `index.html` in Chrome).",
        "   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!",
        "   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.",
        "   - Press **`G`** for the 32-slide grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.",
        "2. **Option B — Google Slides / PowerPoint Presenter View**:",
        "   - Upload `Command_and_Control_Gemini_MCP_Workshop.pptx` to Google Slides (File → Import slides / Open) or open in PowerPoint/Keynote.",
        "   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.",
        "3. **Option C — Tablet / Phone Companion**:",
        "   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through all 32 slides' verbatim notes and copy-paste prompts.",
        "",
        "---",
        "",
        "## ⏱️ 75-Minute Pacing Schedule & Checkpoints",
        "",
        "| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **00:00 – 00:10** | 10 min | **Module 0: Welcome & Onboarding** | Slides 1–4 | Scan Codelab QR + Start Cloud Shell |",
        "| **00:10 – 00:20** | 10 min | **Module 1: Concepts & Architecture** | Slides 5–10 | 🎤 Poll #1 (Hallucinations) + 🎯 Quiz #2 (MCP vs Skills) |",
        "| **00:20 – 00:30** | 10 min | **Module 2: Lab Step 1 — Hello AGY CLI** | Slides 11–14 | ✋ Checkpoint #1: `cat-trivia.js` ASCII Cat (3m timer) |",
        "| **00:30 – 00:45** | 15 min | **Module 3: Lab Step 2 — Developer Knowledge MCP** | Slides 15–18 | 🎤 Quiz #3 (Nano Banana 2) + ✋ Checkpoint #2: Kitten PNG (5m timer) |",
        "| **00:45 – 01:02** | 17 min | **Module 4: Lab Step 3 — Skills & `/planning` Mode** | Slides 19–25 | 🎯 Quiz #4 (`/fast` vs `/planning`) + ✋ Checkpoint #3: `/artifact` Review |",
        "| **01:02 – 01:10** | 8 min | **Module 5: Lab Step 4 — Cloud Run & Guardrails** | Slides 26–27 | ✋ Checkpoint #4: Live Cloud Run + 🎤 Break the Dog Guardrail! |",
        "| **01:10 – 01:15** | 5 min | **Module 6: Playbook, Cheat Sheet & Q&A** | Slides 28–32 | 4-Step Playbook Recap + Open Q&A |",
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
    pptx_out = os.path.join(BASE_DIR, "Command_and_Control_Gemini_MCP_Workshop.pptx")
    html_out = os.path.join(BASE_DIR, "index.html")
    notes_html_out = os.path.join(BASE_DIR, "speaker-notes.html")
    md_out = os.path.join(BASE_DIR, "SPEAKER_NOTES_AND_SCRIPT.md")

    build_pptx(pptx_out)
    build_html_deck(html_out)
    build_speaker_notes_html(notes_html_out)
    build_markdown_runbook(md_out)
