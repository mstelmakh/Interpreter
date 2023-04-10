import pytest

from lexer.streams import TextStream, FileStream


TEST_SAMPLES = (
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
