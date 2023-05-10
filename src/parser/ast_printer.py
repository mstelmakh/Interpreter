from parser.data import BinaryExpr, Visitor


class AstPrinter(Visitor):
    def visit_binary(expr: BinaryExpr):
        pass
