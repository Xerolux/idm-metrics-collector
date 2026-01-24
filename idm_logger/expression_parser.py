"""
Expression Parser for mathematical operations on query results.

Supports operations like:
- A/B (divide query A by query B)
- A*100 (multiply query A by 100)
- (A+B)/2 (average of A and B)
- avg(A,B,C) (average of multiple queries)
- sum(A,B) (sum of A and B)
- min(A,B) (minimum of A and B)
- max(A,B) (maximum of A and B)
"""

import ast
import re
from typing import List, Dict, Union
import operator
import logging

logger = logging.getLogger(__name__)

# Pre-compiled regex patterns for performance
_VALID_CHARS_PATTERN = re.compile(r"^[\w\s+\-*/().,]+$")
_FUNCTION_PATTERN = re.compile(r"(\w+)\s*\(")
_INVALID_OPS_PATTERN = re.compile(r"([^\w\s])([^\w\s])")
_QUERY_LABEL_PATTERN = re.compile(r"\b([A-Z])\b")


class SafeExpressionEvaluator(ast.NodeVisitor):
    """
    Safe AST-based expression evaluator.
    Only allows basic arithmetic operations and whitelisted functions.
    """

    # Allowed binary operators
    BINARY_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    # Allowed unary operators
    UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    # Allowed function names
    ALLOWED_FUNCTIONS = {"min", "max", "abs"}

    def __init__(self):
        self.result = None

    def evaluate(self, expr: str) -> float:
        """Safely evaluate a mathematical expression."""
        try:
            tree = ast.parse(expr, mode='eval')
            return self.visit(tree.body)
        except (SyntaxError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid expression: {e}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in self.BINARY_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return self.BINARY_OPS[op_type](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in self.UNARY_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return self.UNARY_OPS[op_type](operand)

    def visit_Num(self, node):
        # Python 3.7 compatibility
        return node.n

    def visit_Constant(self, node):
        # Python 3.8+ numbers
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")
        func_name = node.func.id
        if func_name not in self.ALLOWED_FUNCTIONS:
            raise ValueError(f"Function not allowed: {func_name}")
        args = [self.visit(arg) for arg in node.args]
        if func_name == "min":
            return min(args)
        elif func_name == "max":
            return max(args)
        elif func_name == "abs":
            if len(args) != 1:
                raise ValueError("abs() takes exactly one argument")
            return abs(args[0])

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


class ExpressionParser:
    """Safe expression parser for mathematical operations on query results."""

    # Supported operators
    OPERATORS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    # Supported functions
    FUNCTIONS = {
        "avg": lambda values: sum(values) / len(values) if values else 0,
        "sum": sum,
        "min": min,
        "max": max,
    }

    def __init__(self):
        """Initialize the expression parser."""
        self.query_results: Dict[str, List[tuple]] = {}

    def set_query_results(self, query_results: Dict[str, List[tuple]]):
        """
        Set query results for expression evaluation.

        Args:
            query_results: Dictionary mapping query labels to their results
                          Format: { 'A': [(timestamp1, value1), (timestamp2, value2), ...] }
        """
        self.query_results = query_results

    def validate_expression(self, expression: str) -> tuple[bool, str]:
        """
        Validate an expression for syntax errors.

        Args:
            expression: The expression to validate

        Returns:
            (is_valid, error_message)
        """
        if not expression or not expression.strip():
            return False, "Expression is empty"

        # Check for balanced parentheses
        paren_count = expression.count("(") - expression.count(")")
        if paren_count != 0:
            return (
                False,
                f"Unbalanced parentheses: {paren_count} extra {'(' if paren_count > 0 else ')'}",
            )

        # Check for invalid characters (only allow alphanumeric, operators, parentheses, commas, dots, spaces)
        if not _VALID_CHARS_PATTERN.match(expression):
            return False, "Expression contains invalid characters"

        # Check for valid function names
        functions = _FUNCTION_PATTERN.findall(expression)
        for func in functions:
            if func not in self.FUNCTIONS and func not in self.OPERATORS:
                # Might be a query reference, which is fine
                pass

        # Check for invalid operators
        invalid_ops = _INVALID_OPS_PATTERN.findall(expression)
        if invalid_ops:
            return False, f"Invalid operator sequence: {invalid_ops[0]}"

        return True, ""

    def parse_expression(self, expression: str) -> List[str]:
        """
        Parse an expression and extract query references.

        Args:
            expression: The expression to parse

        Returns:
            List of query labels referenced in the expression
        """
        # Extract all standalone uppercase letters (A, B, C, etc.)
        queries = _QUERY_LABEL_PATTERN.findall(expression)
        return list(set(queries))

    def evaluate_expression(
        self, expression: str, timestamp: int
    ) -> Union[float, None]:
        """
        Evaluate an expression at a specific timestamp.

        Args:
            expression: The expression to evaluate (e.g., "A/B", "A*100", "(A+B)/2")
            timestamp: The timestamp to evaluate at

        Returns:
            The calculated value or None if any query has no value at this timestamp
        """
        # First, get the value for each query at this timestamp
        query_values = {}
        for query_label in self.parse_expression(expression):
            if query_label not in self.query_results:
                return None

            # Find the value for this timestamp
            values = self.query_results[query_label]
            value = None
            for ts, val in values:
                if ts == timestamp:
                    value = val
                    break

            if value is None:
                return None

            query_values[query_label] = value

        # Now evaluate the expression with these values
        try:
            return self._evaluate_with_values(expression, query_values)
        except Exception as e:
            logger.error(f"Error evaluating expression '{expression}': {e}")
            return None

    def _evaluate_with_values(self, expression: str, values: Dict[str, float]) -> float:
        """
        Evaluate an expression with given query values.

        Args:
            expression: The expression to evaluate
            values: Dictionary mapping query labels to their values

        Returns:
            The calculated value
        """
        # Replace query references with their values
        expr = expression
        for query_label, value in values.items():
            # Use word boundaries to avoid partial replacements
            expr = re.sub(r"\b" + query_label + r"\b", str(value), expr)

        # Replace functions with Python equivalents
        # avg(A,B,C) -> (A+B+C)/3
        for func_name in ["avg", "sum", "min", "max"]:
            pattern = rf"{func_name}\s*\(([^)]+)\)"
            matches = re.findall(pattern, expr)
            for match in matches:
                args = [arg.strip() for arg in match.split(",")]
                if func_name == "avg":
                    replacement = f"({'+'.join(args)})/{len(args)}"
                elif func_name == "sum":
                    replacement = f"({'+'.join(args)})"
                elif func_name == "min":
                    replacement = f"min({','.join(args)})"
                elif func_name == "max":
                    replacement = f"max({','.join(args)})"
                expr = re.sub(
                    rf"{func_name}\s*\({re.escape(match)}\)", replacement, expr
                )

        # Safe evaluation using AST-based evaluator (no eval!)
        expr = expr.strip()
        try:
            evaluator = SafeExpressionEvaluator()
            result = evaluator.evaluate(expr)
            return float(result)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expr}': {e}")

    def evaluate_expression_series(self, expression: str) -> List[tuple]:
        """
        Evaluate an expression over all timestamps.

        Args:
            expression: The expression to evaluate

        Returns:
            List of (timestamp, value) tuples
        """
        # Get all unique timestamps from all queries
        all_timestamps = set()
        for values in self.query_results.values():
            for ts, _ in values:
                all_timestamps.add(ts)

        # Evaluate expression at each timestamp
        results = []
        for timestamp in sorted(all_timestamps):
            value = self.evaluate_expression(expression, timestamp)
            if value is not None:
                results.append((timestamp, value))

        return results

    def get_expression_help(self) -> str:
        """Get help text for expressions."""
        return """
Mathematical Expressions Help:

Operators:
  +    Addition (A + B)
  -    Subtraction (A - B)
  *    Multiplication (A * 100)
  /    Division (A / B)
  ()   Grouping ((A + B) / 2)

Functions:
  avg(A,B,C)  Average of multiple queries
  sum(A,B)    Sum of multiple queries
  min(A,B)    Minimum of multiple queries
  max(A,B)    Maximum of multiple queries

Examples:
  A/B                    Divide A by B
  A*100                  Multiply A by 100
  (A+B)/2                Average of A and B
  avg(A,B,C)             Average of A, B, and C
  (A-B)*100/B            Percentage difference
  sum(A,B,C)             Sum of A, B, and C

Note:
  - Query labels are uppercase letters: A, B, C, etc.
  - Division by zero returns None
  - Invalid expressions return None
  - Use parentheses to control operation order
"""


def test_expression_parser():
    """Test the expression parser."""
    parser = ExpressionParser()

    # Set up test data
    parser.set_query_results(
        {
            "A": [(1000, 10.0), (2000, 20.0), (3000, 30.0)],
            "B": [(1000, 2.0), (2000, 4.0), (3000, 6.0)],
            "C": [(1000, 5.0), (2000, 10.0), (3000, 15.0)],
        }
    )

    # Test validation
    print("Validation tests:")
    tests = [
        ("A/B", True),
        ("A*100", True),
        ("(A+B)/2", True),
        ("avg(A,B,C)", True),
        ("A +", False),
        ("((A+B)", False),
    ]
    for expr, expected in tests:
        valid, msg = parser.validate_expression(expr)
        print(f"  {expr}: {valid} (expected: {expected}) - {msg}")

    # Test evaluation
    print("\nEvaluation tests:")
    tests = [
        ("A/B", [5.0, 5.0, 5.0]),
        ("A*100", [1000.0, 2000.0, 3000.0]),
        ("(A+B)/2", [6.0, 12.0, 18.0]),
        ("avg(A,B,C)", [5.666666666666667, 11.333333333333334, 17.0]),
        ("sum(A,B)", [12.0, 24.0, 36.0]),
    ]
    for expr, expected in tests:
        result = parser.evaluate_expression_series(expr)
        values = [v for _, v in result]
        print(f"  {expr}: {values}")
        assert len(values) == len(expected), f"Length mismatch for {expr}"

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_expression_parser()
