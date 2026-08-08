# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from lexer import *
from typing import TypeAlias
from pathlib import Path
import reporter
from utils import TriBool

ANI: TypeAlias = int

class TypeKind(Enum):
   Bit8 = iota()
   Bit16 = iota()
   Bit32 = iota()
   Bit64 = iota()
   Class = iota()
   Procedure = iota()
   Pointer = iota()
   Count = reset()

TypeId: TypeAlias = int

class Type:
   kind: TypeKind

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      assert False, "Missing implementation for procedure display in one of the Type subclasses."

class TypeBit(Type):
   signed: bool

   def __init__(self, kind: TypeKind, signed: bool) -> None:
      self.kind = kind
      self.signed = signed

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}", end="")
      match self.kind:
         case TypeKind.Bit8:  print(f"Bit8 (signed={self.signed})");
         case TypeKind.Bit16: print(f"Bit16 (signed={self.signed})");
         case TypeKind.Bit32: print(f"Bit32 (signed={self.signed})");
         case TypeKind.Bit64: print(f"Bit64 (signed={self.signed})");
         case _:
            panic("unreachable")

class TypeClass(Type):
   kind = TypeKind.Class
   fields: list[TypeId]

   def __init__(self, fields: list[TypeId]) -> None:
      self.fields = fields

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Class")
      prefix += TreePrinter.last_to_prefix_append(last)
      for i, ani in enumerate(self.fields):
         ast.nodes[ani].display(ast, prefix, i + 1 >= len(self.fields))

class TypeProcedure(Type):
   kind = TypeKind.Procedure
   parameters: list[TypeId]
   returns: tuple[TypeId, TypeId]

   def __init__(self, parameters: list[TypeId], returns: tuple[TypeId, TypeId]) -> None:
      self.parameters = parameters
      self.returns = returns

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Class")
      prefix += TreePrinter.last_to_prefix_append(last)

      print(f"{prefix}├─Parameters")
      new_prefix: str = prefix + TreePrinter.last_to_prefix_append(False)
      for i, type_id in enumerate(self.parameters):
         ast.types[type_id].display(ast, new_prefix, i + 1 >= len(self.parameters))

      print(f"{prefix}└─Returns")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      if self.returns[0] > 0:
         ast.types[self.returns[0]].display(ast, new_prefix, self.returns[1] < 0)
      if self.returns[1] > 0:
         ast.types[self.returns[1]].display(ast, new_prefix, True)

class TypePointer(Type):
   kind = TypeKind.Pointer
   pointee: TypeId

   def __init__(self, pointee: TypeId) -> None:
      self.pointee = pointee

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Pointer")
      prefix += TreePrinter.last_to_prefix_append(last)
      ast.types[self.pointee].display(ast, prefix, True)

class SymbolKind(Enum):
   Variable = iota()
   Procedure = iota()
   Type = iota()
   Count = reset()

class Symbol:
   kind: SymbolKind
   type: TypeId

   def display(self, name: str, ast: "Ast", prefix: str, last: bool) -> None:
      assert False, "Missing implementation for procedure display in one of the Symbol subclasses."

