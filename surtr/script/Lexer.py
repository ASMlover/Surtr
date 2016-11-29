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
    TokenType.ERROR: '<ERROR>',
    TokenType.EOF: '<EOF>',

    TokenType.COMMENT: '<COMMENT>',
    TokenType.LPAREN: '<LPAREN>',
    TokenType.RPAREN: '<RPAREN>',
    TokenType.COMMA: '<COMMA>',

    TokenType.STRING: '<STRING>',
    TokenType.IDENTIFIER: '<IDENTIFIER>',
}

class Token(object):
    def __init__(self, text, type=TokenType.ERROR, line=0):
        self.value = text
        self.type = type
        self.line = line

    def __str__(self):
        type_text = TokenNames.get(self.type, '<INVALID>')
        return '>>>>>>>>>> {value: "%s", type: %s, line: %d}' % (self.value, type_text, self.line)

class LexerException(Exception):
    def __init__(self, message, lineno):
        self.message = message
        self.lineno = lineno

    def __str__(self):
        return 'Error at line(%d) - %s' % (self.lineno, self.message)

class Lexer(object):
    def __init__(self, content=''):
        self.content = content
        self.pos = 0
        self.lineno = 1

    def get_char(self):
        if self.pos >= len(self.content):
            return None

        c = self.content[self.pos]
        self.pos += 1
        return c

    def unget_char(self):
        assert self.pos > 0, 'Lexer pos can not be neigative'
        self.pos -= 1

    def skip_line_comment(self):
        while True:
            c = self.get_char()
            if c is None or c == '\r' or c == '\n':
                if c == '\r' or c == '\n':
                    if c == '\r' and self.get_char() != '\n':
                        self.unget_char()
                    self.lineno += 1
                break

    def get_string(self):
        char_list = []
        while True:
            c = self.get_char()
            if c is None or c == '\r' or c == '\n':
                if c == '\r' and self.get_char() != '\n':
                    self.unget_char()
                raise LexerException('need close const string symbol `"`', self.lineno)
            elif c == '"':
                return Token(''.join(char_list), TokenType.STRING, self.lineno)
            else:
                char_list.append(c)

    def get_identifier(self):
        self.unget_char()

        char_list = []
        while True:
            c = self.get_char()
            if str.isalnum(c) or c == '_':
                char_list.append(c)
            else:
                self.unget_char()
                return Token(''.join(char_list), TokenType.IDENTIFIER, self.lineno)

    def get_token(self):
        while True:
            c = self.get_char()
            if c is None:
                return Token(None, TokenType.EOF, self.lineno)
            elif c in (' ', '\t',):
                continue
            elif c == '\r':
                if self.get_char() != '\n':
                    self.unget_char()
                self.lineno += 1
            elif c == '\n':
                self.lineno += 1
            elif c == '#':
                self.skip_line_comment()
            elif c == '"':
                return self.get_string()
            elif str.isalpha(c) or c == '_':
                return self.get_identifier()
            elif c == ',':
                return Token(',', TokenType.COMMA, self.lineno)
            elif c == '(':
                return Token('(', TokenType.LPAREN, self.lineno)
            elif c == ')':
                return Token(')', TokenType.RPAREN, self.lineno)
            else:
                return Token(None, TokenType.ERROR, self.lineno)

if __name__ == '__main__':
    with Utils.do_open("demo.su", mode='r', encoding='utf-8') as fp:
        content = fp.read()
        lex = Lexer(content)

        while True:
            tok = lex.get_token()
            if tok.type in (TokenType.ERROR, TokenType.EOF):
                break
            print (tok)
