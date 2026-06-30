"""
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

# =========================================================
# TOKEN
# =========================================================

@dataclass(slots=True)
class Token:
    """
    Token generado por el lexer.

    Attributes
    ----------
    type:
        Tipo del token.

    value:
        Valor original.

    line:
        Línea del archivo.

    column:
        Columna donde comienza.

    index:
        Posición absoluta dentro del texto.
    """

    type: TokenType

    value: Optional[str]

    line: int

    column: int

    index: int

    def __str__(self):

        return (
            f"{self.type.name}"
            f"({repr(self.value)}) "
            f"[{self.line}:{self.column}]"
        )

    def __repr__(self):

        return self.__str__()

# =========================================================
# LEXER ERROR
# =========================================================

class LexerError(Exception):
    """
    Error producido durante el análisis léxico.
    """

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        index: int
    ):

        self.message = message
        self.line = line
        self.column = column
        self.index = index

        super().__init__(self.__str__())

    def __str__(self):

        return (
            f"LexerError"
            f"({self.line}:{self.column}) "
            f"{self.message}"
        )

# =========================================================
# INTERNAL CONSTANTS
# =========================================================

WHITESPACE = {
    ' ',
    '\t',
    '\r',
    '\n'
}


IDENTIFIER_START = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

IDENTIFIER_BODY = (
    IDENTIFIER_START +
    "0123456789"
)

HEX_DIGITS = "0123456789abcdefABCDEF"

DECIMAL_DIGITS = "0123456789"

# =========================================================
# LEXER
# =========================================================

class Lexer:
    """
    Scanner para Lua 5.1.

    Convierte una cadena de texto en una secuencia de Tokens.
    """

    def __init__(self, source: str, filename: str = "<stdin>"):

        self.source = source
        self.filename = filename

        # Posición absoluta dentro del texto
        self.index = 0

        # Línea actual (empieza en 1)
        self.line = 1

        # Columna actual (empieza en 1)
        self.column = 1

        # Longitud del archivo
        self.length = len(source)

    # =====================================================
    # CHARACTER ACCESS
    # =====================================================

    @property
    def current_char(self) -> Optional[str]:
        """
        Carácter actual.

        Devuelve None si se llegó al final del archivo.
        """

        if self.index >= self.length:
            return None

        return self.source[self.index]

    def peek(self, offset: int = 1) -> Optional[str]:
        """
        Mira caracteres futuros sin avanzar.
        """

        pos = self.index + offset

        if pos >= self.length:
            return None

        return self.source[pos]

    def previous(self) -> Optional[str]:
        """
        Devuelve el carácter anterior.
        """

        if self.index <= 0:
            return None

        return self.source[self.index - 1]


    def is_eof(self) -> bool:
        """
        ¿Se llegó al final del archivo?
        """

        return self.index >= self.length

    # =====================================================
    # MOVEMENT
    # =====================================================

    def advance(self) -> Optional[str]:
        """
        Avanza un carácter.

        Devuelve el carácter leído.
        """

        if self.is_eof():
            return None

        char = self.source[self.index]

        self.index += 1

        if char == '\n':
            self.line += 1
            self.column = 1

        else:
            self.column += 1

        return char

    def advance_n(self, count: int):
        for _ in range(count):
            self.advance()

    def match(self, text: str) -> bool:
        """
        Comprueba si el texto actual coincide.
        """

        end = self.index + len(text)

        return self.source[self.index:end] == text

    # =====================================================
    # TOKEN CREATION
    # =====================================================

    def make_token(
        self,
        token_type: TokenType,
        value: Optional[str],
        start_line: int,
        start_column: int,
        start_index: int
    ) -> Token:

        return Token(
            type=token_type,
            value=value,
            line=start_line,
            column=start_column,
            index=start_index
        )

    # =====================================================
    # ERRORS
    # =====================================================

    def error(self, message: str):
        raise LexerError(
            message=message,
            line=self.line,
            column=self.column,
            index=self.index
        )
    
    # =====================================================
    # SCANNER HELPERS
    # =====================================================

    def consume(self) -> str:
        """
        Consume el carácter actual.

        Lanza LexerError si ya estamos en EOF.
        """

        if self.is_eof():
            self.error("Unexpected end of file.")

        return self.advance()


    def skip_whitespace(self):
        """
        Salta espacios, tabs y saltos de línea.
        """

        while not self.is_eof():
            c = self.current_char

            if c not in WHITESPACE:
                break

            self.advance()


    def skip_comment(self):
        """
        Salta un comentario Lua.

        Soporta:

            --

            --[[ ]]

            --[=[ ]=]

            etc.
        """

        if not self.match("--"):
            return

        self.advance_n(2)

        #
        # Long comment?
        #

        if self.current_char == '[':
            level = self._long_bracket_level()

            if level >= 0:

                self._consume_long_string(level)

                return

        #
        # Single line comment
        #

        while not self.is_eof():
            if self.current_char == '\n':
                break

            self.advance()


    def skip_ignored(self):
        """
        Salta cualquier cosa que el parser
        nunca necesita ver.
        """

        while True:

            self.skip_whitespace()

            if self.match("--"):

                self.skip_comment()

                continue

            break

    # =====================================================
    # CHARACTER TESTS
    # =====================================================

    def is_identifier_start(self, c: str | None) -> bool:

        return c is not None and c in IDENTIFIER_START

    def is_identifier_body(self, c: str | None) -> bool:

        return c is not None and c in IDENTIFIER_BODY

    def is_digit(self, c: str | None) -> bool:

        return c is not None and c in DECIMAL_DIGITS

    def is_hex_digit(self, c: str | None) -> bool:

        return c is not None and c in HEX_DIGITS

    # =====================================================
    # LONG STRINGS / COMMENTS
    # =====================================================

    def _long_bracket_level(self) -> int:
        """
        Detecta:

            [[

            [=[

            [==[

        Devuelve:

            -1  -> no es long bracket

             0  -> [[

             1  -> [=[

             2  -> [==[
        """

        if self.current_char != '[':
            return -1

        pos = self.index + 1

        level = 0

        while pos < self.length and self.source[pos] == '=':

            level += 1
            pos += 1

        if pos >= self.length:
            return -1

        if self.source[pos] != '[':
            return -1

        return level


    def _consume_long_string(self, level: int):
        """
        Consume:

            [[ ]]

            [=[ ]=]

            [==[ ]==]

        Se utiliza tanto para comentarios
        como para strings largos.
        """

        #
        # Saltar apertura
        #

        self.advance()

        for _ in range(level):

            self.advance()

        self.advance()

        #
        # Leer contenido
        #

        while not self.is_eof():
            if self.current_char == ']':

                pos = self.index + 1

                count = 0

                while (
                    pos < self.length
                    and self.source[pos] == '='
                ):
                    count += 1
                    pos += 1

                if (
                    count == level
                    and pos < self.length
                    and self.source[pos] == ']'
                ):

                    self.advance()

                    for _ in range(level):
                        self.advance()

                    self.advance()

                    return

            self.advance()
        self.error("Unterminated long string/comment.")

    # =====================================================
    # IDENTIFIERS
    # =====================================================

    def read_identifier(self) -> str:
        """
        Lee un identificador Lua.

        El cursor debe estar situado sobre el primer
        carácter del identificador.

        Ejemplos:

            beat

            activeMods

            movex0

            _private

            math

            sin

        Devuelve únicamente el texto leído.
        """

        chars = []

        while not self.is_eof():

            c = self.current_char

            if not self.is_identifier_body(c):
                break

            chars.append(self.advance())

        return "".join(chars)


    def scan_identifier(self) -> Token:
        """
        Escanea un identificador o una palabra reservada.
        """

        start_line = self.line
        start_column = self.column
        start_index = self.index

        text = self.read_identifier()

        token_type = KEYWORDS.get(
            text,
            TokenType.IDENTIFIER
        )

        return self.make_token(
            token_type,
            text,
            start_line,
            start_column,
            start_index
        )

    # =====================================================
    # IDENTIFIER LOOKAHEAD
    # =====================================================

    def peek_identifier(self) -> str | None:
        """
        Devuelve el identificador siguiente sin mover
        el lexer.

        Muy útil para el parser.
        """

        if not self.is_identifier_start(self.current_char):
            return None

        saved_index = self.index
        saved_line = self.line
        saved_column = self.column

        text = self.read_identifier()

        self.index = saved_index
        self.line = saved_line
        self.column = saved_column

        return text
    
    # =====================================================
    # NUMBERS
    # =====================================================

    def _read_digits(self) -> str:
        """
        Lee una secuencia de dígitos decimales.
        """

        chars = []

        while self.is_digit(self.current_char):
            chars.append(self.advance())

        return "".join(chars)


    def _read_hex_digits(self) -> str:
        """
        Lee una secuencia de dígitos hexadecimales.
        """

        chars = []

        while self.is_hex_digit(self.current_char):
            chars.append(self.advance())

        return "".join(chars)


    def read_number(self) -> str:
        """
        Lee un número Lua.

        Soporta:

            123
            12.34
            .5
            5.
            1e5
            1.2e-3
            0xFF
            0xABCDEF
        """

        chars = []

        #
        # Hexadecimal
        #

        if self.match("0x") or self.match("0X"):

            chars.append(self.advance())
            chars.append(self.advance())

            digits = self._read_hex_digits()

            if digits == "":
                self.error("Expected hexadecimal digits.")

            chars.append(digits)

            return "".join(chars)

        #
        # Parte entera
        #

        chars.append(self._read_digits())

        #
        # Parte decimal
        #

        if self.current_char == '.' and self.peek() != '.':

            chars.append(self.advance())

            chars.append(self._read_digits())

        #
        # Exponente
        #

        if self.current_char in ('e', 'E'):

            chars.append(self.advance())

            if self.current_char in ('+', '-'):

                chars.append(self.advance())

            digits = self._read_digits()

            if digits == "":
                self.error("Expected exponent.")

            chars.append(digits)

        return "".join(chars)


    def scan_number(self) -> Token:
        """
        Escanea un literal numérico.
        """

        start_line = self.line
        start_column = self.column
        start_index = self.index

        value = self.read_number()

        return self.make_token(
            TokenType.NUMBER,
            value,
            start_line,
            start_column,
            start_index
        )
    
    # =====================================================
    # STRINGS
    # =====================================================

    def read_escape(self) -> str:
        """
        Lee una secuencia de escape Lua.

        El cursor debe estar situado justo después del '\'.
        """

        if self.is_eof():
            self.error("Unexpected end of string.")

        c = self.advance()

        escapes = {
            'a': '\a',
            'b': '\b',
            'f': '\f',
            'n': '\n',
            'r': '\r',
            't': '\t',
            'v': '\v',
            '\\': '\\',
            '"': '"',
            "'": "'",
        }

        return escapes.get(c, c)


    def read_short_string(self) -> str:
        """
        Lee un string delimitado por
        comillas simples o dobles.
        """

        quote = self.consume()

        chars = []

        while not self.is_eof():

            c = self.current_char

            if c == quote:

                self.advance()

                return "".join(chars)

            if c == '\\':

                self.advance()

                chars.append(self.read_escape())

                continue

            if c == '\n':

                self.error("Unterminated string literal.")

            chars.append(self.advance())

        self.error("Unexpected end of file while reading string.")


    def read_long_string(self) -> str:
        """
        Lee:

            [[ ]]

            [=[ ]=]

            [==[ ]==]
        """

        level = self._long_bracket_level()

        if level < 0:
            self.error("Invalid long string.")

        #
        # Saltar apertura
        #

        self.advance()

        for _ in range(level):
            self.advance()

        self.advance()

        chars = []

        while not self.is_eof():

            #
            # ¿Fin?
            #

            if self.current_char == ']':

                pos = self.index + 1

                count = 0

                while (
                    pos < self.length
                    and self.source[pos] == '='
                ):
                    count += 1
                    pos += 1

                if (
                    count == level
                    and pos < self.length
                    and self.source[pos] == ']'
                ):

                    self.advance()

                    for _ in range(level):
                        self.advance()

                    self.advance()

                    return "".join(chars)

            chars.append(self.advance())

        self.error("Unterminated long string.")


    def scan_string(self) -> Token:
        """
        Escanea cualquier literal string Lua.
        """

        start_line = self.line
        start_column = self.column
        start_index = self.index

        if self.current_char == '[':
            value = self.read_long_string()

        else:
            value = self.read_short_string()

        return self.make_token(
            TokenType.STRING,
            value,
            start_line,
            start_column,
            start_index
        )

    # =====================================================
    # TOKEN DISPATCH
    # =====================================================

    def scan_operator(self) -> Token:
        """
        Escanea cualquier operador de Lua.

        Siempre intenta reconocer primero los operadores
        más largos.

        Ejemplo:

            ...
            ..
            <=
            >=
            ==
            ~=
        """

        start_line = self.line
        start_column = self.column
        start_index = self.index

        #
        # Operadores de 3 caracteres
        #

        if self.match("..."):

            self.advance_n(3)

            return self.make_token(
                TokenType.VARARG,
                "...",
                start_line,
                start_column,
                start_index
            )

        #
        # Operadores de 2 caracteres
        #

        for op in ("<=", ">=", "==", "~=", ".."):

            if self.match(op):

                self.advance_n(2)

                return self.make_token(
                    OPERATORS[op],
                    op,
                    start_line,
                    start_column,
                    start_index
                )

        #
        # Operadores simples
        #

        c = self.current_char

        if c in OPERATORS:

            self.advance()

            return self.make_token(
                OPERATORS[c],
                c,
                start_line,
                start_column,
                start_index
            )

        self.error(f"Unknown operator '{c}'.")


    def scan_separator(self) -> Token:
        """
        Escanea un separador.

        (

        )

        {

        }

        ,

        ;

        etc.
        """

        start_line = self.line
        start_column = self.column
        start_index = self.index

        c = self.consume()

        return self.make_token(
            SEPARATORS[c],

            c,

            start_line,

            start_column,

            start_index
        )


    def scan_symbol(self) -> Token:
        """
        Decide si el símbolo actual es
        un operador o un separador.
        """

        c = self.current_char

        #
        # Separadores
        #

        if c in SEPARATORS:

            #
            # '.' necesita tratamiento especial
            #

            if c == '.':
                return self.scan_operator()

            return self.scan_separator()

        #
        # Operadores
        #

        return self.scan_operator()
    
    # =====================================================
    # NEXT TOKEN
    # =====================================================

    def next_token(self) -> Token:
        """
        Devuelve el siguiente token del archivo.

        Si se llega al final del archivo devuelve EOF.
        """

        #
        # Ignorar espacios y comentarios
        #

        self.skip_ignored()

        #
        # EOF
        #

        if self.is_eof():

            return Token(
                TokenType.EOF,
                None,
                self.line,
                self.column,
                self.index
            )

        c = self.current_char

        #
        # ----------------------------
        # Identifier / Keyword
        # ----------------------------
        #

        if self.is_identifier_start(c):

            return self.scan_identifier()

        #
        # ----------------------------
        # Number
        # ----------------------------
        #

        if self.is_digit(c):

            return self.scan_number()

        #
        # Lua permite:
        #
        #     .5
        #
        #

        if c == '.' and self.is_digit(self.peek()):

            return self.scan_number()

        #
        # ----------------------------
        # String
        # ----------------------------
        #

        if c == '"' or c == "'":

            return self.scan_string()

        #
        # Long String
        # ----------------------------
        #

        if c == '[':

            if self._long_bracket_level() >= 0:

                return self.scan_string()

        #
        # ----------------------------
        # Operators / Separators
        # ----------------------------
        #

        if c in OPERATORS:

            return self.scan_operator()

        if c in SEPARATORS:

            return self.scan_separator()

        #
        # ----------------------------
        # Unknown character
        # ----------------------------
        #

        self.error(
            f"Unexpected character '{c}'."
        )

    # =====================================================
    # TOKENIZE
    # =====================================================

    def tokenize(self) -> list[Token]:
        """
        Convierte todo el código fuente en una lista de Tokens.

        Siempre incluye el token EOF al final.

        Returns
        -------
        list[Token]
            Lista completa de tokens.
        """

        tokens: list[Token] = []

        while True:

            token = self.next_token()

            tokens.append(token)

            if token.type == TokenType.EOF:
                break

        return tokens

    # =====================================================
    # ITERATOR
    # =====================================================

    def __iter__(self):
        """
        Permite iterar sobre el lexer directamente.

        Ejemplo:

            for token in Lexer(source):
                ...
        """

        while True:

            token = self.next_token()

            yield token

            if token.type == TokenType.EOF:
                break

    # =====================================================
    # DEBUG
    # =====================================================

    def dump_tokens(self):
        """
        Imprime todos los tokens por consola.

        Muy útil durante el desarrollo del parser.
        """

        for token in self.tokenize():
            print(token)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def reset(self):
        """
        Reinicia el lexer para volver a analizar el mismo
        archivo desde el principio.
        """

        self.index = 0
        self.line = 1
        self.column = 1


    def clone(self):
        """
        Crea un nuevo lexer apuntando al mismo código fuente.

        Muy útil para el parser cuando quiera hacer
        lookahead complejo.
        """

        lexer = Lexer(
            self.source,
            self.filename
        )

        lexer.index = self.index
        lexer.line = self.line
        lexer.column = self.column

        return lexer

    # =====================================================
    # POSITION
    # =====================================================

    def position(self):
        """
        Devuelve la posición actual.
        """

        return (
            self.line,
            self.column,
            self.index
        )

    def restore_position(self, position):
        """
        Restaura una posición guardada previamente.
        """

        self.line, self.column, self.index = position

    # =====================================================
    # DEBUG HELPERS
    # =====================================================

    def remaining_source(self):
        """
        Devuelve el texto restante por analizar.
        """

        return self.source[self.index:]

    def current_line_text(self):
        """
        Devuelve la línea actual completa.
        """

        lines = self.source.splitlines()

        if self.line - 1 >= len(lines):
            return ""

        return lines[self.line - 1]

    def error_context(self):
        """
        Devuelve una representación visual del error.
        """

        text = self.current_line_text()

        pointer = " " * (self.column - 1) + "^"

        return (
            text +
            "\n" +
            pointer
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):
        """
        Ejecuta el lexer completo únicamente para comprobar
        que el archivo es válido.

        Devuelve True si no hay errores.
        """

        self.reset()

        try:

            self.tokenize()

            return True

        except LexerError:

            return False

    # =====================================================
    # INFORMATION
    # =====================================================

    @property
    def finished(self):
        return self.is_eof()


    @property
    def progress(self):
        if self.length == 0:
            return 100.0

        return self.index * 100 / self.length


    def __len__(self):
        return self.length

    def __repr__(self):
        return (
            f"<Lexer "
            f"{self.filename} "
            f"{self.line}:{self.column}>"
        )
    
