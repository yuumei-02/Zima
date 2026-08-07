# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

class CompileFlags:
   token_dump: bool
   ast_dump: bool

   def __init__(self) -> None:
      self.token_dump = False
      self.ast_dump = False
