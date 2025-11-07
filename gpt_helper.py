# gpt_helper.py (replace the previous implementation)
import os
from openai import OpenAI

MODEL_DEFAULT = "gpt-4-turbo"

SYSTEM_PROMPT = """You are a helpful data analyst that only outputs Python pandas code (no imports) to answer user queries on a provided dataset. Return only valid Python code that uses the provided DataFrame "df" variable. Use pandas operations (groupby, merge, pivot_table, sort_values, etc.). Do not include any explanatory text. If plotting is requested, create a DataFrame or Series named 'result' that the caller can render. Avoid file operations, network calls, or dangerous functions. Never use 'import', 'open', 'exec', 'eval', 'os', 'subprocess', or '__'."""

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")
    return _client

def _build_prompt(query, metadata):
    columns = metadata.get('columns', {})
    n_rows = metadata.get('n_rows', None)
    cols_str = '\n'.join([f"- {c}: {t}" for c,t in columns.items()])
    prompt = f"""{SYSTEM_PROMPT}

Dataset schema (columns and types):
{cols_str}

Number of rows: {n_rows}

User question: {query}

IMPORTANT: Put the final answer object into a variable named 'result'. If you want to show a DataFrame, assign it to 'result'. If you want to show a plot, assign the DataFrame to 'result' and the app will plot it. Only output Python code.
"""
    return prompt

def generate_code_for_query(query, metadata, model=None, temperature=0.0, max_tokens=800):
    client = _get_client()
    model = model or MODEL_DEFAULT
    prompt = _build_prompt(query, metadata)

    # New client usage
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Extract text from the response
    # (response structure: resp.choices[0].message.content)
    text = resp.choices[0].message.get("content") if resp.choices and resp.choices[0].message else None
    if not text:
        # fallback for some versions
        text = resp.choices[0].message.content if hasattr(resp.choices[0].message, "content") else str(resp)

    # strip markdown fences if any
    if text and text.strip().startswith("```"):
        parts = text.split("```")
        text = parts[-1].strip()
    return text
