import os

# Ensure the app and AIAnalyzer construct fully offline. `app.config.Settings`
# requires ANTHROPIC_API_KEY, and AIAnalyzer() builds anthropic.Anthropic(api_key=...);
# neither makes a network call at construction time, so a dummy key is sufficient and
# keeps the entire test suite from ever needing a real key or network access.
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
