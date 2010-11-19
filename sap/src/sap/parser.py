"""A parser for SAP scripts.
"""

import bisect

class NoMatchError(Exception):
  pass

class Location:
  """The start and end are (line, column) pairs. Inclusive.
  """
  def __init__(self, start, end=None):
    self.start = start
    self.end = end if end is not None else start

  def __str__(self):
    def pp(x):
      return '{0}:{1}'.format(x[0], x[1])
    ps = pp(start)
    pe = pp(end)
    return ps + '-' + pe if ps != pe else ps

def join_locations(locations):
  pass # TODO

class DataWithLocation:
  def __init__(self, data, location):
    self.data = data
    self.location = location

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

def add_locations(input):
  line = 1
  column = 1
  for c in input:
    position = (line, column)
    yield DataWithLocation(c, Location(position))
    if c == '\n':
      line += 1
      column = 1
    else:
      column += 1

def strip_comments(input):
  state = 0
  for t in input:
    if state == 0:
      if t.data == '#':
        state = 1
      else:
        yield t
    else:
      if t.data == '\n':
        state = 0
        yield t

def space_of_tab(input):
  for t in input:
    if t.data == '\t':
      sys.stderr.write('tab at {0} treated as space\n'
          .format(t.location)) # TODO
      t.data = ' '
    yield t

def glue_lines(input):
  state = 0
  for t in input:
    if state == 0:
      if t.data == '\\':
        escape = t
        state = 1
      else:
        yield t
    else:
      if t.data != '\n':
        yield escape
        yield t
      state = 0

def add_newline_at_end(input):
  for t in input:
    yield t
  if t.data != '\n':
    position = (t.location.end[0], t.location.end[1] + 1)
    yield DataWithLocation('\n', Location(position))

def strip_trailing_space(input):
  queue = []
  for t in input:
    if t.data == ' ':
      queue.append(t)
    else:
      if t.data != '\n':
        for q in queue:
          yield q
      queue = []
      yield t

def process_indents(input):
  pass # TODO

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
  cs = iter(sys.stdin.read())  # TODO: don't load in memory
  cs = add_locations(cs)
  cs = add_newline_at_end(cs)
  cs = space_of_tab(cs)
  cs = strip_comments(cs)
  cs = glue_lines(cs)  # NOTE: in C usually this is done before strip_comments
  cs = strip_trailing_space(cs)
  cs = map(lambda x: x.data, cs)
  for c in cs:
    sys.stdout.write(c)
