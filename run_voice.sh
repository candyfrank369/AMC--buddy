#!/bin/bash
# Start the AMC-buddy voice adapter (XiaoZhi WS protocol -> tutor core -> OpenAI STT/TTS).
# StackChan connects to ws://<this-mac-ip>:8000/xiaozhi/v1/
set -a; . "$HOME/.amcbuddy.env"; set +a
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
cd "$(dirname "$0")"
echo "Mac IP for the device's XiaoZhiUrl:"
ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "  (check manually)"
PORT="${PORT:-8000}" ./.venv/bin/python -m tutor_agent.voice_adapter_xiaozhi