class SymbolVariable(Symbol):
   kind = SymbolKind.Variable
   mutable: bool

   def __init__(self, type: TypeId, mutable: bool) -> None:
      self.type = type
      self.mutable = mutable

   def display(self, name: str, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{name}: Variable -> {self.type}")
      prefix += TreePrinter.last_to_prefix_append(last)
      print(f"{prefix}└─Mutable: {self.mutable}")

class SymbolProcedure(Symbol):
   kind = SymbolKind.Procedure

   def __init__(self, type: TypeId) -> None:
      self.type = type

   def display(self, name: str, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{name}: Procedure -> {self.type}")

class SymbolType(Symbol):
   kind = SymbolKind.Type

   def __init__(self, type: TypeId) -> None:
      self.type = type

   def display(self, name: str, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{name}: Type -> {self.type}")


class TreePrinter:
   @staticmethod
   def last_to_prefix_append(last: bool) -> str:
      if last:
         return "  "
      return "│ "

   @staticmethod
   def bool_to_connector(last: bool) -> str:
      if last:
         return "└─"
      return "├─"

class ParsingState:
   panic: bool
   failure: bool

   def __init__(self) -> None:
      self.panic = False
      self.failure = False

   def enter_panic(self) -> None:
      self.panic = True
      self.failure = True

   def exit_panic(self) -> None:
      self.panic = False

class Operator(Enum):
   Add = iota()
   Sub = iota()
   Mul = iota()
   Div = iota()
   Assign = iota()
   Access = iota()
   Count = reset()

   @staticmethod
   def try_parse_bin_op_token(kind: TokenKind) -> "Operator | None":
      assert Operator.Count.value == 6
      match kind:
         case TokenKind.Plus:   return Operator.Add
         case TokenKind.Minus:  return Operator.Sub
         case TokenKind.Star:   return Operator.Mul
         case TokenKind.Slash:  return Operator.Div
         case TokenKind.Equals: return Operator.Assign
         case TokenKind.Dot:    return Operator.Access
         case _: return None

   def to_str(self) -> str:
      assert Operator.Count.value == 6
      match self:
         case Operator.Add:    return "Add"
         case Operator.Sub:    return "Sub"
         case Operator.Mul:    return "Mul"
         case Operator.Div:    return "Div"
         case Operator.Assign: return "Assign"
         case Operator.Access: return "Access"
         case _:
            panic("unreachable")

   def precedence(self) -> int:
      assert Operator.Count.value == 6
      match self:
         case Operator.Access:             return 14
         case Operator.Mul | Operator.Div: return 12
         case Operator.Add | Operator.Sub: return 11
         case Operator.Assign:             return 1
         case _:
            panic("unreachable")

   def left_associative(self) -> bool:
      assert Operator.Count.value == 6
      match self:
         case Operator.Add:    return True
         case Operator.Sub:    return True
         case Operator.Mul:    return True
         case Operator.Div:    return True
         case Operator.Assign: return False
         case Operator.Access: return True
         case _:
            panic("unreachable")

   def is_binary(self) -> bool:
      assert Operator.Count.value == 6
      match self:
         case Operator.Mul:    return True
         case Operator.Add:    return True
         case Operator.Sub:    return True
         case Operator.Mul:    return True
         case Operator.Div:    return True
         case Operator.Assign: return True
         case Operator.Access: return True
         case _:
            panic("unreachable")

class AstNodeKind(Enum):
   # Declarations
   Module = iota()
   Class = iota()
   Procedure = iota()
   Parameter = iota()
   Variable = iota()
   Scope = iota()

   # Statements
   Return = iota()

   # Expressions
   BinOp = iota()
   ProcedureCall = iota()
   IntLiteral = iota()
   StrLiteral = iota()
   Identifier = iota()
   Count = reset()

class AstNode:
   kind: AstNodeKind

   @staticmethod
   def parse_atom(lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      token: Token = lexer.next()
      match token.kind:
         case TokenKind.IntLiteral:
            ast.nodes.append(AstIntLiteral(token))
            return len(ast.nodes) - 1

         case TokenKind.StrLiteral:
            ast.nodes.append(AstStrLiteral(token))
            return len(ast.nodes) - 1

         case TokenKind.Identifier:
            peek: Token = lexer.peek()
            if peek.kind != TokenKind.LParen:
               ast.nodes.append(AstIdentifier(token))
               return len(ast.nodes) - 1

            lexer.next()
            return AstProcedureCall.parse(token, lexer, ast, state)

         case _:
            state.enter_panic()
            reporter.unexpected_token(lexer.file_path, token, [])
            return -1

   @staticmethod
   def parse_expression(precedence: int, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      lhs: ANI = AstNode.parse_atom(lexer, ast, state)
      if lhs < 0: return lhs

      while True:
         token: Token = lexer.next()
         op: Operator | None = Operator.try_parse_bin_op_token(token.kind)
         if op is None or op.precedence() < precedence:
            lexer.undo(token)
            return lhs

         next_precedence: int = op.precedence()
         if op.left_associative():
            next_precedence += 1

         rhs: ANI = AstNode.parse_expression(next_precedence, lexer, ast, state)
         if op.is_binary():
            ast.nodes.append(AstBinOp(op, lhs, rhs))
            lhs = len(ast.nodes) - 1

   # This procedure may fail.
   # To check if this procedure failed, check [state] for panic mode
   @staticmethod
   def parse_code_block(current_indent: int, lexer: Lexer, ast: "Ast", state: ParsingState) -> list[ANI]:
      token: Token = lexer.peek()
      while token.kind == TokenKind.NewLine:
         lexer.next()
         token = lexer.peek()

      if token.kind == TokenKind.Eof:
         return []

      if token.indent <= current_indent:
         state.enter_panic()
         reporter.under_indent(lexer.file_path, token)
         return []

      indent_level: int = token.indent
      self: list[ANI] = []
      while True:
         token = lexer.next()
         if token.kind == TokenKind.NewLine: continue
         if token.kind == TokenKind.Eof: return self

         if token.indent <= current_indent:
            lexer.undo(token)
            return self

         if token.indent > indent_level:
            if not state.panic:
               state.enter_panic()
               reporter.over_indent(lexer.file_path, token)
            continue

         match token.kind:
            case TokenKind.Return:
               state.exit_panic()
               self.append(AstReturn.parse(lexer, ast, state))

            case TokenKind.Identifier:
               state.exit_panic()
               peek: Token = lexer.peek()
               if peek.kind == TokenKind.Colon:
                  lexer.next()
                  variable: ANI = AstVariable.parse(token, lexer, ast, state)
                  if variable >= 0:
                     self.append(variable)
               else:
                  lexer.undo(token)
                  self.append(AstNode.parse_expression(-1, lexer, ast, state))

            case TokenKind.Scope:
               state.exit_panic()
               scope: ANI = AstScope.parse(token.indent, lexer, ast, state)
               if scope >= 0:
                  self.append(scope)

            case TokenKind.IntLiteral | TokenKind.StrLiteral:
               lexer.undo(token)
               self.append(AstNode.parse_expression(-1, lexer, ast, state))

            case TokenKind.Pass:
               state.exit_panic()

            case _:
               if not state.panic:
                  state.enter_panic()
                  reporter.unexpected_token(lexer.file_path, token, [])

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      assert False, "Unimplemented base class"

class AstBinOp(AstNode):
   operator: Operator
   lhs: ANI
   rhs: ANI

   def __init__(self, operator: Operator, lhs: ANI, rhs: ANI) -> None:
      self.kind = AstNodeKind.BinOp
      self.operator = operator
      self.lhs = lhs
      self.rhs = rhs

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.operator.to_str()}")
      prefix += TreePrinter.last_to_prefix_append(last)
      ast.nodes[self.lhs].display(ast, prefix, False)
      ast.nodes[self.rhs].display(ast, prefix, True)

class AstProcedureCall(AstNode):
   procedure: Token
   parameters: list[ANI]

   def __init__(self, procedure: Token) -> None:
      assert procedure.kind == TokenKind.Identifier
      self.kind = AstNodeKind.ProcedureCall
      self.procedure = procedure
      self.parameters = []

   # Expects that the procedure name and the LParen part of the procedure call syntax has already been parsed.
   @staticmethod
   def parse(procedure: Token, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstProcedureCall(procedure)

      while True:
         self.parameters.append(AstNode.parse_expression(-1, lexer, ast, state))
         token: Token = lexer.next()

         match token.kind:
            case TokenKind.RParen:
               state.exit_panic()
               ast.nodes.append(self)
               return len(ast.nodes) - 1

            case TokenKind.Comma:
               pass

            case _:
               if not state.panic:
                  state.enter_panic()
                  reporter.unexpected_token(lexer.file_path, token, [TokenKind.Comma, TokenKind.RParen])

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.procedure.str_literal}")
      prefix += TreePrinter.last_to_prefix_append(last)
      for i, ani in enumerate(self.parameters):
         ast.nodes[ani].display(ast, prefix, i + 1 >= len(self.parameters))

class AstIdentifier(AstNode):
   value: Token

   def __init__(self, value: Token) -> None:
      assert value.kind == TokenKind.Identifier
      self.kind = AstNodeKind.Identifier
      self.value = value

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.value.str_literal}")

class AstStrLiteral(AstNode):
   value: Token

   def __init__(self, value: Token) -> None:
      assert value.kind == TokenKind.StrLiteral
      self.kind = AstNodeKind.StrLiteral
      self.value = value

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.value.str_literal}")

class AstIntLiteral(AstNode):
   value: Token

   def __init__(self, value: Token) -> None:
      assert value.kind == TokenKind.IntLiteral
      self.kind = AstNodeKind.IntLiteral
      self.value = value

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.value.int_literal}")

class AstVariable(AstNode):
   kind: AstNodeKind = AstNodeKind.Variable
   name: Token
   type: Token | str | None # Explicit type | inferred type | implicit type before inference
   expression: ANI

   # Expects that the name and type colon part of the variable declaration syntax has already been parsed
   @staticmethod
   def parse(name: Token, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstVariable()
      self.name = name
      self.expression = -1
      mutable = False

      token: Token = lexer.next()
      match token.kind:
         case TokenKind.Identifier:
            self.type = token
            token = lexer.next()
            match token.kind:
               case TokenKind.NewLine: pass
               case TokenKind.Equals | TokenKind.Colon:
                  self.expression = AstNode.parse_expression(-1, lexer, ast, state)
                  mutable = token.kind == TokenKind.Equals

               case _:
                  state.enter_panic()
                  reporter.unexpected_token(lexer.file_path, token, [TokenKind.Equals, TokenKind.Colon, TokenKind.NewLine])
                  return -1

         case TokenKind.Equals | TokenKind.Colon:
            mutable = token.kind == TokenKind.Equals
            self.type = None
            self.expression = AstNode.parse_expression(-1, lexer, ast, state)

         case _:
            state.enter_panic()
            reporter.unexpected_token(lexer.file_path, token, [TokenKind.Identifier, TokenKind.Equals])
            return -1

      ast.scope_stack[len(ast.scope_stack) - 1][self.name.str_literal] = SymbolVariable(0, mutable)
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.name.str_literal}: ", end="")
      if isinstance(self.type, Token): print(self.type.str_literal)
      elif isinstance(self.type, str): print(self.type)
      else:                            print("@infer")
      prefix += TreePrinter.last_to_prefix_append(last)
      if self.expression >= 0:
         ast.nodes[self.expression].display(ast, prefix, True)

class AstReturn(AstNode):
   expression: ANI

   def __init__(self, expression: ANI) -> None:
      self.expression = expression
      self.kind = AstNodeKind.Return

   @staticmethod
   def parse(lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstReturn(AstNode.parse_expression(-1, lexer, ast, state))
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Return")
      prefix += TreePrinter.last_to_prefix_append(last)
      if self.expression >= 0:
         ast.nodes[self.expression].display(ast, prefix, True)

class AstParameter(AstNode):
   name: Token
   type: Token | None # Type | Inferred Self type

   def __init__(self, name: Token, type: Token | None) -> None:
      self.name = name
      self.type = type
      self.kind = AstNodeKind.Parameter

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      if self.type is None:
         print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.name.str_literal}: Self")
      else:
         print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.name.str_literal}: {self.type.str_literal}")

