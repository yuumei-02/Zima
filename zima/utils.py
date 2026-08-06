# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from operator import truediv
from typing import TypeAlias, NoReturn

__iota__: int = 0;

def iota() -> int:
   global __iota__
   __iota__ += 1
   return __iota__ - 1

def reset() -> int:
   global __iota__
   old: int = __iota__
   __iota__ = 0
   return old

def panic(message: str) -> NoReturn:
   raise Exception(message)

def unreachable() -> NoReturn:
   raise Exception("unreachable")
