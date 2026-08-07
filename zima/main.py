# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from flags import *
from lexer import *
from parser import *

def token_dump(file: str) -> None:
   lexer = Lexer(file)

   while True:
      token: Token = lexer.next()
      token.dump(file)
      if token.kind == TokenKind.Eof:
         break

def compile_program(file: str, flags: CompileFlags) -> None:
   if flags.token_dump:
      token_dump(file)
      return

   ast: Ast = Parser.parse_file(file)
   if flags.ast_dump:
      ast.dump()
      return

def main() -> None:
   args: list[str] = sys.argv

   if len(args) < 0:
      print("[!] Missing input files", file=sys.stderr)

   flags = CompileFlags()
   files: list[str] = []

   for i in range(len(sys.argv) - 1):
      match args[i + 1]:
         case "--token-dump": flags.token_dump = True
         case "--ast-dump":   flags.ast_dump = True
         case _:              files.append(args[i + 1])

   for file in files:
      compile_program(file, flags)

if __name__ == "__main__":
   main()

