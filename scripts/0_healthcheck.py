import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    load_dotenv(root_dir / ".env")

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key:
        print("❌ Missing OPENAI_API_KEY in .env")
        return 1

    client = OpenAI(api_key=api_key)
    try:
        client.models.list()
        print("✅ OpenAI auth check passed")
        return 0
    except AuthenticationError:
        print("❌ OpenAI auth failed (401): invalid/revoked key or wrong project")
        return 1
    except Exception as error:
        print(f"❌ OpenAI health check failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())