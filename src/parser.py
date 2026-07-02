"""
=========================================
Kade2Psych Parser
Lua 5.1 Recursive Descent Parser
=========================================
parser.py

✅ Parte 1
Base del Parser

⬜ Parte 2
Expression Parser
(literales, identificadores, tablas)

⬜ Parte 3
Unary Operators

⬜ Parte 4
Binary Operators (precedencia)

⬜ Parte 5
CallExpression
MemberExpression
IndexExpression

⬜ Parte 6
Assignments

⬜ Parte 7
Statements

⬜ Parte 8
Functions

⬜ Parte 9
If / While / Repeat / For

⬜ Parte 10
Final + recuperación de errores
"""

from __future__ import annotations

import string
from typing import List
from typing import Optional
from xmlrpc.client import boolean

from lexer import Lexer
from lexer import Token
from lexer import TokenType

import ast

class Parser:
    """
    Parser recursivo para Lua 5.1.

    Convierte una lista de Tokens
    en un AST.
    """

    def __init__(self, lexer: Lexer):

        self.lexer = lexer

        #
        # Token actual
        #

        self.current: Token = self.lexer.next_token()

        #
        # Token anterior
        #

        self.previous: Optional[Token] = None

    # =====================================================
    # TOKEN HELPERS
    # =====================================================

    def advance(self) -> Token:
        """
        Consume el token actual.
        """

        self.previous = self.current

        self.current = self.lexer.next_token()

        return self.previous


    def check(self, token_type: TokenType) -> bool:
        """
        Comprueba el tipo del token actual.
        """

        return self.current.type == token_type


    def match(self, *types: TokenType) -> bool:
        """
        Consume el token si coincide.
        """

        if self.current.type in types:

            self.advance()

            return True

        return False


    def consume(
        self,
        token_type: TokenType,
        message: str
    ) -> Token:
        """
        Consume un token obligatorio.
        """

        if self.check(token_type):

            return self.advance()

        self.error(message)


    def peek(self) -> Token:
        """
        Devuelve el token actual.
        """

        return self.current
    
    # =====================================================
    # ERRORS
    # =====================================================

    def error(self, message: str):

        raise SyntaxError(

            f"{message}\n"

            f"Line {self.current.line}, "

            f"Column {self.current.column}"

        )
    
    # =====================================================
    # PUBLIC API
    # =====================================================

    def parse(self) -> ast.Program:
        """
        Punto de entrada del parser.
        """

        body = []

        while not self.check(TokenType.EOF):

            body.append(

                self.parse_statement()

            )

        return ast.Program(body)
    
# =====================================================
# STATEMENTS
# =====================================================

def parse_statement(self):

    #
    # local
    #

    if self.match(TokenType.LOCAL):

        if self.match(TokenType.FUNCTION):

            return self.parse_local_function()

        return self.parse_local()
    
    #
    # function
    #

    if self.match(TokenType.FUNCTION):

        return self.parse_function_declaration()
    #
    # return
    #

    if self.match(TokenType.RETURN):

        return self.parse_return()

    #
    # break
    #

    if self.match(TokenType.BREAK):

        return self.parse_break()

    #
    # do
    #

    if self.match(TokenType.DO):

        return self.parse_do()

    #
    # if
    #

    if self.match(TokenType.IF):

        return self.parse_if()

    #
    # while
    #

    if self.match(TokenType.WHILE):

        return self.parse_while()

    #
    # repeat
    #

    if self.match(TokenType.REPEAT):

        return self.parse_repeat()

    #
    # for
    #

    if self.match(TokenType.FOR):

        return self.parse_for()

    #
    # expression
    #

    return self.parse_expression_statement()

# =====================================================
# LOCAL
# =====================================================

