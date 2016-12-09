#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2016 ASMlover. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list ofconditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materialsprovided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import Utils

TokenType = Utils.enum_def(
    'ERROR',
    'EOF',

    # syntax symbols
    'COMMENT', # `#` - only line comment
    'LPAREN', # `(`
    'RPAREN', # `)`
    'COMMA', # `,`

    # syntax reserved keywords

    # custom definitons
    'STRING', # const string
    'IDENTIFIER', # user identifier (variables or functions)
)

TokenNames = {
    TokenType.ERROR: 'TK_ERROR',
    TokenType.EOF: 'TK_EOF',

    TokenType.COMMENT: 'TK_COMMENT',
    TokenType.LPAREN: 'TK_LPAREN',
    TokenType.RPAREN: 'TK_RPAREN',
    TokenType.COMMA: 'TK_COMMA',

    TokenType.STRING: 'TK_STRING',
    TokenType.IDENTIFIER: 'TK_IDENTIFIER',
}

class Token(object):
    def __init__(self, text, type=TokenType.ERROR, line=0, col=0):
        self.value = text
        self.type = type
        self.line = line
        self.col = col

    def __str__(self):
        type_text = TokenNames.get(self.type, 'TK_INVALID')
        return '|%s|%s|%s|%s|' % (self.value.center(32),
                type_text.center(16), str(self.line).center(8), str(self.col).center(8))

class LexerException(Exception):
    def __init__(self, message, lineno, column):
        self.message = message
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return 'Error at line(%d:%d) - %s' % (self.lineno, self.column, self.message)

class Lexer(object):
    def __init__(self, content=''):
        self.content = content
        self.lexpos = 0
        self.lineno = 1
        self.column = 0

    def get_char(self):
        if self.lexpos >= len(self.content):
            return None

        c = self.content[self.lexpos]
        self.lexpos += 1
        self.column += 1
        return c

    def unget_char(self):
        assert self.lexpos > 0, 'Lexer posistion can not be neigative'
        self.lexpos -= 1
        self.column -= 1

    def make_token(self, tok_type, value=None, line=None, col=None):
        if line is None:
            line = self.lineno
        if col is None:
            col = self.column
        return Token(value, tok_type, line, col)

    def skip_line_comment(self):
        while True:
            c = self.get_char()
            if c is None or c == '\n':
                self.unget_char()
                break

    def get_string(self):
        char_list = []
        begin_col = self.column
        while True:
            c = self.get_char()
            if c is None or c == '\n':
                raise LexerException('need close const string symbol `"`', self.lineno)
            elif c == '"':
                return self.make_token(TokenType.STRING, ''.join(char_list), col=begin_col)
            else:
                char_list.append(c)

    def get_identifier(self, c):
        char_list = []
        begin_col = self.column
        while True:
            if str.isalnum(c) or c == '_':
                char_list.append(c)
            else:
                self.unget_char()
                return self.make_token(TokenType.IDENTIFIER, ''.join(char_list), col=begin_col)
            c = self.get_char()

    def get_token(self):
        while True:
            c = self.get_char()
            if c is None:
                return self.make_token(TokenType.EOF)
            elif c in (' ', '\t',):
                continue
            elif c == '\n':
                self.lineno += 1
                self.column = 0
            elif c == '#':
                self.skip_line_comment()
            elif c == '"':
                return self.get_string()
            elif str.isalpha(c) or c == '_':
                return self.get_identifier(c)
            elif c == ',':
                return self.make_token(TokenType.COMMA, c)
            elif c == '(':
                return self.make_token(TokenType.LPAREN, c)
            elif c == ')':
                return self.make_token(TokenType.RPAREN, c)
            else:
                return self.make_token(TokenType.ERROR)

if __name__ == '__main__':
    with open("demo.sc", mode='r') as fp:
        content = fp.read()
        lex = Lexer(content)

        index = 0
        print ('+%s+%s+%s+%s+%s+' % ('NUM'.center(4), 'IDENTIFIER'.center(32),
            'TOKEN'.center(16), 'ROW'.center(8), 'COL'.center(8)))
        while True:
            tok = lex.get_token()
            if tok.type in (TokenType.ERROR, TokenType.EOF):
                break
            print ('|%s%s' % (str(index).center(4), tok))
            index += 1
