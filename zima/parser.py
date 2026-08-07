# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

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

class AstNodeKind(Enum):
   Module = iota()
   Procedure = iota()
   Parameter = iota()
   Count = reset()

class AstNode:
   kind: AstNodeKind

   def display(self, ast: "Ast", prefix: str, last: bool) -> None:
      pass

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
            ast.nodes[ani].display(ast, new_prefix + "  ", i + 1 > len(self.return_types))

      print(f"{prefix}└─Body")
      new_prefix = prefix + TreePrinter.last_to_prefix_append(True)
      for i, ani in enumerate(self.body):
         ast.nodes[ani].display(ast, new_prefix + "  ", i + 1 >= len(self.body))

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
