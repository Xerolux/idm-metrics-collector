# Xerolux 2026
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Xerolux
#
# This file contains encrypted logic for IDM Heat Pump authentication.
# The code is obfuscated to protect the authentication algorithm implementation.
#
# SECURITY NOTE: This module uses encrypted code execution which is a security risk.
# Consider replacing with a proper authentication module in the future.

import logging
import ast
from cryptography.fernet import Fernet
from datetime import datetime

logger = logging.getLogger(__name__)

# Encrypted payload containing the technician code generation logic
_PAYLOAD = b"gAAAAABpdStF2zkxksKs_Z0IS2IXP9R0Vr3Wnw7qN7Eo9EENCrsCmf3nb9ENKdf8exkF5cp3T9KCC3sAVC3cDnGsHP1WlwX767UUqFnKPVAvwHfv3tZ5wPSitt5Oa-w-UP0rk4y3vL4U0i_7_1UyRCYncJ9mPbTPC2i3o6zOWI2zE39HR9G6XFVU3l-DZaM3OtOghSRofhWhqvt8j4iNbK6z56WRgSsZrYNAwrbfmNG_l-TleH6RaCtPXoN5JgI9jokMP_EM7R-eptYBBVXCJIY4HR2pqruuRBz9eSXy2ERWWNaR98_xsnOt9_mzhVvh1K9FJQmrPVz6fusorsABNoyE53MTR9Ik_QxdMdWWpEA0yWzNsP-MZp6BBPvZkJAno4IBb_TbrgcwYMf7fYdmWkicRksLr2US_NRgiNL66SzQO1DExPJZNNivLN4VrzwO4aNwEd614oU6IQVCySh_WBQBQSqPjIUU34-H9ecPbgkJb5ElWXQl2Pj-PVjVKcGmOAxqBIWWj5duY9QgLG4JvrUAErRGGJd_01o1owiCngwofBddv4LIfqpUs3HCf8N5Of-HXnrRThQnvRQckYZw1ZZQd01kj_HOtfGfejTDnsEE68mx-bduwDXEwbkZK4-B6n13khlfa3-u5tLeGHqig4DdUcOgGtKfxDnWsht5njMB2sh0bCTqHL9ljAo_3yceJS2UfU4kGkl40CwK02xvJ-rxhPUPjLWb_I3aF_UdL06LaY3B7xvelK_oTHv3PeCWsTt8nTGWKfcGodxlWLMiuwYtIuLlMTpGYnjWL3C5HnLeHgudI1BRoaIvwXx0sxA9xbaB0jnbvJPl"

# Restricted namespace for code execution (security hardening)
_ALLOWED_BUILTINS = {
    "int": int,
    "str": str,
    "len": len,
    "range": range,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "divmod": divmod,
    "round": round,
    "format": format,
    "chr": chr,
    "ord": ord,
    "hex": hex,
    "bin": bin,
    "True": True,
    "False": False,
    "None": None,
    "datetime": datetime,
}


def _get_key():
    # Key reconstruction for in-memory decryption
    # Part 1: iYYeyAs
    k1 = "iYYeyAs"
    # Part 2: 9MbBuLxzH
    k2 = "9MbBuLxzH"
    # Part 3: Anacdiqd2h9f
    k3 = "Anacdiqd2h9f"
    # Part 4: N4UaeAYKPHxYZ0E=
    k4 = "N4UaeAYKPHxYZ0E="
    return (k1 + k2 + k3 + k4).encode()


def _validate_code(code_str: str) -> bool:
    """
    Validate decrypted code using AST parsing.
    Rejects code with dangerous constructs like imports, exec, eval, etc.
    """
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            # Block imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                logger.error("Security: Import statements not allowed")
                return False
            # Block dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in (
                        "exec",
                        "eval",
                        "compile",
                        "__import__",
                        "open",
                    ):
                        logger.error(f"Security: {node.func.id}() not allowed")
                        return False
        return True
    except SyntaxError as e:
        logger.error(f"Security: Code validation failed: {e}")
        return False


# Module-level namespace for executed code
_module_namespace = {"__builtins__": _ALLOWED_BUILTINS}

try:
    _cipher_suite = Fernet(_get_key())
    _decrypted_code = _cipher_suite.decrypt(_PAYLOAD).decode("utf-8")

    # Security: Validate code before execution
    if _validate_code(_decrypted_code):
        # Compile first to catch syntax errors
        _compiled_code = compile(_decrypted_code, "<technician_auth>", "exec")
        # Execute with restricted namespace
        exec(_compiled_code, _module_namespace)
        # Export any defined functions to module level
        for name, obj in _module_namespace.items():
            if callable(obj) and not name.startswith("_"):
                globals()[name] = obj
    else:
        logger.error("Authentication code validation failed")
except Exception as e:
    # Log error type but not details to prevent analysis
    logger.error(f"Authentication logic error: {type(e).__name__}")


def calculate_codes():
    """Fallback if decryption fails - returns empty codes."""
    if "calculate_codes" in _module_namespace:
        return _module_namespace["calculate_codes"]()
    return {"code1": "ERROR", "code2": "ERROR", "code3": "ERROR"}
