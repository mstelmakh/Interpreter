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
- **Numbers.** The language will have only two kinds of numbers: `int` and `float`.
- **Strings.** The strings are enclosed in double quotes. Escape character (`\`) allows to insert special characters in strings.
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

Because of the fact, that the language is weakly typed, some operations can be also performed on different operand types by coercing them to common type supported by the operator. Some examples:
```JavaScript
// On Booleans
true + true                 = 2     // true is coerced to 1
false + false               = 0     // false if coerced to 0
true + false = false + true = 1

// On Numbers
4 + 6                       = 10
"5" + 3                     = "53"
7 + "2"                     = "72"

// Operator "-" is used only for numerical substraction
7 - "2" = "7" - 2           = 5     // string is coerced to number
10 - ""                     = 10    // empty string is coerced to 0
10 - "foo"                          // error

// On Strings
"hello" + "world"           = "helloworld"
"The answer is: " + 12      = "The answer is: 12"
"The answer is " + true     = "The answer is true"
```

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

2. If operator is `==` and one of the operands is `nil`, the other must also be `nil` to return true. Otherwise return false.

3. Because the language is weakly typed, when comparing values of different types, the interpreter will attempt to coerce the values to a common type using the type coersion rules:
    - If one of the operands is `nil`, convert `nil` to 0. Then compare two operands again.
    - If one of the operands is a Boolean, convert the boolean to a number: true is converted to 1, and false is converted to 0. Then compare two operands again.
    - Number to string: the string is converted to a number if possible. If the string cannot be converted to a number, the comparison will always return false.

#### Logical operators

There are three logical operators used:
- **!** - the NOT operator, returns `false` if its operand is `true`, and vice versa.
- **and** - determines if two values are both `true`. It doesn't evaluate the right operand if the left one is `false`.
- **or** - determines if either of two values (or both) are `true`. It doesn't evaluate the right operand if the left one is `true`.

#### Grouping

To change the order of precedence in arithmetic expressions, the parentheses `()` can be used to group sub-expressions. The expressions inside parentheses are evaluated first before the rest of the expression, regardless of the usual operator precedence.

### Statements

The language uses a semicolon (`;`) to mark the end of the statement.

To pack a series of statements, the **block** (`{}`) syntax is used.

### Variables

The keyword `var` is used to declare a variable. The variable without a value defaults to `nil`.
```JavaScript
var a = "string";
var b;  // nil
```
Because the variables are mutable by default, their value can be changed. To declare a constant variable, that can not be modified, use the keyword `const`.
```JavaScript
const a = 5;
a = 6           // Throws an error
```

Because of the dynamic typing, the data types of variables are determined at runtime, rather than at compile time. It means that there is no need to specify the data type of a variable explicitly when declaring it, and its data type can be changed by assigning a value of a different type to it.

For example:
```JavaScript
var variable = "John";
variable = 10;
```

### Comments

Comment starts with a double-slash (`//`) symbol and ends with the new line.

```JavaScript
// Limit the number
if (number > maxNumber) {
    number = maxNumber;     // If greater than the high limit, set to max value
}
if (number < minNumber>) {
    number = minNumber;     // If less than the low limit, set to min value
}
```

### Control flow

There are three ways of controlling the flow of the program:

**if** - executes the block of statements based on the condition.
```JavaScript
var a;
if (someCondition) {
    a = true;
} else {
    a = false;
}
```

**while** - executes the block of statements while the condition evaluates to `true`.
```JavaScript
var a = 0;

while (a < 10) {
    a = a + 1;
}
```

**for** - it is a C-style loop, that gets three arguments: initialization, condition and the statement executed at the end of each iteration.
```JavaScript
for (var a = 1; a < 10; a = a + 1) {
    // Code here
}
```

### Functions

The function declaration looks like this:
```Rust
fn getSum(a, b) {
    return a + b;
}
```

Where `fn` is the keyword to declare a function.

If the function doesn't have a `return` statement, it returns `nil`.

To call a function use the following syntax:
```JavaScript
someFunction(5, 5);

// Or without arguments
someFunction();
```
<!-- TODO -->
<!-- By default arguments are passed by their values, so the original object can not be modified inside the function. To pass the argument as a reference to the object, use the symbol `$` before the agument.
```JavaScript
fn incrementNumber($a) {
    a = a + 1;
}

var a = 2;

incrementNumber($a);      // a = 3
``` -->

Function can be passed to another function, as well as it can be declared in another function.
Example:
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

## Code examples
### Hello world
```javascript
print("hello world");
```
### Arithmetic

```javascript
var a = 5;
var b = 7.2;
var c = "3";

var sum = a + b; // 12.2
var product = a * b; // 36
var division = b / a; // 1.44
var difference = b - a; // 2.2
var stringConcat = "The result is: " + product; // "The result is: 36"
var mixedAddition = a + c; // "53" (because c is a string, it is concatenated to a as a string)
```

### Strings

```javascript
var firstName = "John";
var lastName = "Doe";
var fullName = firstName + " " + lastName; // "John Doe"
```

### Comparisons

```javascript
var a = 5;
var b = 10;
var c = "5";

var isEqual = a == c; // true (c is coerced to a number before comparison)
var isNotEqual = a != b; // true
var isLessThan = a < b; // true
var isGreaterThan = b > c; // true (c is coerced to a number before comparison)
var isLessThanOrEqual = a <= 5; // true
var isGreaterThanOrEqual = b >= 10; // true
var andResult = (a == 5) and (b == 10); // true
var orResult = (a == 5) or (b == 5); // true
var notResult = !(a == b); // true
```

### Conditional statement

```javascript
var a = 5;
var b = 7;

if (a > b) {
  print("a is greater than b");
} else {
  print("a is not greater than b");
}

if (a == b) print("a is equal to b");

```
### Loops
```javascript
var i = 0;
while (i < 5) {
  print("The value of i is " + i);
  i = i + 1;
}

for (var j = 0; j < 5; j++) {
  print("The value of j is " + j);
}
```
### Functions

```javascript
fn add(a, b) {
  return a + b;
}

fn fib(n) {
    if (n <= 1) return n;
    return fib(n - 2) + fib(n - 1);
}

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


var result = add(5, 10); // 15
print(result);

for (var i = 0; i < 20; i = i + 1) {
    print(fib(i));
}

wrapper(getSum)(5, 3)   // returns 9
```

## Grammar

```ebnf
```

## Error handling

## How to run

## Expected implementation

## Testing