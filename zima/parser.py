# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.
from abc import abstractmethod
from dataclasses import dataclass
from lexer import *
from typing import TypeAlias
from pathlib import Path
import reporter
from utils import TriBool

ANI: TypeAlias = int

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
   Count = reset()

   @staticmethod
   def try_parse_bin_op_token(kind: TokenKind) -> "Operator | None":
      assert Operator.Count.value == 4
      match kind:
         case TokenKind.Plus:  return Operator.Add
         case TokenKind.Minus: return Operator.Sub
         case TokenKind.Star:  return Operator.Mul
         case TokenKind.Slash: return Operator.Div
         case _: return None

   def to_str(self) -> str:
      assert Operator.Count.value == 4
      match self:
         case Operator.Add: return "Add"
         case Operator.Sub: return "Sub"
         case Operator.Mul: return "Mul"
         case Operator.Div: return "Div"
         case _:
            panic("unreachable")

   def precedence(self) -> int:
      assert Operator.Count.value == 4
      match self:
         case Operator.Mul | Operator.Div: return 12
         case Operator.Add | Operator.Sub: return 11
         case _:
            panic("unreachable")

   def left_associative(self) -> bool:
      assert Operator.Count.value == 4
      match self:
         case Operator.Add: return True
         case Operator.Sub: return True
         case Operator.Mul: return True
         case Operator.Div: return True
         case _:
            panic("unreachable")

   def is_binary(self) -> bool:
      assert Operator.Count.value == 4
      match self:
         case Operator.Mul: return True
         case Operator.Add: return True
         case Operator.Sub: return True
         case Operator.Mul: return True
         case Operator.Div: return True
         case _:
            panic("unreachable")

class AstNodeKind(Enum):
   # Declarations
   Module = iota()
   Procedure = iota()
   Parameter = iota()
   Variable = iota()

   # Statements
   Return = iota()

   # Expressions
   BinOp = iota()
   IntLiteral = iota()
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

         case TokenKind.Identifier:
            ast.nodes.append(AstIdentifier(token))
            return len(ast.nodes) - 1

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
      check_indent = False
      while True:
         token = lexer.next()
         if token.kind == TokenKind.NewLine:
            check_indent = True
            continue

         if token.kind == TokenKind.Eof or (check_indent and token.indent <= current_indent):
            lexer.undo(token)
            return self

         if check_indent and token.indent > indent_level:
            if state.panic: continue
            state.enter_panic()
            reporter.over_indent(lexer.file_path, token)
            continue
         else:
            check_indent = False

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

            case TokenKind.Pass:
               state.exit_panic()

            case _:
               if state.panic: continue
               state.enter_panic()
               reporter.unexpected_token(lexer.file_path, token, [])

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      assert False, "Unimplemented base class"

class AstBinOp(AstNode):
   operator: Operator
   lhs: ANI
   rhs: ANI

   def __init__(self, operator: Operator, lhs: ANI, rhs: ANI) -> None:
      self.operator = operator
      self.lhs = lhs
      self.rhs = rhs

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.operator.to_str()}")
      prefix += TreePrinter.last_to_prefix_append(last)
      ast.nodes[self.lhs].display(ast, prefix, False)
      ast.nodes[self.rhs].display(ast, prefix, True)

class AstIdentifier(AstNode):
   value: Token

   def __init__(self, value: Token) -> None:
      assert value.kind == TokenKind.Identifier
      self.value = value

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.value.str_literal}")

class AstIntLiteral(AstNode):
   value: Token

   def __init__(self, value: Token) -> None:
      assert value.kind == TokenKind.IntLiteral
      self.value = value

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.value.int_literal}")

class AstVariable(AstNode):
   name: Token
   type: Token | str | None # Explicit type | inferred type | implicit type before inference
   expression: ANI

   # Expects that the name and type colon part of the variable declaration syntax has already been parsed
   @staticmethod
   def parse(name: Token, lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstVariable()
      self.name = name

      token: Token = lexer.next()
      match token.kind:
         case TokenKind.Identifier:
            self.type = token
            token = lexer.next()
            match token.kind:
               case TokenKind.NewLine: pass
               case TokenKind.Equals:
                  self.expression = AstNode.parse_expression(-1, lexer, ast, state)

               case _:
                  state.enter_panic()
                  reporter.unexpected_token(lexer.file_path, token, [TokenKind.Equals, TokenKind.NewLine])
                  return -1

         case TokenKind.Equals:
            self.type = None
            self.expression = AstNode.parse_expression(-1, lexer, ast, state)

         case _:
            state.enter_panic()
            reporter.unexpected_token(lexer.file_path, token, [TokenKind.Identifier, TokenKind.Equals])
            return -1

      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.name.str_literal}: ", end="")
      if isinstance(self.type, Token): print(self.type.str_literal)
      elif isinstance(self.type, str): print(self.type)
      else:                            print("@infer")
      prefix += TreePrinter.last_to_prefix_append(last)
      ast.nodes[self.expression].display(ast, prefix, True)

