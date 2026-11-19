"""API keys and the SEC contact string: environment variables first, then ~/.config/research-keys.env (the authors'
setup). A replicator sets DEEPSEEK_API_KEY (or any OpenAI-compatible key; see code_events.py) and SEC_USER_AGENT."""

import os


def get(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name].strip().strip('"')
    path = os.path.expanduser("~/.config/research-keys.env")
    if os.path.exists(path):
        for line in open(path):
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"set the environment variable {name}")
