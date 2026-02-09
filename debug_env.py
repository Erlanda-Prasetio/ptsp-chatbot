import os
import pathlib
from dotenv import load_dotenv, dotenv_values

env_path = pathlib.Path(".env")
print(f"Path: {env_path.absolute()}")
print(f"Exists: {env_path.exists()}")

try:
    content = env_path.read_text(encoding='utf-8')
    print(f"Start of content: {content[:10]!r}")
except Exception as e:
    print(f"Read error: {e}")

print("\nAttempting load_dotenv:")
loaded = load_dotenv(dotenv_path=env_path, override=True)
print(f"Loaded: {loaded}")

print(f"GROQ_API_KEY in os.environ: {'GROQ_API_KEY' in os.environ}")
print(f"OPENROUTER_API_KEY in os.environ: {'OPENROUTER_API_KEY' in os.environ}")

print("\nAttempting dotenv_values:")
values = dotenv_values(env_path)
print(f"Keys in .env: {list(values.keys())}")
