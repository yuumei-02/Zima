# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from typing import TypeAlias
import io

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

def panic(message: str) -> None:
   raise Exception(message)

def unreachable() -> None:
   raise Exception("unreachable")

FileHandle: TypeAlias = io.TextIOWrapper

