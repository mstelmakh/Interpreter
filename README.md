# TKOM 23L
Student: **Mikalai Stelmakh**

Language used: **Python**
## Functionality

### Specifications
Main specifications of the language:
- **Typing**: weak, dynamic
- **Mutability**: mutable by default
- **Passing the arguments**: The arguments to the function are passed by its value, so the function only gets the copy of the object.

### Data types
There will be only a few data types:
- **Booleans.** There are two boolean values: `True` and `False`.
- **Numbers.** The language has two kind of numbers: `int` and `float`.
- **Strings.** The strings are enclosed in double quotes. Escape character (`\`) allows to insert special characters in strings.
- **Functions.** See [functions](#functions).
- **Nil.** Represents the absence of a value.

### Expressions

#### Arithmetic
There are four operators:

|      name      | sign |      type     |
|----------------|------|---------------|
| Addition       |   +  |  Infix        |
| Substraction   |   -  |  Infix/Prefix |
| Miltiplication |   *  |  Infix        |
| Division       |   /  |  Infix        |

All of these operators can work on numbers. Addition can also be used on strings to concatenate them.

Because of the fact, that the language is weakly typed, some operations can be also performed on different operand types by coercing them to common type supported by the operator.

See [examples](#arithmetic-1).

#### Comparison

There are some operators that always return a Boolean result.

|          name         | sign |
|-----------------------|------|
| Less than             |  <   |
| Less than or equal    |  <=  |
| Greater than          |  >   |
| Greater than or equal |  >=  |
| Equal                 |  ==  |
| Not equal             |  !=  |

The comparison rules can be roughly summarized as follows:
1. If the operands have the same type, they are compared as follows:
    - Number: The values are compared.
    - String: The values are compared character by character, using the Unicode value of each character.
    - Boolean: The boolean is converted to a number. true is converted to 1, and false is converted to 0. Then they are compared as numbers.
    - Functions: The names of the functions are compared as strings.

2. If operator is `==` and one of the operands is `nil`, the other must also be `nil` to return true. Otherwise return false.

3. Because the language is weakly typed, when comparing values of different types, the interpreter will attempt to coerce the values to a common type using the type coersion rules:
    - If one of the operands is `nil`, convert `nil` to 0. Then compare two operands again.
    - If one of the operands is a Boolean, convert the boolean to a number: true is converted to 1, and false is converted to 0. Then compare two operands again.
    - If one of the operands is a function, convert the function to a string. Then compare two operands again.
    - Number to string: string is converted to number if possible, otherwise, the number is converted to string, then values are compared.

See [examples](#comparison-1).

#### Logical operators

There are three logical operators used:
- **not** - returns `false` if its operand is `true`, and vice versa.
- **and** - determines if two values are both `true`. It doesn't evaluate the right operand if the left one is `false`.
- **or** - determines if either of two values (or both) are `true`. It doesn't evaluate the right operand if the left one is `true`.

#### Grouping

To change the order of precedence in arithmetic expressions, the parentheses `()` can be used to group sub-expressions. The expressions inside parentheses are evaluated first before the rest of the expression, regardless of the usual operator precedence.

### Statements

The language uses a semicolon (`;`) to mark the end of the statement.

To pack a series of statements, the **block** (`{}`) syntax is used.

### Variables

The keyword `var` is used to declare a variable. The variable without a value defaults to `nil`.

Because the variables are mutable by default, their value can be changed. To declare a constant variable, that can not be modified, use the keyword `const`.

Because of the dynamic typing, the data types of variables are determined at runtime, rather than at compile time. It means that there is no need to specify the data type of a variable explicitly when declaring it, and its data type can be changed by assigning a value of a different type to it.

See [examples](#declaration).

#### Variable Scopes

Variable from the outer scope can be modified inside the block, but if the variable is declared inside the block, it is not visible outside of it.

See [examples](#scopes).

### Comments

Comment starts with a double-slash (`//`) symbol and ends with the new line.

See [example](#comments-1).

### Control flow

There are three ways of controlling the flow of the program:

**if** - executes statement or block of statements based on the condition. See [example](#if).

**while** - executes statement or block of statements while the condition evaluates to `true`. See [example](#while).

**match** - see [Pattern Matching](#pattern-matching).

The scope of the variables described [here](#variable-scopes).

### Functions

The function declaration looks like this:
```Rust
fn getSum(a, const b) {
    return a + b;
}
```

Where `fn` is the keyword to declare a function and `const` - to declare that the parameter is constant in this function.

The code after the `return` statement is not executed. If the function doesn't have a `return` statement, it returns `nil`.

To call a function use the following syntax:
```javascript
someFunction(5, 5);

// Or without arguments
someFunction();
```

Function can be passed to another function, as well as it can be declared in another function. See [example](#nested-functions).

Functions and variables are stored in the same namespace, so it is not possible to declare a function and a variable with the same name within the same scope and use them both. The same goes for redefining a function. The latest definition overrides previous ones. See [example](#overriding).

#### Function Scopes

Scopes does work [the same way](#variable-scopes) they do in blocks, but here we have one more case to consider - when the variable is passed as the argument to the function. See [example](#scopes-1).

### Pattern matching

Pat­tern match­ing is a form of con­di­tional branch­ing which al­lows to con­cisely match on data struc­ture pat­terns and bind vari­ables at the same time.

#### Syntax

Syntactically, a match statement contains:
- a subject expressions
- zero or more case clauses

Each case clause specifies:
- a pattern (or multiple patterns separated by `and` or `or` keywords) and optional assignment to a constant variable (using `as` keyword), which then will be unbound
- an optional “guard” (a condition to be checked if the pattern matches)
- a code to be executed if the case clause is selected

See [example](#pattern-matching-1).

#### Patterns

There are two patterns that can be used in the case block: **compare** and **type** patterns. The patterns can be combined using `or` and `and` keywords. Only one case block can be executed. If multiple patterns fit the matched expression - only the first one will be executed.

##### Compare pattern

A compare pattern consists of a comparison or equality sign and a unary expression. Compare pattern evaluates the matchable with the unary using given operator.

See [example](#compare-pattern-1).

##### Type pattern

A type pattern consists of a `Str`, `Num`, `Bool`, `Func`, `Nil` types. It compares the type of the matched expression with this type.

See [example](#type-pattern-1).

#### Guard

Each top-level pattern can be followed by a guard of the form if expression. A case clause succeeds if the pattern matches and the guard evaluates to a true value.

See [example](#guard-1).

## Code examples

### Hello world
```javascript
print("hello world");
```

### Arithmetic

```javascript
// Basic arithmetics
8 / 4 * 1 + 1               = 3
8 / 4 * (1 + 1)             = 4
8 / (4 * (1 + 1))           = 1
15.5 / 7.75                 = 2.0
2.36 - 5 * -1               = 7.36
```

### Type coercion
```javascript
// On Booleans
true + true                 = 2     // true is coerced to 1
false + false               = 0     // false if coerced to 0
true + false = false + true = 1

// On Numbers
4 + 6                       = 10
"5" + 3                     = 53    // "5" is coerced to number
7 + "2.5"                   = 72.5  // "2.5" is coerced to number
7 + "2a"                    = "72a" // "2a" can not be coerced to number

// On Functions
// functions are converted to string containing its name
"function " + someFunction  = "function: someFunction"
1 + function123             = "1function123"

// Operator "-" is used only for numerical substraction
7 - "2" = "7" - 2           = 5     // string is coerced to number
10 - ""                     = 10    // empty string is coerced to 0
10 - "foo"                          // error

// On Strings
"hello" + "world"           = "helloworld"
"The answer is: " + 12      = "The answer is: 12"
"The answer is " + true     = "The answer is true"
```

### Comparison

```javascript
5 == "5";                           // true
5 != 10;                            // true
5 < 10;                             // true
10 > "5";                           // true
5 <= 5;                             // true
10 >= 10;                           // true
(5 == 5) and (10 == 10);            // true
(5 == 5) or (10 == 5);              // true
not (5 == 10);                      // true
1 == "1" == true                    // true
1 < 1 == true                       // false
true == 2 > 1                       // true
(2 >= 1) and (1 >= 0)               // true
2 >= 1 >= 0                         // error (not grammatically correct)

5 <= "5"                            // true
7 > "-1"                            // true
1000 < "1000a"                      // true
10001 < "1000a"                     // true
12345000 < "a"                      // true
"hello" < "hello!"                  // true
"hello" > "Hello"                   // true
"Hello" < sayHelloFunc              // true
```

### Variables

#### Declaration

```javascript
const a = "string";
var b;                              // nil

b = 5;
print(b);                           // 5

a = 6                               // error

var variable = "one";
print(variable)                     // "one"
var variable = 2;                   // error (variable can't be redefined)
```

#### Scopes

```javascript
var a = 1;

{
    print(a);           // 1
    a = a + 1;
    print(a);           // 2

    var c = 10;
}

print(a);               // 2
print(c);               // error
```

### Comments

```javascript
// Comment starts with a double-slash (`//`) symbol and ends with the new line.

var number = -5;
var maxNumber = 10;
var minNumber = 0;

// Limit the number
if (number > maxNumber) {
    number = maxNumber;     // If greater than the high limit, set to max value
}
if (number < minNumber>) {
    number = minNumber;     // If less than the low limit, set to min value
}
```

### If

```javascript
var a;
var b;

if (b = someCondition or not otherCondition) a = true;
else a = false;

if (b = someCondition == false and otherCondition) {
    a = true;
    print(b);           // true
} else {
    a = false;
    print(b);           // false
}
```

### While

```javascript
var a = 0;

while (a < 10) a = a + 1;

while (a < 20) {
    a = a + 1;
    print(a)
}

```

### Functions

#### Declaration

```Rust
fn getSum(a, const b) {
    a = a + 1;
    b = b + 1;                  // Error
    return a + b;
}
```

#### Nested functions

```Rust
fn getSum(a, b) {
    var outside = a + b;

    fn inner() {
        return outside + 1
    }

    return inner();
}

fn wrapper(a) {
    return a;
}

wrapper(getSum)(5, 3)   // returns 9
```

#### Recursion

```javascript
fn fib(const n) {
    if (n <= 1) return n;
    return fib(n - 2) + fib(n - 1);
}

var i = 0;
while (i < 20) {
    print(fib(i));
}
```

#### Overriding

```javascript
fn name() {
    print("John");
}

name();                 // "John"

fn name() {
    print("Jane");
}

name();                 // "Jane"

name = "Doe";
print(name);            // "Doe"
```

#### Scopes

```javascript
var a = 0;

fn add(value) {
    a = 1;
    value = 1;
    fn inner() {
        value = 2;
    }
    print(value);           // 2
    b = 1;                  // Error (b not declared)
}

fn main() {
    var b = 0;
    var value = 0;
    add(value);
    print(a);               // 1 (the value was modified inside the function)
    print(value);           // 0 (arguments are passed by value, not by reference)
}
```

### Pattern matching

```
match (2+2) {
   (Num and >4 as number): print(number + " is greater than four.");
   (_ as number): {
        print(number + " is less than two");
        number = number + 1;                        // error (number is constant)
   }
}

print(number)                                 // error (number is unbound)
```

```
match (number) {
    (==0): print("Nothing");
    (==1): print("Just one");                 // equals to (==true):
    (==2): print("A couple");
    (==-1): print("One less than nothing");
    (_): print("Unknown");
}
```

#### Match expression

```
match (a, b, c) {}

match ("John", 25, true, someFunc(), anotherFunc, nil) {}
```

#### Compare pattern

```
match (number) {
    (==0): {}
    (==1): {}
    (>1): {}
    (<-100): {}
    (!=100): {}
    (==true): {}
    (==not true as result): {}
    (=="string"): {}
    (==nil): {}
    (==someFunc()): {}
    (==(someFunc() and 1+1>5 or true) or ==false as result): {}
}
```

#### Type pattern

```
match (input1, input2) {
    (Str as name, Num as age): {
        print("name is " + name);
        print("age is " + name);
    }
    (Num as age, Str as name): {
        print("name is " + name);
        print("age is " + name);
    }
    (_, _): print("Invalid input");
}
```

#### Guard

```
match ("John") {
    (Str as name) if someFunction(name): print("Hello" + name);
    (_): print("Hello!");
}
```

#### Examples

```
match ("John", 10) {
    (Str as name, Num and <30) if (age < 30): print(name + " is young.");
    (Str as name, Num and >30 and <60): print(name + " is in middle age");
    (Str as name, Num): print(name + " is old");
    (_, _): print("Invalid input");
}
```

```
match (x, y) {
    (Num and >0, Num and >0 ): print("first");
    (Num and <0, Num and >0): print("second);
    (Num and <0, Num and <0): print("third");
    (Num and >0, Num and <0): print("fourth");
    (Num and ==0, Num): print("on Y");                                // Not the same as (==0, Num) pattern
    (Num, Num): print("on X");
    (_ as x, _ as y): print("Invalid coords: " + x + ", " + y);
}
```

## Grammar

The grammar is in [this](./grammar.ebnf) file.

## Error handling

If the error was found while scanning the source - the lexer reports an error, but it doesn't stop, it keeps scanning.

If the error was found while parsing - the parser reports an error and uses a technique called *error recovery* to try and continue parsing the code.

The error message structure looks like this:
```
<Error Type>: <Error message>

    <line number> | <place where error occured>
```

For example:
```
ZeroDivisionError: division by zero

    15 | var number = 15 / 0;
```

## How to run

To run the interpreter use following syntax:
```sh
python3 interpreter.py [filepath]
```

Where `interpreter.py` is a path to the interpreter and `filepath` is a path to the file with the source code.

If `filepath` is not given, the interpreter will be run interactively.

## Implementation

As it's a *tree-walk interpreter*, it has three main parts: **Lexer**, **Parser**, **Interpreter**. For convenience, an interpreter is divided into two more modules: **error handling** and **input reader**. This will make interpreter more flexible and will allow to change the interpreter behavior simply by replacing one of the modules.

#### Error handling

This module is responsible for handling an errors on different stages of interpreting.

The representation of this module is a class that implements the interface:

```python
class ErrorHandler:
    def handle_lexer_error(self, exception: LexerError):
        ...

    def handle_parser_error(self, exception: ParserError):
        ...

    def handle_interpreter_error(self, exception: InterpreterError):
        ...
```

Each type of error should implement this interface:
```python
class Position:
    line: int
    column: int
    offset: int

class Exception:
    position: Position
    message: str
```

These fields are required to build a user-friendly error message.

#### Input reader

This module is responsible for reading an input and provide lexer with the stream of characters.

An input reader should implement this interface:
```python
class InputReader:
    position: Position

    def advance(self) -> str:
        ...
```

`advance()` method is responsible for moving forward in source by one character. It also keeps track of the current position in the source, so that it can be passed to the token or error handler.

#### Lexer

A **lexer** (or **scanner**) takes a stream of characters and groups it into **tokens**. Because there is an additional layer for reading source, lexer doesn't interact with the source, it uses an input reader it got during initialization to move in the code.

The interface of the scanner is the following:
```python
class Scanner:
    input_reader: InputReader
    error_handler: ErrorHandler

    def next_token(self) -> Token:
        ...
```

A `Token` is a class that represents a token built from the characters. Its interface is the following:
```python
class Token:
    type: TokenType
    value: int | float | str | None
    position: Position
```

If it represents a **literal** (identifier, string or number), than it has a value. Otherwise, if it represents a **keyword** or other **operator** - it's value is `None`.

#### Parser

A parser takes the flat sequence of **tokens** and builds a **tree** structure using **recursive descent** method. It also defines a type an a precedence of the node based on the grammar rules.

```python
class Parser:
    scanner: Scanner

    def parse(self) -> Statement:
        ...
```

Where `Statement` is a base class for language's statements defined in the [grammar](./grammar.ebnf) file. A `Statement` might also contain an `Expression` object.

To handle errors, parser uses `error_handler` object that is present in the `scanner` instance.

#### Interpreter

Interpreter's job is to apply static analysis to the **AST** and execute the code. To run the program, the interpreter traverses the syntax tree one branch and leaf at a time, evaluating each node as it goes.

## Testing

There will be a set of unit tests for each module and integration tests to verify how modules work together. Acceptance testing will also be applied for testing the whole interpreter against prepared examples.
