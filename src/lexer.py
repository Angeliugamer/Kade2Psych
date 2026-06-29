"""
lexer.py
│
├── Parte 1
│   Imports
│   TokenType
│   Keywords
│   Operators
│   Separators
│
├── Parte 2
│   Token class
│   LexerError
│
├── Parte 3
│   Lexer.__init__()
│   Helpers
│
├── Parte 4
│   Scanner
│   advance()
│   peek()
│   skipSpaces()
│
├── Parte 5
│   scanIdentifier()
│
├── Parte 6
│   scanNumber()
│
├── Parte 7
│   scanString()
│
├── Parte 8
│   scanComment()
│
├── Parte 9
│   nextToken()
│
├── Parte 10
│   tokenize()
│
└── Parte 11
    Tests internos

=========================================================
Kade2Psych Lexer
---------------------------------------------------------
Lexer (scanner) para Lua 5.1 utilizado por Kade2Psych.

Su única responsabilidad es convertir texto en una lista
de tokens.

NO interpreta Lua.
NO construye el AST.
NO conoce nada sobre Kade Engine.

Author:
    ChatGPT + Angeliu Gamer
=========================================================
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

# =========================================================
# TOKEN TYPES
# =========================================================

class TokenType(Enum):
    # ---------- End ----------
    EOF = auto()

    # ---------- Identifiers ----------
    IDENTIFIER = auto()

    # ---------- Literals ----------
    NUMBER = auto()
    STRING = auto()

    TRUE = auto()
    FALSE = auto()
    NIL = auto()

    # ---------- Keywords ----------
    AND = auto()
    BREAK = auto()
    DO = auto()
    ELSE = auto()
    ELSEIF = auto()
    END = auto()
    FOR = auto()
    FUNCTION = auto()
    GOTO = auto()
    IF = auto()
    IN = auto()
    LOCAL = auto()
    NOT = auto()
    OR = auto()
    REPEAT = auto()
    RETURN = auto()
    THEN = auto()
    UNTIL = auto()
    WHILE = auto()

    # ---------- Symbols ----------
    LPAREN = auto()          # (
    RPAREN = auto()          # )

    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]

    LBRACE = auto()          # {
    RBRACE = auto()          # }

    COMMA = auto()           # ,
    DOT = auto()             # .
    COLON = auto()           # :
    SEMICOLON = auto()       # ;

    # ---------- Operators ----------
    ASSIGN = auto()          # =

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()

    CONCAT = auto()          # ..

    VARARG = auto()          # ...

    LT = auto()
    GT = auto()

    LE = auto()
    GE = auto()

    EQ = auto()
    NE = auto()

    LENGTH = auto()          # #

    # ---------- Misc ----------
    UNKNOWN = auto()

# =========================================================
# LUA KEYWORDS
# =========================================================

KEYWORDS = {
    "and": TokenType.AND,

    "break": TokenType.BREAK,

    "do": TokenType.DO,

    "else": TokenType.ELSE,

    "elseif": TokenType.ELSEIF,

    "end": TokenType.END,

    "false": TokenType.FALSE,

    "for": TokenType.FOR,

    "function": TokenType.FUNCTION,

    "goto": TokenType.GOTO,

    "if": TokenType.IF,

    "in": TokenType.IN,

    "local": TokenType.LOCAL,

    "nil": TokenType.NIL,

    "not": TokenType.NOT,

    "or": TokenType.OR,

    "repeat": TokenType.REPEAT,

    "return": TokenType.RETURN,

    "then": TokenType.THEN,

    "true": TokenType.TRUE,

    "until": TokenType.UNTIL,

    "while": TokenType.WHILE,
}

# =========================================================
# OPERATORS
# =========================================================

OPERATORS = {
    "=": TokenType.ASSIGN,

    "+": TokenType.PLUS,

    "-": TokenType.MINUS,

    "*": TokenType.STAR,

    "/": TokenType.SLASH,

    "%": TokenType.PERCENT,

    "^": TokenType.CARET,

    "#": TokenType.LENGTH,

    "<": TokenType.LT,

    ">": TokenType.GT,

    "<=": TokenType.LE,

    ">=": TokenType.GE,

    "==": TokenType.EQ,

    "~=": TokenType.NE,

    "..": TokenType.CONCAT,

    "...": TokenType.VARARG,
}

# =========================================================
# SEPARATORS
# =========================================================

SEPARATORS = {
    "(": TokenType.LPAREN,

    ")": TokenType.RPAREN,

    "[": TokenType.LBRACKET,

    "]": TokenType.RBRACKET,

    "{": TokenType.LBRACE,

    "}": TokenType.RBRACE,

    ",": TokenType.COMMA,

    ".": TokenType.DOT,

    ":": TokenType.COLON,

    ";": TokenType.SEMICOLON,
}

