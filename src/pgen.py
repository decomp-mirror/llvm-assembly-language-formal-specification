# Copyright (c) 2011, MIPS Technologies, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions, and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions, and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of MIPS Technologies, Inc. nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL MIPS TECHNOLOGIES, INC. BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES,
# LOSS OF USE, DATA, OR PROFITS, OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."

'''
Created on Aug 15, 2011

@author: rkotler
'''
import re
from optparse import OptionParser

parser = OptionParser()
(options, args) = parser.parse_args()

lexpattern = r"""
(?P<whitespace>\s+)
|(?P<comment>\#.*)   
|(?P<list>list)
|(?P<grammar>grammar)                 
|(?P<nonterminal>\w+)
|(?P<pseudo_terminal>\'\<[^']+\>\')                   
|(?P<terminal>\'[^']+\')            
|(?P<semicolon>[;])                    
|(?P<star>\*)                   
|(?P<plus>\+)
|(?P<question>\?)
|(?P<bar>\|)
|(?P<lparen>\()
|(?P<rparen>\))
|(?P<lbrace>\{)
|(?P<rbrace>\})
|(?P<defined>\-\>)              
"""

pos = 0


token_re = re.compile(lexpattern, re.VERBOSE)

tokens = []

lines_array = [""]

read_index = 0

nonterminal_definitions = {}

nonterminal_references = {}

pseudo_terminal_definitions = {}

pseudo_terminal_references = {}

trace_parse = True

def do_trace_parse(text):
    if trace_parse:
        print text

def add_nonterminal_reference(text):
    print "add nonterminal reference"
    name = text[1]
    if name in nonterminal_references:
        pass
    else:
        nonterminal_references[name] = [[text[2], text[3]]]
    print "adding nonterminal reference", name
    
def next_token():
    return tokens[read_index][0]

def next_token_text():
    return tokens[read_index][1]

def next_token_line():
    return tokens[read_index][2]

def next_token_column():
    return tokens[read_index][3]

def next_token_full():
    return tokens[read_index]

def lookead(n):
    return tokens[read_index + n - 1][0]

def advance_token():
    global read_index
    print "consumed:", next_token_full()
    read_index = read_index + 1
    
def error_here():
    global lines_array
    print "error: ", next_token_line(), lines_array[next_token_line()] 
    carrots = ''
    for i in range(1,7+next_token_column()):
        carrots = carrots + '.'
    print carrots + '^';
      
def expect(text):
    #print 'type: ', type(text)
    if (type(text) is str):
        text  =  [text]
    for t in text:
        if (next_token() == t):
            #print 'as expected: ', t
            return
    error_here()
    print 'expected: ', text
    for t in text:
        print '  ', t
    print 'read: ', next_token()
    advance_token()
    raise NameError(text)
        
def parser():
    if (next_token == 'grammar'):
        parse_grammar()
    pass

def parse_grammar():
    expect('grammar')
    advance_token()
    expect('nonterminal')
    advance_token()
    expect('lbrace')
    advance_token()
    while (next_token() != "rbrace"):
        parse_rule()
    advance_token()    
        
def parse_rule():
    do_trace_parse("parsing rule")
    expect(['nonterminal', 'pseudo_terminal', 'lparen',  'bar', 'list'])
    if (next_token() == 'nonterminal'):
        nonterminal_definitions[next_token_text()] = \
            [next_token_line(), next_token_column()]
    elif (next_token() == 'pseudo_terminal'):
        pseudo_terminal_definitions[next_token_text()] = \
            [next_token_line(), next_token_column()]


    advance_token()
    while (next_token() == 'defined'):
        advance_token()
        if (next_token() == 'semicolon'):
            exit
        if (next_token() != 'defined'):    
            parse_rhs()
    expect("semicolon")
    advance_token()
        
def parse_rhs():
    do_trace_parse("parse_rhs")

    while (next_token() != 'semicolon' and next_token() != 'rparen'
           and next_token() != 'defined'):
        parse_rhs_element()
    pass
        
def parse_rhs_element():
    do_trace_parse("parse_rhs_element")
    expect(['nonterminal', 'terminal', 'pseudo_terminal', 'lparen',
            'bar', 'list'])
    if (next_token() == 'nonterminal') or \
       (next_token() == 'terminal') or \
       (next_token() == 'pseudo_terminal'):
        if (next_token() == 'nonterminal'):
            add_nonterminal_reference(next_token_full())
        advance_token()
        if (next_token() == 'star') or (next_token() == 'plus') \
            or (next_token() == 'question'):
            advance_token()
            print 'after star' , next_token()
    elif (next_token() == 'lparen'):
        advance_token()
        parse_rhs()
        expect('rparen')
        advance_token()
        if (next_token() == 'star') or (next_token() == 'plus') \
            or (next_token() == 'question'):
            advance_token()
            print 'after star' , next_token()
 

    if (next_token() == 'bar'):
        advance_token()
        parse_rhs_element()
    elif (next_token() == 'list'):
        advance_token()
        parse_rhs_element()
                   
for arg in args:
    f = open(arg, 'r')
    global lines_array
    lines = f.readlines()
    line_num = 1;
    for line in lines:
        lines_array.append(line)
        #print line,
        print line_num, line,
        line_num = line_num + 1
        pos = 0
        while True:
            m = token_re.match(line, pos)
            #print m
            if not m: break
            #print pos, m.end()
            tokname = m.lastgroup
            tokvalue = m.group(tokname)
            if (tokname != "whitespace") and (tokname != "comment"):
                # print tokname, tokvalue
                tokens.append ([tokname, tokvalue, line_num, pos])
            pos = m.end()
        if pos != len(line):
            print "tokenizer stopped at", line, pos
tokens.append (['<$>', '<$>', line_num, pos])

#print "lines"
#for i in lines_array:
#    print i,

print "tokens"
for i in tokens:
    print i

print ""
print "grammar parse"
print "_____________"

parse_grammar()

print ""
print ""
print "non terminals"
print "_____________"

for i in nonterminal_definitions:
    print i    

print ""
print ""
print "non terminal references"
print "_____________"
for i in nonterminal_references:
    print i 
    
print ""
print ""
print "pseudo terminals"
print "_____________"

for i in pseudo_terminal_definitions:
    print i    

print ""
print ""
print "undefined nonterminals"
for i in nonterminal_references:
    if i not in nonterminal_definitions:
        print "reference to undefined nonterminal: ", i