def parse_local(self):

    names = []

    values = []

    #
    # Primer identificador
    #

    token = self.consume(

        TokenType.IDENTIFIER,

        "Expected local variable name."

    )

    names.append(

        ast.Identifier(token.value)

    )

    #
    # Más variables
    #

    while self.match(TokenType.COMMA):

        token = self.consume(

            TokenType.IDENTIFIER,

            "Expected local variable name."

        )

        names.append(

            ast.Identifier(token.value)

        )

    #
    # Inicialización
    #

    if self.match(TokenType.ASSIGN):

        values.append(

            self.parse_expression()

        )

        while self.match(TokenType.COMMA):

            values.append(

                self.parse_expression()

            )

    return ast.LocalStatement(

        names=names,

        values=values

    )

# =====================================================
# RETURN
# =====================================================

def parse_return(self):

    values = []

    #
    # return vacío
    #

    if self.check(

        TokenType.END,

        TokenType.ELSE,

        TokenType.ELSEIF,

        TokenType.UNTIL,

        TokenType.EOF

    ):

        return ast.ReturnStatement(

            values=values

        )

    #
    # Expresiones
    #

    values.append(

        self.parse_expression()

    )

    while self.match(TokenType.COMMA):

        values.append(

            self.parse_expression()

        )

    return ast.ReturnStatement(

        values=values

    )

# =====================================================
# BREAK
# =====================================================

def parse_break(self):

    return ast.BreakStatement()

# =====================================================
# DO BLOCK
# =====================================================

def parse_do(self):

    body = []

    while not self.check(

        TokenType.END,

        TokenType.EOF

    ):

        body.append(

            self.parse_statement()

        )

    self.consume(

        TokenType.END,

        "Expected 'end'."

    )

    #return ast.DoStatement(body)
    
# =====================================================
# EXPRESSIONS
# =====================================================

    def parse_expression(self):
        """
        Punto de entrada para analizar expresiones.

        La precedencia se resolverá descendiendo por
        diferentes niveles.
        """

        return self.parse_or()


    def parse_primary(self):
        """
        Expresiones básicas.
        """

        #
        # Number
        #

        if self.match(TokenType.NUMBER):

            return self.finish_postfix(
                ast.NumberLiteral(
                    float(self.previous.value)
                )
            )

        #
        # String
        #

        if self.match(TokenType.STRING):

            return self.finish_postfix(
                ast.StringLiteral(
                    self.previous.value
                )
            )

        #
        # true
        #

        if self.match(TokenType.TRUE):

            return self.finish_postfix(
                ast.BooleanLiteral(True)
            )

        #
        # false
        #

        if self.match(TokenType.FALSE):

            return self.finish_postfix(
                ast.BooleanLiteral(False)
            )

        #
        # nil
        #

        if self.match(TokenType.NIL):

            return self.finish_postfix(
                ast.NilLiteral()
            )

        #
        # (...)
        #

        if self.match(TokenType.LEFT_PAREN):

            expr = self.parse_assignable()

            self.consume(
                TokenType.RIGHT_PAREN,
                "Expected ')'."
            )
            
            return self.finish_postfix(

                ast.ParenthesizedExpression(
                    expr
                )

            )

        #
        # VarArg
        #

        if self.match(TokenType.VARARG):

            return self.finish_postfix(

                ast.VarArgExpression()

            )

        #
        # Identifier
        #

        if self.match(TokenType.IDENTIFIER):

            return self.finish_postfix(

                ast.Identifier(

                    self.previous.value

                )

            )

        #
        # Table
        #

        if self.check(TokenType.LEFT_BRACE):

            return self.finish_postfix(
                self.parse_table()
            )

        self.error(
            "Expected expression."
        )

