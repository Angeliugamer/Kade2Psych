# Kade2Psych Compiler Checklist

---

# FRONTEND
## AST

- [x] Node
- [x] Statement
- [x] Expression
- [x] Program

### Literals
- [x] NumberLiteral
- [x] StringLiteral
- [x] BooleanLiteral
- [x] NilLiteral
- [x] VarArgExpression

### Expressions
- [x] Identifier
- [x] BinaryExpression
- [x] UnaryExpression
- [x] CallExpression
- [x] MemberExpression
- [x] IndexExpression
- [x] MethodCallExpression
- [x] ParenthesizedExpression
- [x] TableExpression

### Statements
- [x] Assignment
- [x] Return
- [x] LocalStatement
- [x] ExpressionStatement

### Control Flow
- [x] If
- [x] While
- [x] Repeat
- [x] ForNumeric
- [x] ForGeneric

### Functions
- [x] FunctionDeclaration
- [x] AnonymousFunction

---

## Lexer
### Tokens
- [x] Keywords
- [x] Numbers
- [x] Strings
- [x] Identifiers
- [x] Operators
- [x] Separators
- [x] VarArg (...)

### Features
- [x] Comments
- [x] Long Strings
- [ ] Hex Numbers
- [ ] Scientific Numbers

---

## Parser
### Expressions
- [x] Literals
- [x] Unary
- [x] Binary
- [x] Tables
- [x] Function Calls
- [x] Method Calls
- [x] Member Access
- [x] Index Access

### Statements
- [x] Assignment
- [ ] Local
- [ ] Return
- [ ] Break
- [ ] Do
- [ ] While
- [ ] Repeat
- [ ] If
- [ ] Numeric For
- [ ] Generic For
- [ ] Function Declaration

---

# MIDDLE END
## Semantic Analysis
- [ ] Scope Resolution
- [ ] Symbol Table
- [ ] Type Checking
- [ ] Constant Folding

## Transformer
- [ ] me{}
- [ ] set{}
- [ ] ease{}
- [ ] mpf{}
- [ ] definemod{}
- [ ] func{}
- [ ] easefunc{}

## IR
- [ ] Intermediate Representation
- [ ] Optimization

---

# BACKEND
## Psych Engine
- [ ] Modifiers
- [ ] Tweens
- [ ] Events
- [ ] Camera
- [ ] Notes
- [ ] Shader Calls

---

# OUTPUT
## Generator
- [ ] Lua Writer
- [ ] Pretty Printer
- [ ] Formatting

---

# TESTS
- [ ] Lexer
- [ ] Parser
- [ ] Transformer
- [ ] Backend
- [ ] Full Modchart Conversion
