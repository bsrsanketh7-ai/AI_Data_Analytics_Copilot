import ast, builtins, traceback, io, sys, textwrap
import pandas as pd
import numpy as np

SAFE_NAMES = {
    'pd': pd,
    'np': np,
}

DISALLOWED_WORDS = ['import', 'open', 'exec', 'eval', 'subprocess', 'socket', 'os', '__', 'system', 'shutil']

def _contains_disallowed(code_text):
    lower = code_text.lower()
    return any(w in lower for w in DISALLOWED_WORDS)

def safe_execute(code_text, df):
    """Attempt to safely execute the generated pandas code.

    - Rejects code containing disallowed words.
    - Parses AST and allows only simple statements (Assign, Expr, For, If, With, Return not allowed at top-level).
    - Executes code with limited globals where 'df' is the DataFrame.
    - Returns (result, logs)
    """
    logs = ''
    if _contains_disallowed(code_text):
        raise RuntimeError('Code contains disallowed expressions (import/file/network operations).')

    try:
        node = ast.parse(code_text, mode='exec')
    except Exception as e:
        raise RuntimeError(f'AST parse error: {e}')

    # basic AST whitelist
    allowed_nodes = (
        ast.Module, ast.Expr, ast.Assign, ast.AugAssign, ast.BinOp, ast.UnaryOp,
        ast.Call, ast.Name, ast.Load, ast.Store, ast.Attribute, ast.Subscript,
        ast.Index, ast.Slice, ast.If, ast.Compare, ast.For, ast.ListComp, ast.Dict,
        ast.Tuple, ast.List, ast.Return, ast.Lambda, ast.FunctionDef, ast.IfExp,
        ast.DictComp, ast.SetComp, ast.comprehension
    )

    for n in ast.walk(node):
        if not isinstance(n, allowed_nodes):
            # allow literal nodes
            if isinstance(n, (ast.Constant, ast.Num, ast.Str)):
                continue
            # raise on truly unsafe nodes
            raise RuntimeError(f'Unsafe or unsupported AST node detected: {n.__class__.__name__}')

    # prepare execution environment
    safe_globals = {k: SAFE_NAMES[k] for k in SAFE_NAMES}
    safe_globals['df'] = df
    safe_locals = {}

    # capture stdout/err
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        exec(compile(node, filename='<generated>', mode='exec'), safe_globals, safe_locals)
        # prefer 'result' var in locals or globals
        result = None
        if 'result' in safe_locals:
            result = safe_locals.get('result')
        elif 'result' in safe_globals:
            result = safe_globals.get('result')
        else:
            # try to find last DataFrame-like variable
            for v in list(safe_locals.values())[::-1]:
                if isinstance(v, (pd.DataFrame, pd.Series, np.ndarray, list, dict)):
                    result = v
                    break
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
        logs = (stdout + "\n" + stderr).strip()
        return result, logs
    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(f'Error during execution: {e}\n{tb}')
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
