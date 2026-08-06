Copyright (c) 2026 yuumei-02. All Rights Reserved.
See the LICENSE file for more information.

# About
The Zima programming language specification.

# Expressions
## Atoms
```Zima
1234567890  // Int literals
0xdeadbeef  // Hex literals
12345.67890 // Float literals
"world"     // String literals
'c'         // Character literals
my_func()   // Procedure calls
variable    // Variables
```
Atoms are literals that make up expressions.
Atoms on their own are expressions but can also be combined using operators to create compound expressions

## Operators
+------------+-------------------+------------+---------------+----------+--------------------------------+
|    Type    |     Operator      | Precedence | Associativity | Operands |          Description           |
+------------+-------------------+------------+---------------+----------+--------------------------------+
| Arithmatic | * / %             | 12         | left to right | binary   | Multiply, divide, modulo       |
|            | + -               | 11         |               |          | Add, subtract                  |
+------------+-------------------+------------+---------------+----------+--------------------------------+
| Logical    | !                 | 13         | right to left | unary    | invert boolean                 |
|            | > >=              | 9          | left to right | binary   | greater, greater or equals     |
|            | < <=              | 9          |               |          | less than, less than or equals |
|            | != ==             | 8          |               |          | Not equals, equals             |
|            | &&                | 4          |               |          | and                            |
|            | ||                | 3          |               |          | or                             |
+------------+-------------------+------------+---------------+----------+--------------------------------+
| Bitwise    | ~                 | 13         | right to left | unary    | not                            |
|            | << >>             | 10         | left to right | binary   | shift left, shift right        |
|            | &                 | 7          |               |          | and                            |
|            | ^                 | 6          |               |          | xor                            |
|            | |                 | 5          |               |          | or                             |
+------------+-------------------+------------+---------------+----------+--------------------------------+
| Misc       | &                 | 13         | right to left | unary    | address of                     |
|            | sizeof(type)      | 13         |               |          | size of type
|            | cast(type)        | 13         |               |          | cast to type                   |
|            | reinterpret(type) | 13         |               |          | reinterpet as type             |
+------------+-------------------+------------+---------------+----------+--------------------------------+

Operator precedence is the priority a operator has over another operator.
The higher the precedence, the more priority the operator has.

# Statements
## If
```Zima
if cond:
   pass
elif cond:
   pass
else:
   pass
```

## switch
```Zima
switch enum_or_int:
   case enum.variant1: panic("variant1")
   case enum.variant2: panic("variant2")
   default:
      panic("unhandled variant")
   
   // The invalid case only works for enums
   invalid:
      panic("invalid enum variant")
```

## for
```Zima
iterable: int = 10
for i: int in iterable:
   print(i.to_str())
```

## Defer
```Zima
import memory

def main():
   int* ptr = memory.alloc(4)
   // Gets run before exiting the procedure but and thus, not right away.
   defer:
      memory.free(ptr)
      print("after free")
   
   print("before defer")
```

# Declerations
## Procedure
```Zima
def proc_name(arg1: type, arg2: type) -> return_type:
   pass
```
The return type of a procedure that does not return a value is void.
Void procedure may leave out the return type

## Classes
```Zima
import memory \\ Hypothetical allocator library

class MyList[T]:
   data: T*
   length: int
   capacity: int

   def __init__(self):
      self.length = 0
      self.capacity = 16
      self.data = memory.alloc(sizeof(T) * 16)
      
   def __index__(self, index: usize) -> T*:
      if index >= self.length:
         abort("out of bounds array index")

      return self.data + index
      
   def __iter__(self, index: usize) -> (T*, bool):
      if index >= self.length:
         return (null, false)
      return (self.__index__(index), true)
      
   def append(self, value: T):
      if self.length >= self.capacity:
         self.capacity *= 2
         self.data = memory.realloc(self.data, sizeof(T) * self.capacity)
   
      memory.copy(self.data + self.length, &value, sizeof(T))
      self.length += 1

   def clear(self):
      self.length = 0

def main():
   list := MyList[int]()
   list.append(0xdeadbeef)
   
   beef: int = list[0]
   beef.reset() // A hypothetical int method
```

Almost every type in Zima is a class. Even integers are classes.
Classes are a grouping of one or more values with optional namespaced procedures.

Classes can have special procedures as shown in the example above.
These special procedures are serounded on both ends of their name by two underscores and have unique properties attached that normal procedures do not.
Currently there are two special procedures a class could have.
The __init__ procedure and the __index__ procedure.

### __init__
Objects are always left unitialized when created meaning that they contain junk memory that just so happened to be there in memory at creation time.
The __init__ procedure if it is defined for a object, implicitly gets called for said object right after object creation.
All parameters passed to object creation gets passed to the __init__procedure.
The __init__ procedure is meant to be used to define default values for fields and or to assign object creation parameters to the actual fields.

### __index__
When you index into an array using the bracket syntax (```val: int = int_array[2]```), you don't actually index into the array but instead, call the __index__ procedure.
Container types such as the build in list type implement these procedures for array indexing.
The __index__ procedure is meant to be used to implement indexing for custom container types.

### __iter__
When a class exposes this procedure, it becomes an iterable object.
The for loop can only loop over iterables.
The for loop calls the __iter__ procedure each iteration and expects the method to return a tuple
containing the value and a boolean to indicate whether or not to terminate the iteration.

## Enums
```Zima
enum error:
   Success = 0,
   FileNotFound,
   DirNotFound
```
Enums are a namespace containing constant int variables only.
Enums are ints in every way except for switch cases where they have a few special properties.

# Types
1. Classes
2. Enums
3. Tuples

