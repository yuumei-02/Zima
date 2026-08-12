# Copyright (c) 2026 yuumei-02. All Rights Reserved.
# See the LICENSE file for more information.

import os
from utils import *
from enum import Enum
from typing import TypeAlias, cast

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
   memry_alignment: int
   name: str

   def __init__(self, name: str, type_table: list[Type], fields: list[TypeId]):
      self.fields = []
      self.memory_alignment = 0
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
         if field_alignment > self.memory_alignment:
            self.memory_alignment = field_alignment

   def size(self) -> int:
      return self.byte_size

   def alignment(self) -> int:
      return self.memory_alignment

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

ValueId: TypeAlias = int
InstrId: TypeAlias = int

class Value:
   type: TypeId
   value: int | None

   def __init__(self, type: TypeId, value: int | None = None):
      self.type = type
      self.value = value

class InstrKind(Enum):
   Ret = iota()
   Add = iota()
   Sub = iota()
   Mul = iota()
   Div = iota()
   Count = reset()

   def to_str(self) -> str:
      assert InstrKind.Count.value == 5
      match self:
         case InstrKind.Ret: return "Ret"
         case InstrKind.Add: return "Add"
         case InstrKind.Sub: return "Sub"
         case InstrKind.Mul: return "Mul"
         case InstrKind.Div: return "Div"
         case _:
            panic("unreachable")

class Instr:
   kind: InstrKind
   descendant: int = -1

class InstrBinOp(Instr):
   dest: ValueId
   lhs: ValueId
   rhs: ValueId

   def __init__(self, op: InstrKind, dest: ValueId, lhs: ValueId, rhs: ValueId) -> None:
      self.kind = op
      self.dest = dest
      self.lhs = lhs
      self.rhs = rhs

class InstrRet(Instr):
   kind = InstrKind.Ret
   src: ValueId | None

   def __init__(self, src: ValueId | None = None) -> None:
      self.src = src

class Procedure:
   name: str
   parameters: list[TypeId]
   returns: tuple[TypeId, TypeId]
   values: list[Value]
   instructions: list[Instr]

   def __init__(self, name: str, parameters: list[TypeId], returns: tuple[TypeId, TypeId]) -> None:
      self.name = name
      self.parameters = parameters
      self.returns = returns
      self.values = []
      self.instructions = []

   def set_current_instr_as_descendant_of_the_previous(self) -> None:
      if len(self.instructions) > 0:
         self.instructions[len(self.instructions) - 1].descendant = len(self.instructions)

   def add_value(self, type: TypeId, literal: int | None = None) -> ValueId:
      self.values.append(Value(type, literal))
      return len(self.values) - 1

   def add_bin_op(self, op: InstrKind, lhs: ValueId, rhs: ValueId) -> ValueId:
      self.set_current_instr_as_descendant_of_the_previous()
      self.instructions.append(InstrBinOp(op, len(self.values), lhs, rhs))
      self.values.append(Value(self.values[lhs].type))
      return len(self.values) - 1

   def add_ret(self, src: ValueId | None = None) -> None:
      self.set_current_instr_as_descendant_of_the_previous()
      self.instructions.append(InstrRet(src))

class ZMIR:
   type_table: list[Type]
   procedures: list[Procedure]

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
      self.procedures = []

   def instrinsic_i1(self) -> int: return 0
   def instrinsic_i8(self) -> int: return 1
   def instrinsic_i16(self) -> int: return 2
   def instrinsic_i32(self) -> int: return 3
   def instrinsic_i64(self) -> int: return 4
   def instrinsic_u8(self) -> int: return 5
   def instrinsic_u16(self) -> int: return 6
   def instrinsic_u32(self) -> int: return 7
   def instrinsic_u64(self) -> int: return 8

   def add_procedure(self, procedure: Procedure) -> None:
      self.procedures.append(procedure)

   def add_type(self, type: Type) -> None:
      self.type_table.append(type)

   def dump(self) -> None:
      instruction_shape = "rect"
      control_flow_shape = "diamond"
      data_flow_color = "green"
      control_flow_color = "red"

      with open("./output.dot", "w") as f:
         f.write("digraph {\n")
         f.write("subgraph type_table {\n")
         f.write("label = \"data types\"\n")
         f.write("cluster = true\n")
         for i, typ in enumerate(self.type_table):
            f.write(f"t{i} [label=\"{typ.to_str(self.type_table)}\"]\n")
         f.write("}\n")

         for procedure in self.procedures:
            f.write("subgraph {\n")
            f.write("cluster = true\n")
            f.write(f"label = \"procedure {procedure.name}\"\n")
            f.write("subgraph {\n")
            f.write("cluster = false\n")
            for i, value in enumerate(procedure.values):
               if value.value is None:
                  f.write(f"v{i}\n")
               else:
                  f.write(f"v{i} ({value.value})\n")
            f.write("}\n")

            f.write("subgraph {\n")
            f.write("cluster = false\n")
            for i, instr in enumerate(procedure.instructions):
               if instr.descendant >= 0:
                  f.write(f"instr_{i} -> instr_{instr.descendant}\n [color={control_flow_color}]")

               assert InstrKind.Count.value == 5
               match instr.kind:
                  case InstrKind.Add | InstrKind.Sub | InstrKind.Mul | InstrKind.Div:
                     f.write(f"instr_{i} [label=\"{instr.kind.to_str()}\"; shape={instruction_shape}]")
                     instr = cast(InstrBinOp, instr)
                     f.write(f"{{ v{instr.lhs}; v{instr.rhs} }} -> instr_{i} [color={data_flow_color}]\n")
                     f.write(f"instr_{i} -> v{instr.dest}\n [color={data_flow_color}]")
                     f.write(f"t{procedure.values[instr.lhs].type} -> v{instr.lhs}\n")
                     f.write(f"t{procedure.values[instr.rhs].type} -> v{instr.rhs}\n")

                  case InstrKind.Ret:
                     f.write(f"instr_{i} [label=\"{instr.kind.to_str()}\"; shape={control_flow_shape}]")
                     instr = cast(InstrRet, instr)
                     if instr.src is not None:
                        f.write(f"v{instr.src} -> instr_{i} [color={data_flow_color}]\n")

                  case _:
                     panic("unreachable")
            f.write("}\n")
            f.write("}\n")

         f.write("}\n")

      os.system("dot -Tsvg ./output.dot > ./output.svg")
      os.system("rm ./output.dot")

def test_ir() -> ZMIR:
   ir = ZMIR()

   main = Procedure("main", [], (-1, -1))
   v1 = main.add_value(ir.instrinsic_i32())
   v2 = main.add_value(ir.instrinsic_i32())

   i1 = main.add_bin_op(InstrKind.Add, v1, v2)
   main.add_ret(i1)

   ir.add_procedure(main)
   return ir