# =====================================================
# TABLE
# =====================================================

    def parse_table(self):

        self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{'."
        )

        values = []

        while not self.check(TokenType.RIGHT_BRACE):

            values.append(

                self.parse_assignable()

            )

            if not self.match(
                TokenType.COMMA,
                TokenType.SEMICOLON
            ):
                break

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}'."
        )

        return ast.TableExpression(values)
    
    # =====================================================
    # EXPRESSION / ASSIGNMENT
    # =====================================================

    def parse_expression_statement(self):

        expr = self.parse_assignable()

        #
        # Assignment
        #

        if self.check(TokenType.ASSIGN):

            return self.parse_assignment(expr)

        return ast.ExpressionStatement(expr)
    
    # =====================================================
    # PRECEDENCE
    # =====================================================

    def parse_or(self):

        expr = self.parse_and()

        while self.match(TokenType.OR):

            operator = self.previous

            right = self.parse_and()

            expr = ast.BinaryExpression(
                left=expr,
                operator=operator.value,
                right=right
            )

        return expr


    def parse_and(self):

        expr = self.parse_compare()

        while self.match(TokenType.AND):

            operator = self.previous

            right = self.parse_compare()

            expr = ast.BinaryExpression(
                left=expr,
                operator=operator.value,
                right=right
            )

        return expr
    
    def parse_compare(self):

        expr = self.parse_concat()

        while self.match(

            TokenType.EQUAL,

            TokenType.NOT_EQUAL,

            TokenType.LESS,

            TokenType.LESS_EQUAL,

            TokenType.GREATER,

            TokenType.GREATER_EQUAL

        ):

            operator = self.previous

            right = self.parse_concat()

            expr = ast.BinaryExpression(

                left=expr,

                operator=operator.value,

                right=right

            )

        return expr
    
    def parse_concat(self):

        expr = self.parse_term()

        while self.match(TokenType.CONCAT):

            operator = self.previous

            right = self.parse_term()

            expr = ast.BinaryExpression(

                left=expr,

                operator=operator.value,

                right=right

            )

        return expr
    
    def parse_term(self):

        expr = self.parse_factor()

        while self.match(

            TokenType.PLUS,

            TokenType.MINUS

        ):

            operator = self.previous

            right = self.parse_factor()

            expr = ast.BinaryExpression(

                left=expr,

                operator=operator.value,

                right=right

            )

        return expr
    
    def parse_factor(self):

        expr = self.parse_unary()

        while self.match(

            TokenType.MULTIPLY,

            TokenType.DIVIDE,

            TokenType.MODULO

        ):

            operator = self.previous

            right = self.parse_unary()

            expr = ast.BinaryExpression(

                left=expr,

                operator=operator.value,

                right=right

            )

        return expr
    
    # =====================================================
    # UNARY
    # =====================================================

    def parse_unary(self):

        if self.match(

            TokenType.NOT,

            TokenType.MINUS,

            TokenType.LENGTH

        ):

            operator = self.previous

            operand = self.parse_unary()

            return ast.UnaryExpression(

                operator=operator.value,

                operand=operand

            )

        return self.parse_power()
    
    # =====================================================
    # POWER
    # =====================================================

    def parse_power(self):

        expr = self.parse_primary()

        #
        # Lua hace la potencia asociativa por la derecha.
        #
        # 2^3^4
        #
        # =>
        #
        # 2^(3^4)
        #

        if self.match(TokenType.POWER):

            operator = self.previous

            right = self.parse_power()

            expr = ast.BinaryExpression(

                left=expr,

                operator=operator.value,

                right=right

            )

        return expr

# =====================================================
# POSTFIX
# =====================================================

def finish_postfix(self, expr):

    while True:

        #
        # obj.member
        #

        if self.match(TokenType.DOT):

            name = self.consume(

                TokenType.IDENTIFIER,

                "Expected member name."

            )

            expr = ast.MemberExpression(

                object=expr,

                member=name.value

            )

            continue

        #
        # obj[index]
        #

        if self.match(TokenType.LEFT_BRACKET):

            index = self.parse_assignable()

            self.consume(

                TokenType.RIGHT_BRACKET,

                "Expected ']'."

            )

            expr = ast.IndexExpression(

                object=expr,

                index=index

            )

            continue

        #
        # method
        #

        if self.match(TokenType.COLON):

            method = self.consume(

                TokenType.IDENTIFIER,

                "Expected method."

            )

            arguments = self.parse_arguments()

            expr = ast.MethodCallExpression(

                object=expr,

                method=method.value,

                arguments=arguments

            )

            continue

        #
        # function(...)
        #

        if (

            self.check(TokenType.LEFT_PAREN)

            or

            self.check(TokenType.LEFT_BRACE)

            or

            self.check(TokenType.STRING)

        ):

            arguments = self.parse_arguments()

            expr = ast.CallExpression(

                callee=expr,

                arguments=arguments

            )

            continue

        break

    return expr