class AstReturn(AstNode):
   expression: ANI

   def __init__(self, expression: ANI) -> None:
      self.expression = expression

   @staticmethod
   def parse(lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstReturn(AstNode.parse_expression(-1, lexer, ast, state))
      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Return")
      prefix += TreePrinter.last_to_prefix_append(last)
      ast.nodes[self.expression].display(ast, prefix, True)

class AstParameter(AstNode):
   name: Token
   type: Token

   def __init__(self, name: Token, type: Token) -> None:
      self.name = name
      self.type = type

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}{self.name.str_literal}: {self.type.str_literal}")

class AstProcedure(AstNode):
   name: Token
   parameter_types: list[ANI]
   return_types: tuple[ANI, ANI]
   body: list[ANI]

   def __init__(self, name: Token) -> None:
      self.name = name
      self.parameter_types = []
      self.return_types = (-1, -1)
      self.body = []

   @staticmethod
   def parse(lexer: Lexer, ast: "Ast", state: ParsingState) -> ANI:
      self = AstProcedure(lexer.next())
      current_indent: int = self.name.indent
      if self.name.kind != TokenKind.Identifier:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, self.name, [TokenKind.Identifier])
         return -1

      token: Token = lexer.next()
      if token.kind != TokenKind.LParen:
         state.enter_panic()
         reporter.unexpected_token(lexer.file_path, token, [TokenKind.LParen])
         return -1

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
            return -1

         match token.kind:
            case TokenKind.Identifier:
               match identifier_as_type:
                  case TriBool.false:
                     parameter_name = token
                     expected = [TokenKind.Colon]

                  case TriBool.true:
                     self.parameter_types.append(len(ast.nodes))
                     ast.nodes.append(AstParameter(parameter_name, token))
                     expected = [TokenKind.Comma, TokenKind.RParen]

                  case TriBool.neutral:
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

      ast.nodes.append(self)
      return len(ast.nodes) - 1

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Procedure {self.name.str_literal}")
      prefix += TreePrinter.last_to_prefix_append(last)
      print(f"{prefix}├─Parameters")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(False)
      for i, ani in enumerate(self.parameter_types):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.parameter_types))

      print(f"{prefix}├─Returns")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(False)
      for i, ani in enumerate(self.return_types):
         if ani >= 0:
            ast.nodes[ani].display(ast, new_prefix, i + 1 > len(self.return_types))

      print(f"{prefix}└─Body")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      for i, ani in enumerate(self.body):
         ast.nodes[ani].display(ast, new_prefix, i + 1 >= len(self.body))

@dataclass
class AstModule(AstNode):
   name: str
   procedures: list[ANI]

   # May return [None] when [file_path] does not exist or is not a file.
   @staticmethod
   def parse(file_path: str, ast: "Ast") -> "AstModule | None":
      # Todo: Check if the file already exists
      if not Path(file_path).is_file():
         return None

      lexer = Lexer(file_path)
      state = ParsingState()
      self = AstModule(Path(file_path).stem, [])

      while True:
         token: Token = lexer.next()
         match token.kind:
            case TokenKind.Def:
               state.exit_panic()
               proc: ANI = AstProcedure.parse(lexer, ast, state)
               if proc >= 0:
                  self.procedures.append(proc)

            case TokenKind.Eof: break
            case TokenKind.NewLine: pass

            case _:
               if state.panic: continue
               state.enter_panic()
               reporter.unexpected_token(file_path, token, [])

      return self

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      print(f"{prefix}{TreePrinter.bool_to_connector(last)}Module {self.name}")
      prefix += TreePrinter.last_to_prefix_append(last)
      print(f"{prefix}└─Procedures")
      for i, ani in enumerate(self.procedures):
         ast.nodes[ani].display(ast, prefix + "  ", i + 1 >= len(self.procedures))

class Ast:
   modules: list[AstNode]
   nodes: list[AstNode]

   def __init__(self) -> None:
      self.modules = []
      self.nodes = []

   def dump(self) -> None:
      print(".")
      for i, module in enumerate(self.modules):
         current_is_last: bool = i + 1 >= len(self.modules)
         module.display(self, "", current_is_last)

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