class AstScope(AstNode):
   kind: AstNodeKind = AstNodeKind.Scope
   name: Token | None
   body: list[ANI]
   scope: dict[str, Symbol]

   @staticmethod
   def parse(current_indent: int, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstScope()
      self.scope = {}
      ast.scope_stack.append(self.scope)
      token: Token = lexer.next()

      match token.kind:
         case TokenKind.StrLiteral:
            self.name = token
            token = lexer.next()
            if token.kind != TokenKind.Colon:
               state.enter_panic()
               reporter.unexpected_token(lexer.file_path, token, [TokenKind.Colon])
               ast.scope_stack.pop()
               return -1

            self.body = AstNode.parse_code_block(current_indent, lexer, ast, state)

         case TokenKind.Colon:
            self.name = None
            self.body = AstNode.parse_code_block(current_indent, lexer, ast, state)

         case _:
            state.enter_panic()
            reporter.unexpected_token(lexer.file_path, token, [TokenKind.StrLiteral, TokenKind.Colon])
            ast.scope_stack.pop()
            return -1

      ast.scope_stack.pop()
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Scope", end="")
      if self.name is not None:
         print(f": {self.name.str_literal}")
      else:
         print("")
      prefix += TreePrinter.last_to_prefix_append(last)

      new_prefix: str = prefix + TreePrinter.last_to_prefix_append(False)
      print(f"{prefix}├─Scope")
      for i, (name, symbol) in enumerate(self.scope.items()):
         symbol.display(name, ast, new_prefix, i + 1 >= len(self.scope.items()))

      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      print(f"{prefix}└─Body")
      for i, ani in enumerate(self.body):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.body))

