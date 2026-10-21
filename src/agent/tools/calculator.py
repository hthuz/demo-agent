"""Calculator tool for mathematical operations."""

import ast
import operator
from typing import Any

from agent.tools.base import Tool


class Calculator(Tool):
    """Tool for performing safe mathematical calculations."""

    # Allowed operators for safe evaluation
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self):
        super().__init__()
        self.name = "Calculator"
        self.description = (
            "Performs mathematical calculations. Supports basic arithmetic "
            "operations: +, -, *, /, **, %, //. Use this tool for any math problem."
        )
        self.parameters = {
            "math_expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')",
                "required": True,
            }
        }

    def execute(self, math_expression: str = "", **kwargs) -> str:
        """Execute a mathematical calculation.

        Args:
            math_expression: Mathematical expression to evaluate

        Returns:
            Result of the calculation as a string
        """
        if not math_expression:
            return "Error: No math expression provided"

        try:
            result = self._safe_eval(math_expression)
            return str(result)
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Error: Invalid mathematical expression - {str(e)}"

    def _safe_eval(self, expr: str) -> float:
        """Safely evaluate a mathematical expression.

        Uses AST parsing to avoid eval() security issues.

        Args:
            expr: Mathematical expression string

        Returns:
            Result of the evaluation

        Raises:
            ValueError: If expression contains unsupported operations
        """
        try:
            node = ast.parse(expr, mode='eval')
            return self._eval_node(node.body)
        except SyntaxError:
            raise ValueError("Invalid syntax in mathematical expression")

    def _eval_node(self, node: Any) -> float:
        """Recursively evaluate AST node.

        Args:
            node: AST node to evaluate

        Returns:
            Evaluated result

        Raises:
            ValueError: If node type is not supported
        """
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} not allowed")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.ALLOWED_OPERATORS[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type.__name__} not allowed")
            operand = self._eval_node(node.operand)
            return self.ALLOWED_OPERATORS[op_type](operand)
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
