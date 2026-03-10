import sys
from io import StringIO
import contextlib

# 1. Define the Vocabulary Map (Punjabi -> Python)
VOCABULARY = {
    # Keywords
    'je': 'if',
    'nahi_ta': 'else',
    'jad_tak': 'while',
    'waaste': 'for',
    'wich': 'in',
    'roko': 'break',
    'challo': 'continue',
    'wapas': 'return',
    'jamat': 'class',
    'kamm': 'def',   # function definition
    'koshish': 'try',
    'fadd_lo': 'except',
    
    # Built-in Functions & Booleans
    'likho': 'print',
    'dasso': 'input',
    'ginti': 'len',
    'sahi': 'True',
    'galat': 'False',
    'kuch_ni': 'None',
}

def translate_code(punjabi_code):
    """
    Translates Punjabi keywords to Python keywords line by line.
    Note: This is a simple string replacement. For a production-level 
    language, you would use a Tokenizer/Parser.
    """
    python_code = punjabi_code
    
    # We sort keys by length (descending) to avoid partial replacements
    # e.g., replacing 'if' inside 'iff'
    sorted_keys = sorted(VOCABULARY.keys(), key=len, reverse=True)
    
    for word in sorted_keys:
        # We add spaces to ensure we replace whole words (basic regex is better here, 
        # but this is simple and functional for a prototype)
        # Using simple replacement for demonstration:
        python_code = python_code.replace(f'{word} ', f'{VOCABULARY[word]} ')
        python_code = python_code.replace(f'{word}(', f'{VOCABULARY[word]}(')
        python_code = python_code.replace(f'{word}:', f'{VOCABULARY[word]}:')
        
    return python_code

@contextlib.contextmanager
def stdoutIO(stdout=None):
    """Capture the output of the executed code to show in our IDE"""
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def execute_punjabi(code_text):
    """Translates and runs the code, returning the output or error."""
    transpiled_code = translate_code(code_text)
    
    try:
        with stdoutIO() as s:
            # Create a safe global dictionary 
            exec(transpiled_code, {})
        return s.getvalue()
    except Exception as e:
        return f"Galti (Error): {e}"