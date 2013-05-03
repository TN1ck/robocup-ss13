#!/usr/bin/env python2.7

# test with "cat <some_file> | ./parser.py"
# e.g. cat example_s_expr.txt | ./ parser.py

import re
from collections import namedtuple

# Some data structures
Token = namedtuple('Token', ['name', 'value'])
RuleMatch = namedtuple('RuleMatch', ['name', 'matched'])
Entry = namedtuple('Entry', ['name', 'value'])

# Maps characters to token names.
# The NUM and STR tokens are not included here.
# They are special cases.
token_map = {
  '(':'LPAR', ')':'RPAR',
}

# The rules of the parser itself. It works recursively.
rule_map = {
  'list': [
    'LPAR STR tail RPAR',
  ],
  'tail': [
    'list tail',
    'list',
    'NUM tail',
    'STR tail',
    'NUM',
    'STR',
  ]
}

# Flattens lists
# E.g. flatten([1, ['foo',]]) = [1, 'foo']
def flatten(l):
  new_list = []
  for item in l:
    if item.__class__.__name__ == 'list':
      inner_list = flatten(item)
      new_list.extend(inner_list)
    else:
      new_list.append(item)
  return new_list

# Determines for each chunk if it is a NUM, a STR or a parenthesis
def return_proper_token(x):
  if re.match('^\-?[0-9\.]+$', x):
    return Token('NUM', float(x))
  else:
    return Token(token_map.get(x, 'STR'), x)

# Tokenizes a string
def tokenize(expr):
  split_expr = re.findall('[a-zA-Z]+[0-9]*[a-zA-Z]*|\-?[0-9\.]+|[%s]' % ''.join(token_map), expr)
  tokens = [return_proper_token(x) for x in split_expr]
  return tokens

# The parser itself, recursively builds a tree of tokens
def match(rule_name, tokens):
  if tokens and rule_name == tokens[0].name:
    return RuleMatch(tokens[0], tokens[1:])
  # Checks for every entry in the rule_map
  for expansion in rule_map.get(rule_name, ()):
    remaining_tokens = tokens
    matched_subrules = []
    # Checks for every subrule if it fits
    for subrule in expansion.split():
      matched, remaining_tokens = match(subrule, remaining_tokens)
      if not matched:
        break
      matched_subrules.append(matched)
    else:
      return RuleMatch(rule_name, matched_subrules), remaining_tokens
  return None, None

# Beautifies and refines the output of the parser and builds the
# final data structure
def create_dict(matched_stuff):
  if matched_stuff.name == 'list':
    key = None
    values = []
    for item in matched_stuff.matched:
      if item.__class__.__name__ == 'RuleMatch':
        values.extend(create_dict(item))
      else:
        if item.name == 'STR':
          if item.name == 'STR' and matched_stuff.matched.index(item) == 1 and matched_stuff.matched[0].name == 'LPAR':
            key = item.value
          else:
            values.append(item.value)
        elif item.name == 'NUM':
          values.append(item.value)
        elif item.name == 'LPAR':
          pass
        else:
          pass
    entry = Entry(key, flatten(values))
    return entry
  # So it's a tail and not a list.
  else:
    values = []
    for item in matched_stuff.matched:
      if item.__class__.__name__ == 'RuleMatch':
        values.append(create_dict(item))
      else:
        if item.name == 'STR':
          values.append(item.value)
        elif item.name == 'NUM':
          values.append(item.value)
        elif item.name == 'LPAR':
          pass
        else:
          pass
    return flatten(values)

# Only a wrapper function, that takes a string and returns the
# parsed output
def parse(expr):
  parsed_stuff = create_dict(match('tail', tokenize(expr))[0])
  if parsed_stuff.__class__.__name__ == "list":
    if len(parsed_stuff) == 1:
      return parsed_stuff[0]  # If parsed stuff is a list with one item, unpack it from the list
  return parsed_stuff # Return the list as it is otherwise

# This part is only executed when you run the file by itself
# If this file is included as a library, this code does not run
if __name__=="__main__":
  import sys
  stdin_expr = sys.stdin.read()
  dictionary = parse(stdin_expr)
  print(dictionary)
