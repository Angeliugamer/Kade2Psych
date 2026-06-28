"""
=========================================================
lexer.py
---------------------------------------------------------
Lexer especializado para modcharts de Kade/Taro.

Este lexer convierte el código Lua en una lista de Tokens.

No interpreta el código.
No convierte nada.
Simplemente divide el texto en piezas.
=========================================================
"""

from dataclasses import dataclass
from enum import Enum, auto

# =========================================================
# TOKEN TYPES
# =========================================================

class TokenType(Enum):

    EOF = auto()

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    KEYWORD = auto()

    OPERATOR = auto()

    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()

    LPAREN = auto()
    RPAREN = auto()

    LBRACKET = auto()
    RBRACKET = auto()

    LBRACE = auto()
    RBRACE = auto()

    COMMENT = auto()

    NEWLINE = auto()

# =========================================================
# TOKEN
# =========================================================

@dataclass(slots=True)
class Token:

    type: TokenType
    value: str

    line: int
    column: int

    def __repr__(self):

        return (
            f"<{self.type.name} "
            f"{repr(self.value)} "
            f"({self.line}:{self.column})>"
        )

# =========================================================
# LUA KEYWORDS
# =========================================================

KEYWORDS = {

    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "goto",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while",

}

# =========================================================
# LUA OPERATORS
# =========================================================

OPERATORS = {

    "+",
    "-",
    "*",
    "/",
    "%",
    "^",

    "=",
    "==",
    "~=",
    "<",
    "<=",
    ">",
    ">=",

    "..",

    "#",

}

# =========================================================
# LEXER
# =========================================================

