#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT="${1:-8086}"
URL="http://localhost:${PORT}/index.html"
NOTES_URL="http://localhost:${PORT}/speaker-notes.html"

echo "=================================================================="
echo " 📍 Location Intelligence ADK Agent — MCP for BigQuery & Maps"
echo "=================================================================="
echo " Main Slide Deck     : ${URL}"
echo " Speaker Notes View  : ${NOTES_URL}"
echo " PowerPoint (.pptx)  : ${DIR}/Location_Intelligence_ADK_MCP_Workshop.pptx"
echo " Markdown Script     : ${DIR}/SPEAKER_NOTES_AND_SCRIPT.md"
echo "------------------------------------------------------------------"
echo " Hotkeys inside Slide Deck:"
echo "   [← / → / Space]  Navigate slides (→ also steps diagram builds)"
echo "   [P]              Pop out Dual-Screen Synchronized Speaker Notes"
echo "   [S]              Toggle On-Screen Speaker Notes Teleprompter"
echo "   [B]              Toggle Bottom Control Bar (hidden by default & in fullscreen)"
echo "   [G]              Open All-Slides Overview Grid"
echo "   [F]              Toggle Fullscreen"
echo "=================================================================="

if command -v xdg-open >/dev/null 2>&1; then
  (sleep 1 && xdg-open "$URL" >/dev/null 2>&1) &
elif command -v open >/dev/null 2>&1; then
  (sleep 1 && open "$URL" >/dev/null 2>&1) &
fi

python3 -m http.server "$PORT"
