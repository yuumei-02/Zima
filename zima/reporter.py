# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from lexer import *

# Todo: Expand [path] to an absolute path using pathlib
def unexpected_token(path: str, token: "Token", expected: list["TokenKind"]) -> None:
   print(f"{path}:{token.y}:{token.x}: error: Unexpected token \"{token.kind.to_str()}\"", file=sys.stderr, end="")

   match len(expected):
      case 0: print("", file=sys.stderr)
      case 1: print(f", expected \"{expected[0].to_str()}\"", file=sys.stderr)
      case 2: print(f", expected either \"{expected[0].to_str()}\" or {expected[1].to_str()}", file=sys.stderr)
      case _:
         print(", expected ", file=sys.stderr, end="")
         for i, kind in enumerate(expected):
            print(f"\"{kind.to_str()}\"", file=sys.stderr, end="")
            if i + 2 < len(expected):
               print(", ", file=sys.stderr, end="")
            else:
               print(f" or {expected[i + 1].to_str()}", file=sys.stderr)

def under_indent(path: str, token: "Token") -> None:
   print(f"{path}:{token.y}:{token.x}: error: Expected an indentation greater than that of the previous block.", file=sys.stderr)

def over_indent(path: str, token: "Token") -> None:
   print(f"{path}:{token.y}:{token.x}: error: Expected an indentation equal to that of the current block.", file=sys.stderr)

def class_field_of_type_self(path: str, token: "Token") -> None:
   print(f"{path}:{token.y}:{token.x}: error: Class field can't be of type Self.", file=sys.stderr)

def type_does_not_exist(path: str, token: "Token") -> None:
   print(f"{path}:{token.y}:{token.x}: error: Type \"{token.str_literal}\" does not exists", file=sys.stderr)
