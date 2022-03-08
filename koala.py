

TT_INT = 'INTEGER'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'ADD'
TT_MINUS = 'MINUS'
TT_MUL = 'MULTIPLY'
TT_DIV = 'DIVIDE'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
DIGITS = '0123456789'


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.error_name = error_name
        self.details = details
        self.pos_start = pos_start
        self.pos_end = pos_end

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f' in File: {self.pos_start.fn}, Line: {self.pos_start.ln + 1}'
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class IllegalSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Syntax', details)


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if (self.value):
            return f'{self.type} : {self.value}'
        return f'{self.type}'


class Position:
    def __init__(self, index, ln, col, fn, ftxt):
        self.index = index
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, curr_char):
        self.index += 1
        self.col += 1

        if (curr_char == "\n"):
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.index, self.ln, self.col, self.fn, self.ftxt)


class Lexer:
    def __init__(self, text, fn):  # constructor for Lexer, takes in a string
        self.text = text
        self.fn = fn
        self.pos = Position(-1, 0, -1, fn, text)
        self.curr_char = None
        self.advance()

    def advance(self):  # method to iterate through string
        self.pos.advance(self.curr_char)
        self.curr_char = self.text[self.pos.index] if self.pos.index < len(
            self.text) else None

    def make_tokens(self):
        tokens = []

        while (self.curr_char != None):
            if (self.curr_char in ' \t'):
                self.advance()
            elif (self.curr_char in DIGITS):
                tokens.append(self.make_number())
            elif (self.curr_char == '+'):
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif (self.curr_char == '-'):
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif (self.curr_char == '/'):
                tokens.append(Token(TT_DIV))
                self.advance()
            elif (self.curr_char == '*'):
                tokens.append(Token(TT_MUL))
                self.advance()
            elif (self.curr_char == '('):
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif (self.curr_char == ')'):
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.curr_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while (self.curr_char != None and self.curr_char in DIGITS + '.'):
            if (self.curr_char == '.'):
                if (dot_count == 1):
                    break
                else:
                    dot_count += 1
                    num_str += '.'
            else:
                num_str += self.curr_char
            self.advance()

        if (dot_count == 0):
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.advance()

    def advance(self):
        self.tok_index += 1

        if (self.tok_index < len(self.tokens)):
            self.curr_tok = self.tokens[self.tok_index]

        return self.curr_tok

    def parse(self):
        res = self.expr()
        return res

    def factor(self):
        tok = self.curr_tok

        if (tok.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return NumberNode(tok)

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        left = func()

        while (self.curr_tok.type in ops):
            op_tok = self.curr_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)

        return left


def run(fn, text):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()

    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None