class Lexer:

    def __init__(self, source: str):

        self.source = source

        self.length = len(source)

        self.index = 0

        self.line = 1
        self.column = 1

        self.tokens = []

    # =====================================================
    # BASIC
    # =====================================================

    def eof(self):

        return self.index >= self.length


    def current(self):

        if self.eof():
            return "\0"

        return self.source[self.index]


    def peek(self, offset=1):

        pos = self.index + offset

        if pos >= self.length:
            return "\0"

        return self.source[pos]


    def advance(self):

        c = self.current()

        self.index += 1

        if c == "\n":

            self.line += 1
            self.column = 1

        else:

            self.column += 1

        return c


    # =====================================================
    # TOKEN CREATION
    # =====================================================

    def add_token(
        self,
        token_type,
        value,
        line=None,
        column=None
    ):

        if line is None:
            line = self.line

        if column is None:
            column = self.column

        self.tokens.append(
            Token(
                token_type,
                value,
                line,
                column
            )
        )


    # =====================================================
    # HELPERS
    # =====================================================

    def is_space(self, c):

        return c in " \t\r"


    def is_newline(self, c):

        return c == "\n"


    def is_digit(self, c):
        return c.isdigit()


    def is_letter(self, c):
        return (
            c.isalpha()
            or c == "_"
        )


    def is_identifier(self, c):
        return (
            self.is_letter(c)
            or self.is_digit(c)
        )


    # =====================================================
    # MAIN
    # =====================================================

    def lex(self):

        """
        Punto de entrada del lexer.

        Será implementado completamente
        en la Parte 2.
        """

        raise NotImplementedError(
            "Lexer.lex() todavía no está implementado."
        )
    
    # =====================================================
    # WHITESPACE
    # =====================================================

    def skip_whitespace(self):

        while not self.eof():

            c = self.current()

            if c in " \t\r":
                self.advance()
                continue

            break

    # =====================================================
    # COMMENTS
    # =====================================================

    def read_comment(self):

        line = self.line
        column = self.column

        # consumir --
        self.advance()
        self.advance()

        text = ""

        # comentario largo --[[ ]]
        if self.current() == "[" and self.peek() == "[":

            self.advance()
            self.advance()

            while not self.eof():

                if self.current() == "]" and self.peek() == "]":
                    self.advance()
                    self.advance()
                    break

                text += self.advance()

        else:

            while not self.eof():

                if self.current() == "\n":
                    break

                text += self.advance()

        self.add_token(
            TokenType.COMMENT,
            text,
            line,
            column
        )

    # =====================================================
    # SYMBOLS
    # =====================================================

    def read_symbol(self):

        c = self.current()

        line = self.line
        column = self.column

        mapping = {
            "(" : TokenType.LPAREN,
            ")" : TokenType.RPAREN,

            "[" : TokenType.LBRACKET,
            "]" : TokenType.RBRACKET,

            "{" : TokenType.LBRACE,
            "}" : TokenType.RBRACE,

            "," : TokenType.COMMA,
            "." : TokenType.DOT,
            ":" : TokenType.COLON,
            ";" : TokenType.SEMICOLON,
        }

        if c in mapping:

            self.advance()

            self.add_token(
                mapping[c],
                c,
                line,
                column
            )

            return True

        return False

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def lex(self):

        while not self.eof():

            c = self.current()

            # -------------------------
            # espacios
            # -------------------------

            if self.is_space(c):
                self.skip_whitespace()
                continue

            # -------------------------
            # saltos de línea
            # -------------------------

            if self.is_newline(c):
                self.add_token(
                    TokenType.NEWLINE,
                    "\\n",
                    self.line,
                    self.column
                )

                self.advance()
                continue

            # -------------------------
            # comentarios
            # -------------------------

            if c == "-" and self.peek() == "-":
                self.read_comment()
                continue

            # -------------------------
            # símbolos
            # -------------------------

            if self.read_symbol():
                continue

            # -------------------------
            # identificadores
            # (Parte 2B)
            # -------------------------

            if self.is_letter(c):
                self.read_identifier()
                continue

            # -------------------------
            # números
            # (Parte 2B)
            # -------------------------

            if self.is_digit(c):
                self.read_number()
                continue

            # -------------------------
            # números tipo .25
            # (Parte 2B)
            # -------------------------

            if c == "." and self.peek().isdigit():
                self.read_number()
                continue

            # -------------------------
            # strings
            # (Parte 2B)
            # -------------------------

            if c == '"' or c == "'":
                self.read_string()
                continue

            # -------------------------
            # operadores
            # (Parte 2C)
            # -------------------------

            if c in "+-*/%=<>~#^":
                self.read_operator()
                continue

            # -------------------------
            # cualquier otra cosa
            # -------------------------

            raise SyntaxError(
                f"Unexpected character '{c}' "
                f"at line {self.line}, column {self.column}"
            )

        self.add_token(
            TokenType.EOF,
            "",
            self.line,
            self.column
        )

        return self.tokens
    
    # =====================================================
    # IDENTIFIERS / KEYWORDS
    # =====================================================

    def read_identifier(self):

        line = self.line
        column = self.column

        text = ""

        while not self.eof():

            c = self.current()

            if not self.is_identifier(c):
                break

            text += self.advance()

        token_type = (
            TokenType.KEYWORD
            if text in KEYWORDS
            else TokenType.IDENTIFIER
        )

        self.add_token(
            token_type,
            text,
            line,
            column
        )

    # =====================================================
    # NUMBERS
    # =====================================================

    def read_number(self):

        line = self.line
        column = self.column

        text = ""

        has_dot = False

        # permite números como .25
        if self.current() == ".":

            has_dot = True
            text += self.advance()

        while not self.eof():

            c = self.current()

            if c.isdigit():

                text += self.advance()
                continue

            if c == "." and not has_dot:

                has_dot = True
                text += self.advance()
                continue

            break

        self.add_token(
            TokenType.NUMBER,
            text,
            line,
            column
        )

    # =====================================================
    # STRINGS
    # =====================================================

    def read_string(self):

        line = self.line
        column = self.column

        quote = self.advance()

        text = ""

        while not self.eof():

            c = self.current()

            # secuencias de escape
            if c == "\\":

                text += self.advance()

                if not self.eof():
                    text += self.advance()

                continue

            # fin del string
            if c == quote:

                self.advance()

                self.add_token(
                    TokenType.STRING,
                    text,
                    line,
                    column
                )

                return

            text += self.advance()

        raise SyntaxError(
            f"Unterminated string at line {line}, column {column}"
        )
    