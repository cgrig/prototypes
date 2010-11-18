"""A parser for SAP scripts.
"""

# BIG TODO: Location.

import bisect

class NoMatchError(Exception):
  pass

def parse(rules, stream):
  for to_match, value in rules:
    stream.mark()
    args = []
    try:
      for m in to_match:
        a = m(stream)
        if a is None:
          raise NoMatchError
        args.append(a)
      stream.unmark()
      return value(args)
    except NoMatchError:
      stream.rewind()
  return None

class CommentStripper:
  def __init__(self, input):
    self.input = input

  def __iter__(self):
    return self

  def __next__(self):
    c = next(self.input)
    if c == '#':
      return self.hide()
    else:
      return c

  def hide(self):
    while True:
      c = next(self.input)
      if c == '\n':
        return '\n'

class LineProcessor:
  pass
  #TODO: eat '\n ' and empty lines

class IndentProcessor:
  def __init__(self, input):
    self.input = input
    self.indents = []

  def __iter__(self):
    indent = 0
    while True:
      c = next(self.input)
      if c == ' ':
        indent += 1
      else:
        p = bisect.bisect_left(self.indents, indent)
        for _ in range(p, len(self.indents)):
          yield '}'
        if p == len(self.indents):
          yield '{'
        self.indents[p:] = [indent]
        break
    while True:
      yield c
      if c == '\n':
        yield c
        return
      c = next(self.input)

if __name__ == '__main__':
  import sys
  parser = IndentProcessor(CommentStripper(iter(sys.stdin.read())))
  for c in parser:
    sys.stdout.write(c)
