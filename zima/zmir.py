# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

from utils import *
from enum import Enum
from typing import TypeAlias
import os

TypeId: TypeAlias = int

# Todo: Validate whether this actually calculates padding correctly
def calculate_padding(address: int, alignment: int) -> int:
   if address == 0: return 0

   remainder = address % alignment
   if remainder == 0:
      return 0
   return alignment - remainder

class TypeKind(Enum):
   i1 = iota()
   i8 = iota()
   i16 = iota()
   i32 = iota()
   i64 = iota()

   u8 = iota()
   u16 = iota()
   u32 = iota()
   u64 = iota()

   Aggregate = iota()
   Pointer = iota()
   Count = reset()

class Type:
   kind: TypeKind

   def size(self) -> int:
      panic("Missing implementation for method \"size\" in one of the type subclasses.")

   def alignment(self) -> int:
      panic("Missing implementation for method \"alignment\" in one of the type subclasses.")

   def to_str(self, type_table: list["Type"]) -> str:
      panic("Missing implementation for method \"to_str\" in one of the type subclasses.")

class TypeScalar(Type):
   def __init__(self, kind: TypeKind) -> None:
      self.kind = kind

   def size(self) -> int:
      match self.kind:
         case TypeKind.i1:  return 1
         case TypeKind.i8:  return 1
         case TypeKind.i16: return 2
         case TypeKind.i32: return 4
         case TypeKind.i64: return 8
         case TypeKind.u8:  return 1
         case TypeKind.u16: return 2
         case TypeKind.u32: return 4
         case TypeKind.u64: return 8
         case _:
            panic("unreachable")

   def alignment(self) -> int:
      return self.size()

   def is_signed(self) -> bool:
      match self.kind:
         case TypeKind.i1:  return True
         case TypeKind.i8:  return True
         case TypeKind.i16: return True
         case TypeKind.i32: return True
         case TypeKind.i64: return True
         case TypeKind.u8:  return False
         case TypeKind.u16: return False
         case TypeKind.u32: return False
         case TypeKind.u64: return False
         case _:
            panic("unreachable")

   def to_str(self, type_table: list["Type"]) -> str:
      match self.kind:
         case TypeKind.i1:  return "i1"
         case TypeKind.i8:  return "i8"
         case TypeKind.i16: return "i16"
         case TypeKind.i32: return "i32"
         case TypeKind.i64: return "i64"
         case TypeKind.u8:  return "u8"
         case TypeKind.u16: return "u16"
         case TypeKind.u32: return "u32"
         case TypeKind.u64: return "u64"
         case _:
            panic("unreachable")

class TypeAggregate(Type):
   kind = TypeKind.Aggregate
   fields: list[tuple[int, TypeId]] # A tuple of padding and the field type
   byte_size: int
   alignment: int
   name: str

   def __init__(self, name: str, type_table: list[Type], fields: list[TypeId]):
      self.fields = []
      self.alignment = 0
      self.byte_size = 0
      self.name = name

      address: int = 0
      for type_id in fields:
         field_size:      int = type_table[type_id].size()
         field_alignment: int = type_table[type_id].alignment()
         field_padding:   int = calculate_padding(address, field_alignment)

         address += field_padding + field_size
         self.fields.append((field_padding, type_id))
         self.byte_size += field_padding + field_size
         if field_alignment > self.alignment:
            self.alignment = field_alignment

   def size(self) -> int:
      return self.byte_size

   def alignment(self) -> int:
      return self.alignment

   def to_str(self, type_table: list["Type"]) -> str:
      return f"Aggregate[{self.name}]"

class TypePointer(Type):
   kind = TypeKind.Pointer
   pointee: TypeId

   def __init__(self, pointee: TypeId) -> None:
      self.pointee = pointee

   def size(self) -> int:
      return 8

   def alignment(self) -> int:
      return 8

   def to_str(self, type_table: list["Type"]) -> str:
      return f"ptr[{type_table[self.pointee].to_str(type_table)}]"

class ZMIR:
   type_table: list[Type]

   def __init__(self) -> None:
      self.type_table = [
         TypeScalar(TypeKind.i1),
         TypeScalar(TypeKind.i8),
         TypeScalar(TypeKind.i16),
         TypeScalar(TypeKind.i32),
         TypeScalar(TypeKind.i64),
         TypeScalar(TypeKind.u8),
         TypeScalar(TypeKind.u16),
         TypeScalar(TypeKind.u32),
         TypeScalar(TypeKind.u64)
      ]

   def add_type(self, type: Type) -> None:
      self.type_table.append(type)

   def dump(self) -> None:
      with open("./output.dot", "w") as f:
         f.write("digraph {\n")
         f.write("subgraph type_table {\n")
         for typ in self.type_table:
            f.write(f"{typ.to_str(self.type_table)}\n")
         f.write("}\n")
         f.write("}\n")

      os.system("dot -Tsvg ./output.dot > ./output.svg")
      os.system("rm ./output.dot")