class AstClass(AstNode):
   kind: AstNodeKind = AstNodeKind.Class
   name: Token
   fields: list[ANI]
   methods: list[ANI]
   scope: dict[str, Symbol]

   @staticmethod
   def parse(current_indent: int, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstClass()
      self.name = lexer.next()
      self.fields = []
      self.methods = []
      self.scope = {}

      if self.name.kind != TokenKind.Identifier:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, self.name, [TokenKind.Identifier])
         return -1

      token: Token = lexer.next()
      if token.kind != TokenKind.Colon:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, self.name, [TokenKind.Colon])
         return -1

      token = lexer.peek()
      while token.kind == TokenKind.NewLine:
         lexer.next()
         token = lexer.peek()
      indent_level: int = token.indent
      ast.scope_stack.append(self.scope)

      while True:
         token = lexer.next()

         if token.kind == TokenKind.Eof: break
         if token.kind == TokenKind.NewLine: continue

         if token.indent <= current_indent:
            lexer.undo(token)
            break

         if token.indent > indent_level:
            if not state.panic:
               state.enter_panic()
               reporter.unexpected_token(lexer.file_path, token, [])
            continue

         match token.kind:
            case TokenKind.Identifier:
               lexer.next_and_expect(state, [TokenKind.Colon])
               if state.panic: continue
               field_type: Token = lexer.next_and_expect(state, [TokenKind.Identifier])
               if state.panic: continue
               param = AstParameter(token, field_type)
               ast.nodes.append(param)
               # Todo: Actually set the type of the parameter
               self.scope[param.name.str_literal] = SymbolVariable(0, True)
               self.fields.append(len(ast.nodes) - 1)

            case TokenKind.Def:
               proc: ANI = AstProcedure.parse(token.indent, lexer, ast, state, in_class=True)
               if proc >= 0:
                  self.methods.append(proc)

            case _:
               if not state.panic:
                  state.enter_panic()
                  reporter.unexpected_token(lexer.file_path, token, [])
               ast.scope_stack.pop()
               return -1

      ast.scope_stack.pop()
      # Todo: Actually set the type of the class
      ast.scope_stack[len(ast.scope_stack) - 1][self.name.str_literal] = SymbolType(0)
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Class: {self.name.str_literal}")
      prefix += TreePrinter.last_to_prefix_append(last)

      new_prefix: str = prefix + TreePrinter.last_to_prefix_append(False)
      print(f"{prefix}├─Scope")
      for i, (name, symbol) in enumerate(self.scope.items()):
         symbol.display(name, ast, new_prefix, i + 1 >= len(self.scope.items()))

      print(f"{prefix}├─Fields")
      for i, ani in enumerate(self.fields):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.fields))

      print(f"{prefix}└─Methods")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      for i, ani in enumerate(self.methods):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.methods))

