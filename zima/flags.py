# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

class CompileFlags:
   token_dump: bool
   ast_dump: bool
   ir_dump: bool
   ir_test: bool
   no_core: bool
   core_path: str

   def __init__(self) -> None:
      self.token_dump = False
      self.ast_dump = False
      self.ir_dump = False
      self.ir_test = False
      self.no_core = False
      self.core_path = "./core/core.zima"
