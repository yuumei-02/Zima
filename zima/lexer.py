# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

import sys
from enum import Enum
from utils import *

class TokenKind(Enum):
   # Misc
   Eof = iota()
   NewLine = iota()

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
   StrLiteral = iota()

   # Keywords
   Def    = iota()
   Return = iota()
   Scope  = iota()
   Pass   = iota()
   Count  = reset()

   def to_str(self) -> str:
      assert TokenKind.Count.value == 19
      match self:
         case TokenKind.Eof:        return "Eof"
         case TokenKind.NewLine:    return "NewLine"
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
         case TokenKind.StrLiteral: return "StrLiteral"
         case TokenKind.Def:        return "Def"
         case TokenKind.Return:     return "Return"
         case TokenKind.Scope:      return "Scope"
         case TokenKind.Pass:       return "Pass"
         case TokenKind.Count:      return "Count"
         case _:
            unreachable()

keywords: dict[str, TokenKind] = {
   "def": TokenKind.Def,
   "return": TokenKind.Return,
   "scope": TokenKind.Scope,
   "pass": TokenKind.Pass
}

class Token:
   kind: TokenKind
   y: int
   x: int
   indent: int
   str_literal: str
   int_literal: int

   def __init__(self) -> None:
      self.kind = TokenKind.Eof
      self.y = 1
      self.x = 1
      self.indent = 0

   def define_str_literal(self) -> None:
      self.str_literal = ""

   def define_int_literal(self) -> None:
      self.int_literal = 0

   def dump(self, file_path: str) -> None:
      print(f"{file_path}:{self.y}:{self.x}: info: ({self.indent}) {self.kind.to_str()}", end="")
      match self.kind:
         case TokenKind.Identifier: print(f" ({self.str_literal})")
         case TokenKind.IntLiteral: print(f" ({self.int_literal})")
         case TokenKind.StrLiteral: print(f" ({self.str_literal})") # @Todo: Unescape string
         case _: print()

class LexerMode(Enum):
   Trim = iota()
   Word = iota()
   IntLiteral = iota()
   StrLiteral = iota()
   Comment = iota()
   Count = reset()

class Lexer:
   file_path: str
   file_contents: str
   z: int
   y: int
   x: int
   undone_tokens: list[Token]

   def __init__(self, file_path: str) -> None:
      self.z = -1
      self.y = 1
      self.x = 0
      self.file_path = file_path
      self.undone_tokens = []
      try:
         with open(file_path, "r") as f:
            self.file_contents = f.read()
      except Exception as e:
         print(f"[ERROR] Failed to create read from file {file_path}, reason: \"{str(e)}\"",
            file=sys.stderr)
         exit()

   @staticmethod
   def identifier_allowed(char: str) -> bool:
      if char.isdigit(): return True
      if char.isalpha(): return True
      if char == '_': return True
      return False

   def advance(self) -> None:
      if self.z > -1 and self.file_contents[self.z] == '\n':
         self.y += 1
         self.x = 0

      self.x += 1
      self.z += 1

   def can_peek(self) -> bool:
      return self.z + 1 < len(self.file_contents)

   def undo(self, token: Token) -> None:
      self.undone_tokens.append(token)

   def peek(self) -> Token:
      token: Token = self.next()
      self.undone_tokens.append(token)
      return token

   # Todo: Figure out why some new lines are outputted twice and remove them
   #       - Yuumei-02, 00:25
   def next(self) -> Token:
      if len(self.undone_tokens) > 0:
         return self.undone_tokens.pop(len(self.undone_tokens) - 1)

      token = Token()
      mode = LexerMode.Trim
      skip_one_advance = False
      int_is_negative = False

      while self.can_peek():
         if skip_one_advance:
            skip_one_advance = False
         else:
            self.advance()
         assert LexerMode.Count.value == 5
         match mode:
            case LexerMode.Trim:
               token.x = self.x
               token.y = self.y
               match self.file_contents[self.z]:
                  case '+': token.kind = TokenKind.Plus;   return token
                  case '*': token.kind = TokenKind.Star;   return token
                  case ',': token.kind = TokenKind.Comma;  return token
                  case ':': token.kind = TokenKind.Colon;  return token
                  case '=': token.kind = TokenKind.Equals; return token
                  case '(': token.kind = TokenKind.LParen; return token
                  case ')': token.kind = TokenKind.RParen; return token

                  case '-':
                     if self.can_peek() and self.file_contents[self.z + 1] == '>':
                        token.kind = TokenKind.Arrow
                        self.advance()
                        return token
                     elif self.can_peek() and self.file_contents[self.z + 1].isdigit():
                        token.define_int_literal()
                        mode = LexerMode.IntLiteral
                        int_is_negative = True
                     else:
                        token.kind = TokenKind.Minus
                        return token

                  case '/':
                     if self.can_peek() and self.file_contents[self.z + 1] == '/':
                        mode = LexerMode.Comment
                     else:
                        token.kind = TokenKind.Slash
                        return token

                  case '\n':
                     token.kind = TokenKind.NewLine
                     return token

                  case ' ':
                     token.indent += 1

                  case "\"":
                     token.define_str_literal()
                     mode = LexerMode.StrLiteral

                  case _:
                     if self.file_contents[self.z].isdigit():
                        mode = LexerMode.IntLiteral
                        token.define_int_literal()
                        int_is_negative = False
                     else:
                        mode = LexerMode.Word
                        token.define_str_literal()
                     skip_one_advance = True

            case LexerMode.IntLiteral:
               token.int_literal *= 10
               token.int_literal += int(self.file_contents[self.z])
               if self.can_peek() and not self.file_contents[self.z + 1].isdigit():
                  token.kind = TokenKind.IntLiteral
                  if int_is_negative:
                     token.int_literal = -token.int_literal
                  return token

            case LexerMode.StrLiteral:
               if self.file_contents[self.z] == "\"":
                  token.kind = TokenKind.StrLiteral
                  return token

               token.str_literal += self.file_contents[self.z]

            case LexerMode.Word:
               token.str_literal += self.file_contents[self.z]
               if self.can_peek() and not self.identifier_allowed(self.file_contents[self.z + 1]):
                  global keywords
                  keyword = keywords.get(token.str_literal)
                  if keyword is None:
                     token.kind = TokenKind.Identifier
                  else:
                     token.kind = keyword
                  return token

            case LexerMode.Comment:
               if self.file_contents[self.z] == '\n':
                  mode = LexerMode.Trim

            case _:
               panic("unreachable")

      return token