class AstProcedure(AstNode):
   kind = AstNodeKind.Procedure
   name: Token
   parameter_types: list[ANI]
   return_types: list[Token]
   body: list[ANI]
   scope: dict[str, Symbol]

   def __init__(self, name: Token) -> None:
      self.name = name
      self.parameter_types = []
      self.return_types = []
      self.body = []
      self.scope = {}

   @staticmethod
   def parse(current_indent: int, lexer: Lexer, ast: "Ast", state: ParsingState, in_class: bool = False) -> ANI:
      self = AstProcedure(lexer.next())
      if self.name.kind != TokenKind.Identifier:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, self.name, [TokenKind.Identifier])
         return -1

      token: Token = lexer.next()
      if token.kind != TokenKind.LParen:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, token, [TokenKind.LParen])
         return -1

      ast.scope_stack.append(self.scope)
      expected: list[TokenKind] = [TokenKind.Identifier, TokenKind.RParen]

      # False is for the parameter name
      # True is for the parameter type
      # Neutral is for the return type
      identifier_as_type: TriBool = TriBool.false
      parameter_name: Token = Token()
      colon_as_end: bool = False

      while True:
         token = lexer.next()

         if token.kind == TokenKind.NewLine:
            continue

         if not expected.__contains__(token.kind):
            state.enter_panic()
            reporter.unexpected_token(lexer.file_path, token, expected)
            ast.scope_stack.pop()
            return -1

         match token.kind:
            case TokenKind.Identifier:
               match identifier_as_type:
                  case TriBool.false:
                     parameter_name = token
                     expected = [TokenKind.Colon]
                     if in_class and parameter_name.str_literal == "self":
                        self.parameter_types.append(len(ast.nodes))
                        param = AstParameter(parameter_name, None)
                        ast.nodes.append(param)
                        # Todo: Actually set the type of the parameter
                        self.scope[param.name.str_literal] = SymbolVariable(0, True)
                        expected = [TokenKind.Comma, TokenKind.RParen]
                        identifier_as_type = TriBool.neutral

                  case TriBool.true:
                     self.parameter_types.append(len(ast.nodes))
                     param = AstParameter(parameter_name, token)
                     ast.nodes.append(param)
                     # Todo: Actually set the type of the parameter.
                     self.scope[param.name.str_literal] = SymbolVariable(0, True)
                     expected = [TokenKind.Comma, TokenKind.RParen]

                  case TriBool.neutral:
                     self.return_types.append(token)
                     expected = [TokenKind.Colon]

            case TokenKind.RParen:
               expected = [TokenKind.Colon, TokenKind.Arrow]
               colon_as_end = True

            case TokenKind.Arrow:
               expected = [TokenKind.Identifier]
               identifier_as_type = TriBool.neutral

            case TokenKind.Colon:
               if colon_as_end:
                  self.body = self.parse_code_block(current_indent, lexer, ast, state)
                  break
               expected = [TokenKind.Identifier]
               identifier_as_type = TriBool.true

            case TokenKind.Comma:
               expected = [TokenKind.Identifier]
               identifier_as_type = TriBool.false

            case _:
               panic("unreachable")

      ast.scope_stack.pop()
      # Todo: Actually set the type of the procedure
      ast.scope_stack[len(ast.scope_stack) - 1][self.name.str_literal] = SymbolProcedure(0)
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Procedure: {self.name.str_literal}")
      prefix += TreePrinter.last_to_prefix_append(last)

      new_prefix: str = prefix + TreePrinter.last_to_prefix_append(False)
      print(f"{prefix}├─Scope")
      for i, (name, symbol) in enumerate(self.scope.items()):
         symbol.display(name, ast, new_prefix, i + 1 >= len(self.scope.items()))

      print(f"{prefix}├─Parameters")
      for i, ani in enumerate(self.parameter_types):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.parameter_types))

      print(f"{prefix}├─Returns")
      for i, token in enumerate(self.return_types):
         current_is_last: bool = i + 1 >= len(self.return_types)
         print(f"{new_prefix}{TreePrinter.bool_to_connector(current_is_last)}{token.str_literal}")

      print(f"{prefix}└─Body")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      for i, ani in enumerate(self.body):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.body))

