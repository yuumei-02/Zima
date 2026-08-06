# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from lexer import *
import sys

def compile_program(file: str) -> None:
   lexer = Lexer(file)

   while True:
      token: Token = lexer.next()
      token.dump(file)
      if token.kind == TokenKind.Eof:
         break

def main() -> None:
   args: list[str] = sys.argv

   if len(args) < 0:
      print("[!] Missing input files", file=sys.stderr)

   for i in range(len(sys.argv) - 1):
      compile_program(args[i + 1])

if __name__ == "__main__":
   main()

