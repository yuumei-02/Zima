# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from dataclasses import dataclass
from enum import Enum
from utils import *
from lexer import *
from typing import TypeAlias, Self
from pathlib import Path

ANI: TypeAlias = int

class AstNodeKind(Enum):
   Module = iota()
   Procedure = iota()
   Parameter = iota()
   Count = reset()

class AstNode:
   kind: AstNodeKind

   def display(self, prefix: str) -> None:
      pass

class AstParameter(AstNode):
   name: Token
   type: Token

class AstProcedure(AstNode):
   name: Token
   parameter_types: list[ANI]
   return_types: tuple[ANI, ANI]
   body: list[ANI]

@dataclass
class AstModule(AstNode):
   lexer: Lexer
   name: str
   procedures: list[ANI]

   # May return [None] when [file_path] does not exist or is not a file.
   @staticmethod
   def parse(file_path: str) -> "AstModule | None":
      # Todo: Check if the file already exists
      if not Path(file_path).is_file():
         return None

      return AstModule(Lexer(file_path), Path(file_path).stem, [])

   def display(self, prefix: str) -> None:
      print(f"{prefix}Module {self.name}")

@dataclass
class Ast:
   modules: list[AstNode]
   nodes: list[AstNode]

   def dump(self) -> None:
      print(".")
      for i, module in enumerate(self.modules):
         if i + 1 < len(self.modules):
            module.display("├─")
         else:
            module.display("└─")

class Parser:
   @staticmethod
   def parse_file(file_path: str) -> Ast:
      module = AstModule.parse(file_path)
      if module is None:
         print(f"[ERROR] File \"{file_path}\" either doesn't exist or is not a file.", file=sys.stderr)
         exit()

      ast = Ast([module], [])
      return ast