class AstModule(AstNode):
   kind = AstNodeKind.Module
   name: str
   procedures: list[ANI]
   types: list[ANI]
   scope: dict[str, Symbol]

   def __init__(self, name: str) -> None:
      self.name = name
      self.procedures = []
      self.types = []
      self.scope = {}

   # May return [None] when [file_path] does not exist or is not a file.
   @staticmethod
   def parse(file_path: str, ast: "Ast") -> "AstModule | None":
      # Todo: Check if the file already exists
      if not Path(file_path).is_file():
         return None

      lexer = Lexer(file_path)
      state = ParsingState()
      self = AstModule(Path(file_path).stem)
      ast.scope_stack.append(self.scope)

      while True:
         token: Token = lexer.next()
         match token.kind:
            case TokenKind.Def:
               state.exit_panic()
               proc: ANI = AstProcedure.parse(token.indent, lexer, ast, state)
               if proc >= 0:
                  self.procedures.append(proc)

            case TokenKind.Class:
               state.exit_panic()
               class_decl: ANI = AstClass.parse(token.indent, lexer, ast, state)
               if class_decl >= 0:
                  self.types.append(class_decl)

            case TokenKind.Eof: break
            case TokenKind.NewLine: pass

            case _:
               if state.panic: continue
               state.enter_panic()
               reporter.unexpected_token(file_path, token, [])

      ast.scope_stack.pop()
      return self

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Module: {self.name}")
      prefix += TreePrinter.last_to_prefix_append(last)

      new_prefix: str = prefix + TreePrinter.last_to_prefix_append(False)
      print(f"{prefix}├─Scope")
      for i, (name, symbol) in enumerate(self.scope.items()):
         symbol.display(name, ast, new_prefix, i + 1 >= len(self.scope.items()))

      print(f"{prefix}├─Types")
      for i, ani in enumerate(self.types):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.types))

      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      print(f"{prefix}└─Procedures")
      for i, ani in enumerate(self.procedures):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.procedures))

