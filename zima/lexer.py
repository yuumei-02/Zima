# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from enum import Enum
from utils import *

class TokenKind(Enum):
   # Misc
   Eof = iota()

   # Singe char
   LParen = iota()
   RParen = iota()
   Colon  = iota()
   Comma  = iota()
   Equals = iota()
   Plus   = iota()
   Minus  = iota()
   Star   = iota()
   Slash  = iota()

   # Double char
   Arrow = iota()

   # Literals
   Identifier = iota()
   IntLiteral = iota()

   # Keywords
   Def    = iota()
   Return = iota()
   Pass   = iota()
   Count  = reset()

   def to_str(self) -> str:
      assert TokenKind.Count.value == 16
      match self:
         case TokenKind.Eof:        return "Eof"
         case TokenKind.LParen:     return "LParen"
         case TokenKind.RParen:     return "RParen"
         case TokenKind.Colon:      return "Colon"
         case TokenKind.Comma:      return "Comma"
         case TokenKind.Equals:     return "Equals"
         case TokenKind.Plus:       return "Plus"
         case TokenKind.Minus:      return "Minus"
         case TokenKind.Star:       return "Star"
         case TokenKind.Slash:      return "Slash"
         case TokenKind.Arrow:      return "Arrow"
         case TokenKind.Identifier: return "Identifier"
         case TokenKind.IntLiteral: return "IntLiteral"
         case TokenKind.Def:        return "Def"
         case TokenKind.Return:     return "Return"
         case TokenKind.Pass:       return "Pass"
         case TokenKind.Count:      return "Count"
         case _:
            unreachable()
         

class Token:
   kind: TokenKind
   y: int
   x: int
   str_literal: str
   int_literal: int

   def __init__(self) -> None:
      self.kind = TokenKind.Eof
      self.y = 1
      self.x = 1

   def dump(self, file_path: str) -> None:
      print(f"{file_path}:{self.y}:{self.x}: info: {self.kind.to_str()}", end="")
      match self.kind:
         case TokenKind.Identifier: print(f" ({self.str_literal})")
         case TokenKind.IntLiteral: print(f" ({self.int_literal})")
         case _: print()

class Lexer:
   file_path: str
   file_handle: FileHandle

   def __init__(self, file_path: str) -> None:
      self.file_path = file_path
      self.file_handle = open(file_path, "r")

   def next(self) -> Token:
      return Token()

   def delete(self) -> None:
      self.file_handle.close()