# =====================================================
# ARGUMENTS
# =====================================================

def parse_arguments(self):

    #
    # (...)
    #

    if self.match(TokenType.LEFT_PAREN):

        args = []

        if not self.check(TokenType.RIGHT_PAREN):

            while True:

                args.append(

                    self.parse_assignable()

                )

                if not self.match(TokenType.COMMA):

                    break

        self.consume(

            TokenType.RIGHT_PAREN,

            "Expected ')'."

        )

        return args

    #
    # table constructor
    #

    if self.check(TokenType.LEFT_BRACE):

        return [

            self.parse_table()

        ]

    #
    # string literal
    #

    if self.match(TokenType.STRING):

        return [

            ast.StringLiteral(

                self.previous.value

            )

        ]

    self.error(

        "Expected function arguments."

    )

# =====================================================
# ASSIGNMENT LIST
# =====================================================

def parse_assignment(self, first_target):

    targets = [first_target]

    #
    # a,b,c =
    #

    while self.match(TokenType.COMMA):

        targets.append(

            self.parse_assignable()

        )

    self.consume(

        TokenType.ASSIGN,

        "Expected '='."

    )

    values = [

        self.parse_assignable()

    ]

    while self.match(TokenType.COMMA):

        values.append(

            self.parse_assignable()

        )

    return ast.Assignment(

        targets=targets,

        values=values

    )

# =====================================================
# PARAMETERS
# =====================================================

def parse_parameter_list(self):

    params = []

    self.consume(

        TokenType.LEFT_PAREN,

        "Expected '('."

    )

    if not self.check(TokenType.RIGHT_PAREN):

        while True:

            if self.match(TokenType.VARARG):

                params.append(

                    ast.VarArgExpression()

                )

                break

            token = self.consume(

                TokenType.IDENTIFIER,

                "Expected parameter."

            )

            params.append(

                ast.Identifier(

                    token.value

                )

            )

            if not self.match(TokenType.COMMA):

                break

    self.consume(

        TokenType.RIGHT_PAREN,

        "Expected ')'."

    )

    return params

# =====================================================
# FUNCTION BODY
# =====================================================

def parse_function_body(self):

    params = self.parse_parameter_list()

    body = []

    while not self.check(

        TokenType.END,

        TokenType.EOF

    ):

        body.append(

            self.parse_statement()

        )

    self.consume(

        TokenType.END,

        "Expected 'end'."

    )

    return params, body

# =====================================================
# LOCAL FUNCTION
# =====================================================

def parse_local_function(self):

    token = self.consume(

        TokenType.IDENTIFIER,

        "Expected function name."

    )

    params, body = self.parse_function_body()

    return ast.FunctionDeclaration(

        name=ast.Identifier(token.value),

        parameters=params,

        body=body,

        local=True

    )

# =====================================================
# FUNCTION
# =====================================================

def parse_function_declaration(self):

    token = self.consume(

        TokenType.IDENTIFIER,

        "Expected function name."

    )

    params, body = self.parse_function_body()

    return ast.FunctionDeclaration(

        name=ast.Identifier(token.value),

        parameters=params,

        body=body,

        local=False

    )

# =====================================================
# IF
# =====================================================