class Ast:
   modules: list[AstNode]
   nodes: list[AstNode]
   types: list[Type]
   scope: dict[str, Symbol]
   scope_stack: list[dict[str, Symbol]]

   def __init__(self) -> None:
      self.modules = []
      self.nodes = []
      self.scope_stack = []
      self.types = [
         TypeBit(TypeKind.Bit8, False),
         TypeBit(TypeKind.Bit16, False),
         TypeBit(TypeKind.Bit32, False),
         TypeBit(TypeKind.Bit64, False),

         TypeBit(TypeKind.Bit8, True),
         TypeBit(TypeKind.Bit16, True),
         TypeBit(TypeKind.Bit32, True),
         TypeBit(TypeKind.Bit64, True),
      ]

      self.scope = {
         "ubit8": SymbolType(0),
         "ubit16": SymbolType(1),
         "ubit32": SymbolType(2),
         "ubit64": SymbolType(3),

         "sbit8": SymbolType(4),
         "sbit16": SymbolType(5),
         "sbit32": SymbolType(6),
         "sbit64": SymbolType(7)
      }

   def dump(self) -> None:
      print(".")
      print(f"├─TypeTable")
      prefix: str = TreePrinter.last_to_prefix_append(False)
      for i, t in enumerate(self.types):
         t.display(self, prefix, i + 1 >= len(self.types))

      print(f"├─Scope")
      for i, (name, symbol) in enumerate(self.scope.items()):
         symbol.display(name, self, prefix, i + 1 >= len(self.scope.items()))

      print(f"└─Modules")
      prefix = TreePrinter.last_to_prefix_append(True)
      for i, module in enumerate(self.modules):
         module.display(self, prefix, i + 1 >= len(self.modules))

class Parser:
   @staticmethod
   def parse_file(file_path: str) -> Ast:
      ast = Ast()
      module = AstModule.parse(file_path, ast)
      if module is None:
         print(f"[ERROR] File \"{file_path}\" either doesn't exist or is not a file.", file=sys.stderr)
         exit()

      ast.modules.append(module)
      return ast
