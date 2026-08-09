# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from flags import *
from lexer import *
import parser
import zmir

def token_dump(file: str) -> None:
   lexer = Lexer(file)

   while True:
      token: Token = lexer.next()
      token.dump(file)
      if token.kind == TokenKind.Eof:
         break

def compile_program(file: str, flags: CompileFlags) -> bool:
   if flags.token_dump:
      token_dump(file)
      return False

   ast: parser.Ast | None = parser.Parser.parse_file(file, flags.core_path)
   if ast is None:
      return True

   if ast.collect_symbols_and_types():
      return True

   if flags.ast_dump:
      ast.dump()
      return False

   ir: zmir.ZMIR = ast.generate_zmir()
   if flags.ir_dump:
      ir.dump()

   return False

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
         case "--ir-dump":    flags.ir_dump = True
         case _:
            if args[i + 1].startswith("--core-path="):
               flags.core_path = args[i + 1].removeprefix("--core-path=")
            else:
               files.append(args[i + 1])

   for file in files:
      if compile_program(file, flags):
         print("Compilation failure", file=sys.stderr)
         return

if __name__ == "__main__":
   main()

