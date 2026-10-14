# AGENTS.md

GDE "train the trainer" workshop material for Gemini/Gemma. No build, tests, lint, or CI.
Repo is mostly standalone Colab notebooks + one small Google ADK app + two self-contained
workshop deck suites + static HTML landing pages.

## Layout
- Root `*.ipynb`, `function-calling/`, `quickstarts/`: independent Colab notebooks, authored
  in Colab ("Save to GitHub" commits). First cell is an "Open in Colab" badge pointing at
  `rabimba/GDE-ML-Artifacts/blob/main/<path>` — update it if you rename/move a notebook.
- `ADK/`: multi-agent trip-planner demo (google-adk). `agents.py` defines agents/workflows,
  `core.py` has the runner + shared `InMemorySessionService`; `cli.py` and
  `streamlit_app.py` DUPLICATE the routing logic — change both.
- `Location-Intelligence-ADK-MCP-Workshop/` and `Command-and-Control-Gemini-MCP-Workshop/`:
  generated deck suites. Never edit `index.html`, `speaker-notes.html`, `*.pptx`, or
  `SPEAKER_NOTES_AND_SCRIPT.md` by hand — edit `SLIDES_DATA` in that folder's
  `generate_slides.py` and re-run it (`pip install python-pptx pillow`; QR assets need
  `qrcode`). Each deck's pptx uses the sibling deck's pptx as its Google Cloud Labs
  layout template (`REF_PPTX`), so don't delete either pptx.
- Root `index.html` + `.nojekyll`: GitHub Pages landing (Pages serves `main` root, legacy
  build). When you add/rename a notebook or folder, update its card in root `index.html`.

## Notebooks
- Colab-only: secrets via `google.colab.userdata.get('GOOGLE_API_KEY')` (Gemma_1 uses
  `KAGGLE_USERNAME`/`KAGGLE_KEY`); Vertex notebooks use `auth.authenticate_user()` +
  `PROJECT_ID`. No local env exists for notebooks.
- Filenames like `[Gemma_1]Common_use_cases.ipynb` contain zsh glob chars — quote paths.
- Edit the `.ipynb` JSON directly (nbformat 4); keep Colab `metadata` and cell `id`s;
  validate with `python3 -m json.tool "<file>" >/dev/null`.
- **Modernize on touch**: when editing a notebook, migrate in the same change —
  `google-generativeai` / `vertexai.generative_models` → `google-genai`; retired model IDs
  (`gemini-pro`, `gemini-1.0-*`, `gemini-1.5-*`) → current Gemini IDs; update the
  pip-install cell and the `index.html` card if it names a model.
- Cell outputs are kept on purpose (showcase). Before committing, scan for secrets:
  `rg -n 'AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{20,}' -g '*.ipynb'`
  Gemini file-upload errors print the request URL including `?key=` — clear those outputs.
  (A key leaked this way in `Ask_Arxiv.ipynb` history: rotate keys, don't just delete cells.)

## ADK app
- Install: `pip install -r ADK/requirements.txt`. Run from INSIDE `ADK/` (bare imports):
  `python cli.py --api-key "$GOOGLE_API_KEY" --query "..." --verbose` or
  `streamlit run streamlit_app.py`.
- No tests/mocks; every query makes live Gemini calls. Keyless smoke check:
  `python -c "import agents"` from `ADK/`.
- Agents hardcode `model="gemini-1.5-flash"` — modernize-on-touch applies here too.
- ADK reads the key from `os.environ['GOOGLE_API_KEY']` (set by `configure_api_key`);
  the `genai.configure` call is legacy leftover.
- `run_agent_query` swallows exceptions into `"An error occurred: ..."` — API/model failures
  surface as "Router chose an unknown route". Check that string first when debugging.
- Routing contract: the router must return a key of `worker_agents`. To add a workflow:
  define it in `agents.py` → add to `worker_agents` → list it in the router instruction.
  The `find_and_navigate_combo` branch in both frontends is dead code (only the unused
  `router_agent` emits that route).

## Hygiene
- `.DS_Store` is tracked and there is no `.gitignore` — stage explicit paths, never
  `git add -A`.
- Never commit without scanning notebook outputs for keys (see above).
