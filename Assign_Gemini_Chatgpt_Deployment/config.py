import os


# 🔒 Production Grade Setup: Fetch token securely from environment space
# Set this in your environment terminal: export GEMINI_API_KEY="your_actual_key"
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY", "jffjykjjfj")
