"""A parser for SAP scripts.
"""
from collections import namedtuple
import bisect
import re

class NoMatchError(Exception):
  pass

warnings = []
errors = []

class Location:
  """The start and end are (line, column) pairs. Inclusive.
  """
  def __init__(self, start, end=None):
    self.start = start
    self.end = end if end is not None else start

  def __str__(self):
    def pp(x):
      return '{0}:{1}'.format(x[0], x[1])
    ps = pp(self.start)
    pe = pp(self.end)
    return ps + '-' + pe if ps != pe else ps

def join_locations(*locations):
  result = None
  for l in locations:
    if result is None:
      result = l
    else:
      result.start = min(result.start, l.start)
      result.end = max(result.end, l.end)
  return result

DataWithLocation = namedtuple('DataWithLocation', 'data location')

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
      warnings.append(DataWithLocation('tab treated as space', t.location))
      t.data = ' '
    yield t

def join_spaces(input):
  spaces = ''
  location = None
  for t in input:
    if t.data == ' ':
      spaces += ' '
      location = join_locations(location, t.location)
    else:
      if spaces != '':
        yield DataWithLocation(spaces, location)
        spaces = ''
        location = None
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
    if t.data == ' ': # TODO make it work for t.data = '   '
      queue.append(t)
    else:
      if t.data != '\n':
        for q in queue:
          yield q
      queue = []
      yield t

# Assumes that spaces are consolidated.
def process_indents(input):
  indents = [0]
  state = 0 # 0 = beginning of line, 1 = non-space seen
  for t in input:
    if state == 0:
      if t.data != '\n':
        indent = len(t.data) if t.data[0] == ' ' else 0
        position = (t.location.start[0], 0)
        p = bisect.bisect_left(indents, indent)
        for _ in range(p + 1, len(indents)):
          yield DataWithLocation('}', Location(position))
        if p == len(indents):
          yield DataWithLocation('{', Location(position))
        indents[p:] = [indent]
        state = 1
      yield t
    else:
      if t.data == '\n':
        state = 0
      yield t
  position = (t.location.end[0] + 1, 0)
  for _ in indents[1:]:
    yield DataWithLocation('}', Location(position))

def glue_string_literals(input):
  s = ''
  ls = []
  state = 0
  for t in input:
    if state == 0:
      if t.data == "'":
        s += t.data
        ls.append(t.location)
        state = 1
      else:
        yield t
    elif state == 1:
      if t.data == "'":
        s += t.data
        ls.append(t.location)
        r = DataWithLocation(s, join_locations(*ls))
        yield r
        s = ''
        ls = []
        state = 0
      elif t.data == '\\':
        state == 2
      elif t.data == '\n':
        warnings.append(DataWithLocation('ignored newline', t.location))
      else:
        s += t.data
        ls.append(t.location)
    elif state == 2:
      s += t.data
      ls.append(t.location)
      state = 1
  if state != 0:
    errors.append('input ends inside string literal', join_locations(*ls))

def glue_consecutive_matching(pattern, input):
  s = ''
  ls = []
  for t in input:
    if pattern.match(t.data):
      s += t.data
      ls.append(t.location)
    else:
      if s != '':
        yield DataWithLocation(s, join_locations(*ls))
        s = ''
        ls = []
      yield t
  assert s == '', 'Leftovers: <{0}>'.format(s)

def glue_identifiers(input):
  import re
  return glue_consecutive_matching(re.compile(r'[a-zA-Z]$'), input)

def glue_integers(input):
  import re
  return glue_consecutive_matching(re.compile(r'[0-9]$'), input)

# This will be split into several functions.
# Glues literals: numbers, strings.
# Glues identifiers.
# Strips spaces that aren't at start of line: They just separate tokens.
# Glues consecutive spaces.
# Keeps line breaks, as line structure is dealt with later.
def tokenizer(input):
  return input # TODO

def main():
  import sys
  cs = iter(sys.stdin.read())  # TODO: don't load in memory
  cs = add_locations(cs)
  cs = add_newline_at_end(cs)
  cs = space_of_tab(cs)
  cs = glue_string_literals(cs)
  cs = glue_identifiers(cs)
  cs = glue_integers(cs)
  cs = tokenizer(cs)  # TODO: must tokenize before even stripping comments to avoid problems with string literals
  cs = strip_comments(cs)
  cs = glue_lines(cs)  # TODO: move before tokenizer?
  cs = strip_trailing_space(cs)
  cs = join_spaces(cs)
  cs = process_indents(cs)
  #cs = map(lambda x: x.data, cs)
  for c in cs:
    sys.stdout.write('{0}: {1}\n'.format(c.location, c.data))

if __name__ == '__main__':
  import cProfile
  cProfile.run('main()', 'sap.parser.prof')
