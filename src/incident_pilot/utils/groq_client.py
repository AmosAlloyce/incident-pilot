"""
Thin wrapper around the Groq Python SDK.
Reads GROQ_API_KEY from the environment (loaded from .env if present).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def chat(
    system_prompt: str,
    user_message: str,
    model: str = "llama-3.1-8b-instant",
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Send a single chat completion request to Groq and return the response text.

    Parameters
    ----------
    system_prompt : str
        Sets the agent's role and behavioural constraints.
    user_message : str
        The input the agent should reason about.
    model : str
        Groq model ID. Defaults to llama3-8b-8192 (free tier).
    temperature : float
        Lower = more deterministic. 0.2 is appropriate for structured TSE analysis.
    max_tokens : int
        Max tokens in the completion.

    Returns
    -------
    str
        The assistant's response text.

    Raises
    ------
    EnvironmentError
        If GROQ_API_KEY is not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Copy .env.example to .env and add your key from https://console.groq.com/keys"
        )

    # Import here so tests can mock this module without importing groq at collection time
    from groq import Groq  # noqa: PLC0415

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()
