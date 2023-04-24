import pytest

from lexer.streams import TextStream, FileStream


TEST_SAMPLES = (
    (
        "// Basic arithmetics\n",
        "8 / 4 * 1 + 1               = 3\n",
        "8 / 4 * (1 + 1)             = 4\n",
        "8 / (4 * (1 + 1))           = 1\n",
        "15.5 / 7.75                 = 2.0\n",
        "2.36 - 5 * -1               = 7.36",
    ),
    (
        '// On Booleans\n',
        'true + true                 = 2     // true is coerced to 1\n',
        'false + false               = 0     // false if coerced to 0\n',
        'true + false = false + true = 1\n',
        '// On Numbers\n',
        '4 + 6                       = 10\n',
        '"5" + 3                     = 53    // "5" is coerced to number\n',
        '7 + "2.5"                   = 72.5  // "2.5" is coerced to number\n',
        '7 + "2a"                    = "72a" // "2a" can not be coerced to number\n',
        '// On Functions\n',
        '// functions are converted to string containing its name\n',
        '"function " + someFunction  = "function: someFunction"\n',
        '1 + function123             = "1function123"\n',
        '// Operator "-" is used only for numerical substraction\n',
        '7 - "2" = "7" - 2           = 5     // string is coerced to number\n',
        '10 - ""                     = 10    // empty string is coerced to 0\n',
        '10 - "foo"                          // error\n',
        '// On Strings\n',
        '"hello" + "world"           = "helloworld"\n',
        '"The answer is: " + 12      = "The answer is: 12"\n',
        '"The answer is " + true     = "The answer is true"\n',
    ),
    (
        'const a = "string";\n',
        'var b;                              // nil\n',
        'b = 5;\n',
        'print(b);                           // 5\n',
        'a = 6                               // error\n',
        'var variable = "one";\n',
        'print(variable)                     // "one"\n',
        'var variable = 2;                   // error (variable cant be redefined)\n'
    ),
    (
        "€var = 15;!\n",
        "match (input1, input2) {~\n",
        ">   (Str as name, Num as age): {\n",
        '       print("name is " + name);\n',
        '       print("age is " + name);\n',
        "   }\n",
        "   (Num as age, Str as name): {\n",
        '       pri&nt("name is " + name);\n',
        '       print("age is " + name);\n',
        "   }\n",
        '   (_, _): print("Invalid input");\n',
        "}",
    ),
)


def _test_stream(stream, text):
    assert stream.current_char == ''
    assert stream.position.line == 1
    assert stream.position.column == 0
    assert stream.position.offset == 0

    offset = 0
    for line_n, line in enumerate(text):
        for col_n, char in enumerate(line):
            stream.advance()
            assert stream.current_char == char
            assert stream.position.line == line_n + 1
            assert stream.position.column == col_n + 1
            assert stream.position.offset == offset
            offset += len(stream.current_char.encode('utf-8'))


@pytest.mark.parametrize('text', TEST_SAMPLES)
def test_text_stream(text):
    stream = TextStream("".join(text))
    _test_stream(stream, text)


@pytest.mark.parametrize('text', TEST_SAMPLES)
def test_file_stream(text, tmpdir):
    file = tmpdir.join("test.txt")
    file.write("".join(text))
    with open(file, "r") as f:
        stream = FileStream(f)
        _test_stream(stream, text)