def parse_if(self):

    condition = self.parse_expression()

    self.consume(
        TokenType.THEN,
        "Expected 'then'."
    )

    body = []

    while not self.check(
        TokenType.ELSE,
        TokenType.ELSEIF,
        TokenType.END,
        TokenType.EOF
    ):

        body.append(
            self.parse_statement()
        )

    elseif_blocks = []

    while self.match(TokenType.ELSEIF):

        expr = self.parse_expression()

        self.consume(
            TokenType.THEN,
            "Expected 'then'."
        )

        block = []

        while not self.check(
            TokenType.ELSEIF,
            TokenType.ELSE,
            TokenType.END,
            TokenType.EOF
        ):

            block.append(
                self.parse_statement()
            )

        elseif_blocks.append(
            (
                expr,
                block
            )
        )

    else_body = []

    if self.match(TokenType.ELSE):

        while not self.check(
            TokenType.END,
            TokenType.EOF
        ):

            else_body.append(
                self.parse_statement()
            )

    self.consume(
        TokenType.END,
        "Expected 'end'."
    )

    return ast.IfStatement(

        condition=condition,

        body=body,

        elseif_blocks=elseif_blocks,

        else_body=else_body

    )

# =====================================================
# WHILE
# =====================================================

def parse_while(self):

    condition = self.parse_expression()

    self.consume(
        TokenType.DO,
        "Expected 'do'."
    )

    body = []

    while not self.check(
        TokenType.END,
        TokenType.EOF
    ):

        body.append(
            self.parse_statement()
        )

    self.consume(
        TokenType.END,
        "Expected 'end'."
    )

    return ast.WhileStatement(

        condition=condition,

        body=body

    )

# =====================================================
# REPEAT
# =====================================================

def parse_repeat(self):

    body = []

    while not self.check(
        TokenType.UNTIL,
        TokenType.EOF
    ):

        body.append(
            self.parse_statement()
        )

    self.consume(
        TokenType.UNTIL,
        "Expected 'until'."
    )

    condition = self.parse_expression()

    return ast.RepeatStatement(

        body=body,

        condition=condition

    )

# =====================================================
# FOR
# =====================================================

def parse_for(self):

    name = self.consume(

        TokenType.IDENTIFIER,

        "Expected identifier."

    )

    #
    # Numeric
    #

    if self.match(TokenType.ASSIGN):

        return self.parse_numeric_for(name)

    #
    # Generic
    #

    return self.parse_generic_for(name)

# =====================================================
# NUMERIC FOR
# =====================================================

def parse_numeric_for(self, token):

    start = self.parse_expression()

    self.consume(
        TokenType.COMMA,
        "Expected ','."
    )

    finish = self.parse_expression()

    step = None

    if self.match(TokenType.COMMA):

        step = self.parse_expression()

    self.consume(
        TokenType.DO,
        "Expected 'do'."
    )

    body = []

    while not self.check(
        TokenType.END,
        TokenType.EOF
    ):

        body.append(
            self.parse_statement()
        )

    self.consume(
        TokenType.END,
        "Expected 'end'."
    )

    return ast.ForNumeric(

        variable=ast.Identifier(
            token.value
        ),

        start=start,

        finish=finish,

        step=step,

        body=body

    )

# =====================================================
# GENERIC FOR
# =====================================================

def parse_generic_for(self, token):

    variables = [

        ast.Identifier(
            token.value
        )

    ]

    while self.match(TokenType.COMMA):

        tok = self.consume(

            TokenType.IDENTIFIER,

            "Expected identifier."

        )

        variables.append(

            ast.Identifier(
                tok.value
            )

        )

    self.consume(
        TokenType.IN,
        "Expected 'in'."
    )

    iterator = [

        self.parse_expression()

    ]

    while self.match(TokenType.COMMA):

        iterator.append(

            self.parse_expression()

        )

    self.consume(
        TokenType.DO,
        "Expected 'do'."
    )

    body = []

    while not self.check(
        TokenType.END,
        TokenType.EOF
    ):

        body.append(

            self.parse_statement()

        )

    self.consume(
        TokenType.END,
        "Expected 'end'."
    )

    return ast.ForGeneric(

        variables=variables,

        iterator=iterator,

        body=body

    )

