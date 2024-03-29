#!/usr/bin/env python2.7
#
# Original can be found at http://rosettacode.org/wiki/S-Expressions#Python
#

import re

dbg = False

# We're using regex expressions to define our grammar, short explanation of these:
# (?mx) sets the further syntax of the re, ?mx means multi-line and verbose, so \n won't be a problem
# \s* matches all the whitespace
# (?:...) Matches whatever regular expression is inside the paretheses, it will return a capturing-group like this:
# For example (?:aaa)(_bbb) would return for the string aaa_bbb the group (aaa_bbb, _bbb), this is useful to iterate through the s-expression.
# (?P<name>...) the substring matched by it, will be accessible through the name in the <name>-tag, for example:
# take the re reg = (?P<id>[a-zA-Z_]\w*), and the string s = "a1234", the function match = re.match(reg,s) would return an MatchObejct,
# you could acces it like match.group('id'), this would return "a1234".
# <sq>"[^"]*" matches all strings except ", we won't ever get this, its for s-expressions like (string "abcdef") .
# <s>\S+ matches any non-whitespace character
# \b matches whitespace at the end of a string

term_regex = r'''(?mx)
    \s*(?:
        (?P<brackl>\()|
        (?P<brackr>\))|
        (?P<num>\-?\d+\.\d+e\-?\d+|\-?\d+\.\d+|\-?\d+)|
        (?P<sq>"[^"]*")|
        (?P<s>\S+)
       )'''

def parse_sexp(sexp):
    sexp = "("+sexp+")"
    sexp = sexp.replace('(',' ( ').replace(')',' ) ')
    stack = []
    out = []
    if dbg: print("%-6s %-14s %-44s %-s" % tuple("term value out stack".split()))
    # re.finditer returns an iterater of all the matches (as MatchObject) as they are found from left to right
    # termtype has the type Matchobject
    for termtypes in re.finditer(term_regex, sexp):
        # .groupdict() returns a dictionary of all the named subgroups of the match, keyed by the subgroup name.
        # Example: re.match("(?P<id>\w*)","2222").groupdict() would return {'id':'2222'}
        # the rest of the logic is used for desturing, so that term becomes 'id' and value becomes '2222'
        term, value = [(t,v) for t,v in termtypes.groupdict().items() if v][0]
        if dbg: print("%-7s %-14s %-44r %-r" % (term, value, out, stack))
        # The term is the name of the rule that matched, just check which rule matched and do the appropriate actions
        # only brackl and brackr are interesting, here we are doing some stack-logic to get the nesting into our parsed datastructure
        if   term == 'brackl':
            stack.append(out)
            out = []
        elif term == 'brackr':
            assert stack, "Trouble with nesting of brackets"
            tmpout, out = out, stack.pop(-1)
            out.append(tmpout)
        elif term == 'num':
            v = float(value)
            if v.is_integer(): v = int(v)
            out.append(v)
        elif term == 'sq':
            out.append(value[1:-1])
        elif term == 's':
            out.append(value)
        else:
            raise NotImplementedError("Error: %r" % (term, value))
    assert not stack, "Trouble with nesting of brackets"
    result = out[0]
    if len(result) == 1 and result[0].__class__.__name__ == 'list':
        result = result[0]
    return result

def print_sexp(exp):
    out = ''
    if type(exp) == type([]):
        out += '(' + ' '.join(print_sexp(x) for x in exp) + ')'
    elif type(exp) == type('') and re.search(r'[\s()]', exp):
        out += '"%s"' % repr(exp)[1:-1].replace('"', '\"')
    else:
        out += '%s' % exp
    return out


if __name__ == '__main__':
    # sexp = '''(time (now 3.58))(GS (unum 1) (team left) (t 0.00) (pm BeforeKickOff))(GYR (n torso) (rt -0.00 -0.00 -0.00))(ACC (n torso) (a -0.00 -0.00 29.42))(HJ (n hj1) (ax 0.00))(HJ (n hj2) (ax -0.00))(HJ (n raj1) (ax -0.00))(HJ (n raj2) (ax -0.00))(HJ (n raj3) (ax -0.00))(HJ (n raj4) (ax 0.00))(HJ (n laj1) (ax 0.00))(HJ (n laj2) (ax 0.00))(HJ (n laj3) (ax 0.00))(HJ (n laj4) (ax -0.00))(HJ (n rlj1) (ax 0.00))(HJ (n rlj2) (ax -0.00))(HJ (n rlj3) (ax -0.00))(HJ (n rlj4) (ax 0.00))(HJ (n rlj5) (ax -0.00))(HJ (n rlj6) (ax -0.00))(HJ (n llj1) (ax -0.00))(HJ (n llj2) (ax 0.00))(HJ (n llj3) (ax -0.00))(HJ (n llj4) (ax 0.00))(HJ (n llj5) (ax 0.00))(HJ (n llj6) (ax -0.00))'''
    # sexp = "(((foo)))"
    sexp = '''(bla 1.3678e-005)'''


    print('Input S-expression: %r' % (sexp, ))
    parsed = parse_sexp(sexp)
    print("\nParsed to Python:", parsed)

    print("\nThen back to: '%s'" % print_sexp(parsed))

