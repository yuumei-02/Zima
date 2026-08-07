# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from lexer import *

# Todo: Expand [path] to an absolute path using pathlib
def unexpected_token(path: str, token: Token, expected: list[TokenKind]) -> None:
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
