#!/usr/bin/env python3
"""Calculadora no gráfica avanzada (modo CLI).

Características:
- Evaluación de expresiones matemáticas con seguridad usando AST.
- Variables y asignaciones (ej: a = 5; b = sin(pi/2)).
- Funciones científicas (trigonometría, logaritmos, potencias).
- Operaciones con listas/matrices (det, transpose, matmul).
- Estadística básica (mean, median, stdev).
- Historial y comandos de ayuda.
"""

import ast
import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


Number = float
Matrix = List[List[Number]]


@dataclass
class CalcState:
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)


def is_matrix(value: Any) -> bool:
    return (
        isinstance(value, list)
        and value
        and all(isinstance(row, list) for row in value)
        and all(all(isinstance(cell, (int, float)) for cell in row) for row in value)
    )


def transpose(matrix: Matrix) -> Matrix:
    if not matrix or not matrix[0]:
        raise ValueError("La matriz no puede estar vacía")
    return [list(row) for row in zip(*matrix)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b:
        raise ValueError("Las matrices no pueden estar vacías")
    if len(a[0]) != len(b):
        raise ValueError("Dimensiones incompatibles para multiplicación")
    result = []
    b_t = transpose(b)
    for row in a:
        result_row = [sum(x * y for x, y in zip(row, col)) for col in b_t]
        result.append(result_row)
    return result


def determinant(matrix: Matrix) -> Number:
    if not matrix or not matrix[0]:
        raise ValueError("La matriz no puede estar vacía")
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("La matriz debe ser cuadrada para calcular el determinante")
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0.0
    for col in range(n):
        minor = [row[:col] + row[col + 1 :] for row in matrix[1:]]
        det += ((-1) ** col) * matrix[0][col] * determinant(minor)
    return det


def to_number(value: Any) -> Number:
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError("Se esperaba un número")


def variance(values: List[Number]) -> Number:
    if len(values) < 2:
        raise ValueError("Se requieren al menos dos valores para la varianza")
    mean_val = statistics.mean(values)
    return statistics.mean([(x - mean_val) ** 2 for x in values])


def stddev(values: List[Number]) -> Number:
    return math.sqrt(variance(values))


def ensure_list(values: Any) -> List[Number]:
    if not isinstance(values, (list, tuple)):
        raise ValueError("Se esperaba una lista o tupla de números")
    numbers = [to_number(v) for v in values]
    return numbers


ALLOWED_FUNCTIONS: Dict[str, Any] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "pow": pow,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "deg": math.degrees,
    "rad": math.radians,
    "mean": lambda values: statistics.mean(ensure_list(values)),
    "median": lambda values: statistics.median(ensure_list(values)),
    "variance": lambda values: variance(ensure_list(values)),
    "stdev": lambda values: stddev(ensure_list(values)),
    "det": lambda matrix: determinant(matrix),
    "transpose": lambda matrix: transpose(matrix),
    "matmul": lambda a, b: matmul(a, b),
}

ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, state: CalcState):
        self.state = state

    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        return super().visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Operación no soportada")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Operación unaria no soportada")

    def visit_Num(self, node: ast.Num) -> Any:  # pragma: no cover (compat)
        return node.n

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node.value, str):
            return node.value
        raise ValueError("Constante no soportada")

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[node.id]
        if node.id in self.state.variables:
            return self.state.variables[node.id]
        raise ValueError(f"Variable o constante desconocida: {node.id}")

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(elt) for elt in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return tuple(self.visit(elt) for elt in node.elts)

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Solo se permiten llamadas a funciones simples")
        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise ValueError(f"Función no permitida: {func_name}")
        func = ALLOWED_FUNCTIONS[func_name]
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Elemento no soportado: {node.__class__.__name__}")


def parse_assignment(line: str) -> Tuple[str, str]:
    parts = line.split("=", 1)
    if len(parts) != 2:
        raise ValueError("Asignación inválida")
    name = parts[0].strip()
    if not name.isidentifier():
        raise ValueError("Nombre de variable inválido")
    expr = parts[1].strip()
    if not expr:
        raise ValueError("La expresión no puede estar vacía")
    return name, expr


def evaluate_expression(expr: str, state: CalcState) -> Any:
    tree = ast.parse(expr, mode="eval")
    evaluator = SafeEvaluator(state)
    return evaluator.visit(tree)


def format_result(result: Any) -> str:
    if is_matrix(result):
        lines = ["[" + ", ".join(f"{value:g}" for value in row) + "]" for row in result]
        return "[\n  " + ",\n  ".join(lines) + "\n]"
    if isinstance(result, list):
        return "[" + ", ".join(str(item) for item in result) + "]"
    if isinstance(result, tuple):
        return "(" + ", ".join(str(item) for item in result) + ")"
    if isinstance(result, float):
        return f"{result:.10g}"
    return str(result)


def print_help() -> None:
    print(
        """
Calculadora avanzada (CLI)

Comandos:
  ayuda | help      Muestra esta ayuda
  historia         Muestra el historial
  limpiar          Limpia la pantalla
  salir | exit     Termina la calculadora

Ejemplos:
  2 + 3 * 5
  a = 10
  b = sin(pi / 2)
  det([[1,2],[3,4]])
  matmul([[1,2],[3,4]], [[5],[6]])
  mean([1,2,3,4,5])
"""
    )


def run_repl() -> None:
    state = CalcState(variables=dict(ALLOWED_CONSTANTS))
    print("Calculadora avanzada. Escribe 'ayuda' para ver comandos.")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        if not line:
            continue
        if line.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego.")
            break
        if line.lower() in {"ayuda", "help"}:
            print_help()
            continue
        if line.lower() == "historia":
            for idx, entry in enumerate(state.history, start=1):
                print(f"{idx}: {entry}")
            continue
        if line.lower() == "limpiar":
            print("\033[2J\033[H", end="")
            continue
        try:
            if "=" in line:
                name, expr = parse_assignment(line)
                result = evaluate_expression(expr, state)
                state.variables[name] = result
                output = f"{name} = {format_result(result)}"
            else:
                result = evaluate_expression(line, state)
                output = format_result(result)
            state.history.append(f"{line} -> {output}")
            print(output)
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_repl()
