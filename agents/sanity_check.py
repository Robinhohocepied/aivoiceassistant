from app.config import load_settings
from agents.client import create_agents_client


def main() -> int:
    s = load_settings()
    client = create_agents_client(s)
    if client is None:
        print("OpenAI client not configured. Set OPENAI_API_KEY in .env.")
        return 1

    prompt = "Réponds uniquement: 'pong'."
    try:
        resp = client.responses.create(model=s.agent_model, input=prompt)
        # `output_text` is a convenience for simple text responses
        text = getattr(resp, "output_text", None) or str(resp)
        print(text)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"OpenAI request failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

