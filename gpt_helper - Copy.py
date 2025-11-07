import os
import openai
import json

MODEL_DEFAULT = "gpt-4-turbo"

openai.api_key = os.getenv('OPENAI_API_KEY') or ''

SYSTEM_PROMPT = """You are a helpful data analyst that only outputs Python pandas code (no imports) to answer user queries on a provided dataset. Return only valid Python code that uses the provided DataFrame "df" variable. Use pandas operations (groupby, merge, pivot_table, sort_values, etc.). Do not include any explanatory text. If plotting is requested, create a DataFrame or Series named 'result' that the caller can render. Avoid file operations, network calls, or dangerous functions. Never use 'import', 'open', 'exec', 'eval', 'os', 'subprocess', or '__'."""

def _build_prompt(query, metadata):
    # metadata: dict with keys 'columns' and 'n_rows'
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
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY not set. Add it as an environment variable.')
    model = model or MODEL_DEFAULT
    prompt = _build_prompt(query, metadata)
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"system","content":prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    text = resp['choices'][0]['message']['content']
    # strip markdown fences if any
    if text.strip().startswith('```'):
        # remove first code fence block
        parts = text.split('```')
        # take the last block likely containing code
        text = parts[-1].strip()
    return text
