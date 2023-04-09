from lexer.streams import TextStream


def test_text_stream():
    text = (
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
    )
    stream = TextStream("".join(text))
    assert stream.current_char == ''
    assert stream.position.line == 1
    assert stream.position.column == 0

    for line_n, line in enumerate(text):
        for col_n, char in enumerate(line):
            stream.advance()
            assert stream.current_char == char
            assert stream.position.line == line_n + 1
            assert stream.position.column == col_n + 1
