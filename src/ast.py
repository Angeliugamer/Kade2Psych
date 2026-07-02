"""
=========================================================
Kade2Psych AST
---------------------------------------------------------
Abstract Syntax Tree para Kade2Psych.

Este archivo define la estructura base utilizada por el
parser para representar código Lua antes de convertirlo
a instrucciones específicas de Kade Engine.

Todas las clases del compilador heredan de Node.

Author:
    ChatGPT + Angeliu Gamer
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# =========================================================
# BASE NODES
# =========================================================

class Node:
    """
    Nodo base del AST.

    Todos los nodos heredan de esta clase.
    """

    pass


class Statement(Node):
    """
    Nodo que representa una instrucción.

    Ejemplos:

        local x = 5

        return x

        if a then

        while true do
    """

    pass


class Expression(Node):
    """
    Nodo que representa una expresión.

    Ejemplos:

        5

        "hola"

        beat + 2

        math.sin(x)

        me{...}
    """

    pass

# =========================================================
# ROOT
# =========================================================

@dataclass(slots=True)
class Program(Node):
    """
    Nodo raíz.

    Representa un archivo Lua completo.
    """

    body: List[Statement] = field(default_factory=list)

    def append(self, node: Statement):
        self.body.append(node)

    def extend(self, nodes: List[Statement]):
        self.body.extend(nodes)

    def __iter__(self):
        return iter(self.body)

    def __len__(self):
        return len(self.body)

    def __getitem__(self, index):
        return self.body[index]

# =========================================================
# PLACEHOLDER
# =========================================================

@dataclass(slots=True)
class EmptyStatement(Statement):
    """
    Sentencia vacía.

    Se usa temporalmente por el parser cuando necesita
    reservar un nodo.
    """

    pass

# =========================================================
# EXPRESSIONS
# =========================================================

class Literal(Expression):
    """
    Clase base para todos los literales.
    """

    pass

# =========================================================
# LITERALS
# =========================================================

@dataclass(slots=True)
class NumberLiteral(Literal):
    
    value: float


@dataclass(slots=True)
class StringLiteral(Literal):

    value: str


@dataclass(slots=True)
class BooleanLiteral(Literal):

    value: bool


@dataclass(slots=True)
class NilLiteral(Literal):
    """
    Representa el valor 'nil' de Lua.
    """

    pass

# =========================================================
# VARARGS
# =========================================================

@dataclass(slots=True)
class VarArgExpression(Expression):
    """
    Representa el operador "..." de Lua.
    """

    pass

# =========================================================
# PARENTHESIZED EXPRESSION
# =========================================================

@dataclass(slots=True)
class ParenthesizedExpression(Expression):
    """
    Conserva los paréntesis originales del código.

    Aunque semánticamente "(a+b)" sea igual a "a+b",
    este nodo permite reconstruir exactamente el código
    fuente si es necesario.
    """

    expression: Expression

# =========================================================
# IDENTIFIER
# =========================================================

@dataclass(slots=True)
class Identifier(Expression):

    name: str

# =========================================================
# UNARY
# =========================================================

@dataclass(slots=True)
class UnaryExpression(Expression):
    """
    Ejemplo:

        -x

        not alive

        #table
    """

    operator: str

    operand: Expression

# =========================================================
# BINARY
# =========================================================

@dataclass(slots=True)
class BinaryExpression(Expression):
    """
    Ejemplo:

        a+b

        x*y

        beat>32

        a and b
    """

    operator: str

    left: Expression

    right: Expression

# =========================================================
# MEMBER ACCESS
# =========================================================

@dataclass(slots=True)
class MemberExpression(Expression):
    """
    obj.member
    """

    object: Expression

    member: str

# =========================================================
# INDEX ACCESS
# =========================================================

@dataclass(slots=True)
class IndexExpression(Expression):
    """
    obj[index]
    """

    object: Expression

    index: Expression

# =========================================================
# FUNCTION CALL
# =========================================================

@dataclass(slots=True)
class CallExpression(Expression):
    """
    func(a,b,c)
    """

    function: Expression

    arguments: List[Expression] = field(default_factory=list)

# =========================================================
# TABLES
# =========================================================

@dataclass(slots=True)
class TableField(Node):
    """
    Campo individual de una tabla.

    Puede representar:

        value

        key=value

        [expr]=value
    """

    key: Optional[Expression]

    value: Expression


@dataclass(slots=True)
class TableExpression(Expression):
    """
    Constructor de tablas de Lua.

    {

        1,

        2,

        a=5,

        [x]=8

    }
    """

    fields: List[TableField] = field(default_factory=list)

# =========================================================
# STATEMENTS
# =========================================================

@dataclass(slots=True)
class ExpressionStatement(Statement):
    """
    Una expresión utilizada como sentencia.

    Ejemplos:

        print("Hola")

        me{...}

        math.sin(x)
    """

    expression: Expression

# =========================================================
# ASSIGNMENT
# =========================================================

@dataclass(slots=True)
class Assignment(Statement):
    """
    Asignación.

    Puede representar:

        a = 1

        a,b = 1,2

        obj.x = 5

        tbl[index] = value
    """

    targets: List[Expression] = field(default_factory=list)

    values: List[Expression] = field(default_factory=list)

# =========================================================
# LOCAL ASSIGNMENT
# =========================================================

@dataclass(slots=True)
class LocalStatement(Statement):
    """
    Asignación local.

    Ejemplos:

        local x = 5

        local a,b = 1,2

        local beat
    """

    names: List[str] = field(default_factory=list)

    values: List[Expression] = field(default_factory=list)

# =========================================================
# RETURN
# =========================================================

@dataclass(slots=True)
class ReturnStatement(Statement):
    """
    return

    return x

    return a,b,c
    """

    values: List[Expression] = field(default_factory=list)

# =========================================================
# BREAK
# =========================================================

@dataclass(slots=True)
class BreakStatement(Statement):
    """
    break
    """

    pass

# =========================================================
# DO STATEMENT
# =========================================================

@dataclass(slots=True)
class DoStatement(Statement):
    """
    Representa un bloque:

    do
        ...
    end
    """

    body: List[Statement] = field(default_factory=list)

# =========================================================
# CONTINUE
# =========================================================

@dataclass(slots=True)
class ContinueStatement(Statement):
    """
    continue

    No existe en Lua estándar, pero algunos motores
    implementan un comportamiento equivalente.
    """

    pass

# =========================================================
# CONTROL FLOW
# =========================================================

@dataclass(slots=True)
class IfBranch(Node):
    """
    Rama individual de un if.

    Representa:

        if cond then

        elseif cond then
    """

    condition: Expression

    body: List[Statement] = field(default_factory=list)


@dataclass(slots=True)
class IfStatement(Statement):
    """
    Sentencia if.

    Puede representar:

        if ... then

        elseif ...

        else
    """

    branches: List[IfBranch] = field(default_factory=list)

    else_body: List[Statement] = field(default_factory=list)

# =========================================================
# WHILE
# =========================================================

@dataclass(slots=True)
class WhileStatement(Statement):
    """
    while condition do
        ...
    end
    """

    condition: Expression

    body: List[Statement] = field(default_factory=list)

# =========================================================
# REPEAT
# =========================================================

@dataclass(slots=True)
class RepeatStatement(Statement):
    """
    repeat
        ...
    until condition
    """

    body: List[Statement] = field(default_factory=list)

    condition: Expression = None

# =========================================================
# NUMERIC FOR
# =========================================================

@dataclass(slots=True)
class ForNumericStatement(Statement):
    """
    for i = start,end,step do
        ...
    end
    """

    variable: Identifier

    start: Expression

    end: Expression

    step: Expression | None = None

    body: List[Statement] = field(default_factory=list)

# =========================================================
# GENERIC FOR
# =========================================================

@dataclass(slots=True)
class ForGenericStatement(Statement):
    """
    for k,v in pairs(tbl) do
        ...
    end
    """

    variables: List[Identifier] = field(default_factory=list)

    iterators: List[Expression] = field(default_factory=list)

    body: List[Statement] = field(default_factory=list)

# =========================================================
# FUNCTIONS
# =========================================================

@dataclass(slots=True)
class Parameter(Node):
    """
    Parámetro de una función.

    Ejemplos:

        function(a,b,c)

        function(...)
    """

    name: str

    vararg: bool = False

# =========================================================
# FUNCTION BASE
# =========================================================

class FunctionBase(Expression):
    """
    Clase base para cualquier función.
    """

    pass

# =========================================================
# ANONYMOUS FUNCTION
# =========================================================

@dataclass(slots=True)
class AnonymousFunction(FunctionBase):
    """
    function(a,b)

    end
    """

    parameters: List[Parameter] = field(default_factory=list)

    body: List[Statement] = field(default_factory=list)

    vararg: bool = False

# =========================================================
# FUNCTION DECLARATION
# =========================================================

@dataclass(slots=True)
class FunctionDeclaration(Statement):
    """
    function name(...)

    end

    También soporta:

        function math.sin()

        function tbl:update()
    """

    name: Expression

    parameters: List[Parameter] = field(default_factory=list)

    body: List[Statement] = field(default_factory=list)

    local: bool = False

    vararg: bool = False

# =========================================================
# METHOD CALL
# =========================================================

@dataclass(slots=True)
class MethodCallExpression(Expression):
    """
    obj:method(a,b)

    Lua convierte internamente esto en

        obj.method(obj,a,b)
    """

    object: Expression

    method: str

    arguments: List[Expression] = field(default_factory=list)

# =========================================================
# MODULE
# =========================================================

@dataclass(slots=True)
class Module(Node):
    """
    Representa un archivo Lua completo.

    En el futuro permitirá almacenar:

    - nombre
    - imports
    - exports
    - comentarios
    - metadata
    """

    name: str = "<main>"

    program: Program = field(default_factory=Program)

    