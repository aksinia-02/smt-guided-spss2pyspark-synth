import re
import functools

from dataclasses import dataclass
from typing import List, Union

import logging
from logger.logger import logger, log_list

def log_step(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        current_token = self._peek() if hasattr(self, "_peek") else "N/A"
        logger.debug(f"Entering {func.__name__} | Current token: {current_token}")
        result = func(self, *args, **kwargs)
        logger.debug(f"Exiting {func.__name__} -> Produced: {type(result).__name__}")
        return result
    return wrapper

class ASTNode:
    pass

@dataclass
class LiteralNode(ASTNode):
    value: Union[str, int, float, bool]

@dataclass
class ParamNode(ASTNode):
    name: str

@dataclass
class FieldNode(ASTNode):
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

@dataclass
class UnaryOpNode(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class IfElseNode(ASTNode):
    conditions: List[tuple[ASTNode, ASTNode]]  # list of (condition, expression)
    else_expr: Optional[ASTNode]

@dataclass
class ListNode(ASTNode):
    elements: List[ASTNode]


class SPSSExpressionParser:
    # Multi-character operators must precede single-character ones (e.g., <= before <)
    TOKEN_REGEX = [
        ("NUMBER", r"\d+(\.\d+)?"),
        ("STRING", r"'[^']*'|\"[^\"]*\""),
        ("CONCAT", r"><"),
        ("NEQ", r"/=|!="),
        ("LTE", r"<="),
        ("GTE", r">="),
        ("EQ", r"="),
        ("LT", r"<"),
        ("GT", r">"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("AND", r"\band\b"),
        ("OR", r"\bor\b"),
        ("NOT", r"\bnot\b"),
        ("IF", r"\bif\b"),
        ("THEN", r"\bthen\b"),
        ("ELSEIF", r"\belseif\b"),
        ("ELSE", r"\belse\b"),
        ("ENDIF", r"\bendif\b"),
        ("UNDEF", r"\bundef\b"),
        ("IDENT", r"[@\$]?[a-zA-Z_äöüÄÖÜß][a-zA-Z0-9_äöüÄÖÜß\-]*"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),
        ("COMMA", r","),
        ("SKIP", r"\s+"),
        ("MISMATCH", r"."),
    ]

    def __init__(self, text: str):
        logger.info(f"Initializing parser with input: {repr(text)}")
        self.tokens = self._tokenize(text)
        self.pos = 0
        log_list("Tokens found", self.tokens, level=logging.INFO)

    def _tokenize(self, text: str):
        tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in self.TOKEN_REGEX)
        tokens = []
        for mo in re.finditer(tok_regex, text, flags=re.IGNORECASE):
            kind = mo.lastgroup
            val = mo.group()
            if kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                logger.error(f"Syntax error encountering character: {val}")
                raise SyntaxError(f"Unexpected character: {val}")
            tokens.append((kind, val))
        tokens.append(("EOF", ""))
        return tokens

    def _peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return ("EOF", "")

    def _consume(self, expected_kind=None):
        # Returns the current token and increment the position
        kind, val = self.tokens[self.pos]
        # if expected_kind and kind != expected_kind:
        #     raise SyntaxError(f"Expected {expected_kind}, got {kind} ('{val}')")
        logger.debug(f"Consumed token: ({kind}, '{val}') at position {self.pos}")
        self.pos += 1
        return kind, val

    # First going deep into the expression tree.
    # The latest layer is the primary expressions (literals, params, functions, parentheses).
    # The order then is the multiplicative operations (* and /), 
    # then additive (+ and -), 
    # then comparisons (=, !=, <, <=, >, >=), 
    # then logical AND, 
    # and finally logical OR.
    @log_step
    def parse(self) -> ASTNode:
        if self._peek()[0] == "IF":
            return self._parse_if_expression()
        return self._parse_or()

    @log_step
    def _parse_if_expression(self) -> ASTNode:
        self._consume("IF")
        conditions = []
        
        cond = self._parse_or()
        self._consume("THEN")
        then_expr = self.parse()
        conditions.append((cond, then_expr))
        
        else_expr = None
        while self._peek()[0] == "ELSEIF":
            self._consume("ELSEIF")
            elif_cond = self._parse_or()
            self._consume("THEN")
            elif_expr = self.parse()
            conditions.append((elif_cond, elif_expr))

        if self._peek()[0] == "ELSE":
            self._consume("ELSE")
            else_expr = self.parse()

        self._consume("ENDIF")
        return IfElseNode(conditions=conditions, else_expr=else_expr)

    # The binary operations are OR, AND, comparisons (=, !=, <, <=, >, >=), additive (+ and -), and multiplicative (* and /).

    @log_step
    def _parse_or(self) -> ASTNode:
        left = self._parse_and()
        while self._peek()[0] == "OR":
            _, op = self._consume("OR")
            right = self._parse_and()
            left = BinaryOpNode(op=op.lower(), left=left, right=right)
        return left

    # --- Precedence Level 2: Logical AND ---
    @log_step
    def _parse_and(self) -> ASTNode:
        left = self._parse_not()
        while self._peek()[0] == "AND":
            _, op = self._consume("AND")
            right = self._parse_not()
            left = BinaryOpNode(op=op.lower(), left=left, right=right)
        return left

    def _parse_not(self) -> ASTNode:
        if self._peek()[0] == "NOT":
            _, op = self._consume("NOT")
            operand = self._parse_not()
            return UnaryOpNode(op="not", operand=operand)
        return self._parse_relational()

    # --- Precedence Level 3: Comparisons (=, !=, <, <=, >, >=) ---
    @log_step
    def _parse_relational(self) -> ASTNode:
        left = self._parse_additive()
        relational_tokens = {"EQ", "NEQ", "LT", "LTE", "GT", "GTE"}
        
        while self._peek()[0] in relational_tokens:
            _, op = self._consume()
            right = self._parse_additive()
            left = BinaryOpNode(op=op, left=left, right=right)
        return left

    # --- Precedence Level 4: Additive Operations (+ and -) ---
    @log_step
    def _parse_additive(self) -> ASTNode:
        left = self._parse_multiplicative()
        while self._peek()[0] in ("PLUS", "MINUS", "CONCAT"):
            _, op = self._consume()
            right = self._parse_multiplicative()
            left = BinaryOpNode(op=op, left=left, right=right)
        return left

    # --- Precedence Level 5: Multiplicative Operations (* and /) ---
    @log_step
    def _parse_multiplicative(self) -> ASTNode:
        left = self._parse_primary()
        while self._peek()[0] in ("MUL", "DIV"):
            _, op = self._consume()
            right = self._parse_primary()
            left = BinaryOpNode(op=op, left=left, right=right)
        return left

    # --- Precedence Level 6: Primaries (Literals, Params, Functions, Parentheses) ---
    @log_step
    def _parse_primary(self) -> ASTNode:
        kind, val = self._peek()

        if kind == "UNDEF":
            self._consume("UNDEF")
            return LiteralNode(value=None)

        elif kind == "IDENT":
            self._consume("IDENT")
            if self._peek()[0] == "LPAREN":
                self._consume("LPAREN")
                args = []
                if self._peek()[0] != "RPAREN":
                    args.append(self.parse())
                    while self._peek()[0] == "COMMA":
                        self._consume("COMMA")
                        args.append(self.parse())
                self._consume("RPAREN")
                return FunctionCallNode(name=val, args=args)
            elif val.startswith("$P-"):
                return ParamNode(name=val)
            else:
                return FieldNode(name=val)

        elif kind == "STRING":
            self._consume("STRING")
            raw_str = val[1:-1]  # Strip surrounding quotes
            if raw_str.startswith("$P-"):
                return ParamNode(name=raw_str)
            # Differentiate quoted field names from literals (heuristic for SPSS quotes)
            #TODO: consider the cases with whitespace in column names, then 'name name' is not literal anymore
            if " " in raw_str or any(c in raw_str for c in ["-", "/"]):
                # Treat as Literal string unless domain specifies as field reference
                return LiteralNode(value=raw_str)
            return LiteralNode(value=raw_str)

        elif kind == "NUMBER":
            self._consume("NUMBER")
            num_val = float(val) if "." in val else int(val)
            return LiteralNode(value=num_val)

        elif kind == "LPAREN":
            self._consume("LPAREN")
            node = self.parse()
            self._consume("RPAREN")
            return node

        elif kind == "LBRACKET":
            # Parsing array/list syntax: [1 2 3] or ["A" "B"]
            self._consume("LBRACKET")
            elements = []
            while self._peek()[0] not in ("RBRACKET", "EOF"):
                elements.append(self._parse_primary())
                if self._peek()[0] == "COMMA":
                    self._consume("COMMA")
            self._consume("RBRACKET")
            return ListNode(elements=elements)

        raise SyntaxError(f"Unexpected token: {kind} ('{val}')")

    def print_ast(self, node: ASTNode, indent: int = 0):
        space = "  " * indent

        if isinstance(node, BinaryOpNode):
            print(f"{space}BinaryOpNode(op='{node.op}')")
            self.print_ast(node.left, indent + 1)
            self.print_ast(node.right, indent + 1)

        elif isinstance(node, UnaryOpNode):
            print(f"{space}UnaryOpNode(op='{node.op}')")
            self.print_ast(node.operand, indent + 1)

        elif isinstance(node, FunctionCallNode):
            print(f"{space}FunctionCallNode(name='{node.name}')")
            for arg in node.args:
                self.print_ast(arg, indent + 1)

        elif isinstance(node, IfElseNode):
            print(f"{space}IfElseNode()")
            for i, (cond, expr) in enumerate(node.conditions):
                branch = "IF" if i == 0 else "ELSEIF"
                print(f"{space}  Branch ({branch}):")
                print(f"{space}    Condition:")
                self.print_ast(cond, indent + 3)
                print(f"{space}    Then:")
                self.print_ast(expr, indent + 3)
            if node.else_expr:
                print(f"{space}  Else:")
                self.print_ast(node.else_expr, indent + 2)

        elif isinstance(node, ListNode):
            print(f"{space}ListNode()")
            for item in node.elements:
                self.print_ast(item, indent + 1)

        elif isinstance(node, FieldNode):
            print(f"{space}FieldNode(name='{node.name}')")

        elif isinstance(node, ParamNode):
            print(f"{space}ParamNode(name='{node.name}')")

        elif isinstance(node, LiteralNode):
            print(f"{space}LiteralNode(value={repr(node.value)})")

        else:
            print(f"{space}UnknownNode({type(node).__name__})")