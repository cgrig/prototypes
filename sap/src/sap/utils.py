class Generator:
  """Wraps a generator, such that you can rewind.

  Generator(x) behaves just like x if only the method next is used.  The space
  and time overhead is constant for each call to next.

  In general, the memory use is proportional to the number of calls to next
  that follow a call to mark and are before a matching unmark/rewind.
  """
  def __init__(self, generator):
    self.generator = generator
    self.buffer = []
    self.position = 0
    self.marks = []

  def mark(self):
    self.marks.append(self.position)

  def unmark(self):
    self.marks.pop()
    if self.marks == []:
      self.buffer = []
      self.position = 0

  def rewind(self):
    self.position = self.marks.pop()

  def __next__(self):
    if self.position == len(self.buffer):
      if self.marks == []:
        self.position = 0
        self.buffer = []
        return next(self.generator)
      self.buffer.append(next(self.generator))
    r = self.buffer[self.position]
    self.position += 1
    return r

if __name__ == '__main__':
  def f():
    for x in range(10):
      yield x
  g = Generator(f())
  g.mark()
  assert next(g) == 0
  assert next(g) == 1
  g.rewind()
  g.mark()
  assert next(g) == 0
  g.mark()
  g.mark()
  assert next(g) == 1
  g.rewind()
  assert next(g) == 1
  g.rewind()
  assert next(g) == 1
  assert next(g) == 2
  g.unmark()
  g.mark()
  assert next(g) == 3
  assert next(g) == 4
  g.rewind()
  for i in range(3, 10):
    assert next(g) == i, 'should be {0}'.format(i)
  try:
    next(g)
  except StopIteration:
    pass
  else:
    assert false, 'Should have thrown StopIteration'
