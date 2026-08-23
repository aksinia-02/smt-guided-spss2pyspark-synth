import re

from dataclasses import dataclass
from typing import List, Union

class ASTNode:
    pass

@dataclass
class LiteralNode(ASTNode):
    value: Union[str, int]

@dataclass
class ParamNode(ASTNode):
    name: str

@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]

@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

class SPSSExpressionParser:
    TOKEN_REGEX = [
        ("NUMBER", r"\d+"),
        ("STRING", r"'[^']*'|\"[^\"]*\""),
        ("IDENT", r"\$?[a-zA-Z_][a-zA-Z0-9_\-]*"),
        ("PLUS", r"\+"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("COMMA", r","),
        ("SKIP", r"\s+"),
        ("MISMATCH", r"."),
    ]

    def __init__(self, text: str):
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str):
        tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in self.TOKEN_REGEX)
        tokens = []
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            val = mo.group()
            if kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character: {val}")
            tokens.append((kind, val))
        tokens.append(("EOF", ""))
        return tokens

    def _peek(self):
        return self.tokens[self.pos]

    def _consume(self, expected_kind=None):
        kind, val = self.tokens[self.pos]
        if expected_kind and kind != expected_kind:
            raise SyntaxError(f"Expected {expected_kind}, got {kind} ('{val}')")
        self.pos += 1
        return kind, val

    def parse(self) -> ASTNode:
        return self._parse_binary_op()

    def _parse_binary_op(self) -> ASTNode:
        """Handles operator precedence for binary operations like '+'."""
        left = self._parse_primary()
        while self._peek()[0] == "PLUS":
            _, op = self._consume("PLUS")
            right = self._parse_primary()
            left = BinaryOpNode(op=op, left=left, right=right)
        return left

    def _parse_primary(self) -> ASTNode:
        """Parses function calls, parameter tokens, strings, and numbers."""
        kind, val = self._peek()

        if kind == "IDENT":
            self._consume("IDENT")
            if self._peek()[0] == "LPAREN":
                # Function call e.g., startstring(...)
                self._consume("LPAREN")
                args = []
                if self._peek()[0] != "RPAREN":
                    args.append(self._parse_binary_op())
                    while self._peek()[0] == "COMMA":
                        self._consume("COMMA")
                        args.append(self._parse_binary_op())
                self._consume("RPAREN")
                return FunctionCallNode(name=val, args=args)
            elif val.startswith("$P-"):
                return ParamNode(name=val)
            else:
                return LiteralNode(value=val)

        elif kind == "STRING":
            self._consume("STRING")
            raw_str = val[1:-1]  # Strip quotes
            # Convert quoted parameter strings '$P-...' directly into ParamNode
            if raw_str.startswith("$P-"):
                return ParamNode(name=raw_str)
            return LiteralNode(value=raw_str)

        elif kind == "NUMBER":
            self._consume("NUMBER")
            return LiteralNode(value=int(val))

        elif kind == "LPAREN":
            self._consume("LPAREN")
            node = self._parse_binary_op()
            self._consume("RPAREN")
            return node

        raise SyntaxError(f"Unexpected token: {kind} ('{val}')")

    def print_ast(self, node, indent=0):
        space = "  " * indent
        if isinstance(node, BinaryOpNode):
            print(f"{space}BinaryOpNode(op='{node.op}')")
            self.print_ast(node.left, indent + 1)
            self.print_ast(node.right, indent + 1)
        elif isinstance(node, FunctionCallNode):
            print(f"{space}FunctionCallNode(name='{node.name}')")
            for arg in node.args:
                self.print_ast(arg, indent + 1)
        elif isinstance(node, ParamNode):
            print(f"{space}ParamNode(name='{node.name}')")
        elif isinstance(node, LiteralNode):
            print(f"{space}LiteralNode(value={repr(node.value)})")