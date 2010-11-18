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

  def mark():
    self.marks.append(self.position)

  def unmark():
    marks.pop()
    if marks == []:
      self.buffer = []
      self.position = 0

  def rewind():
    self.position = marks.pop()

  def next(self):
    if marks == []:
      return self.generator.next()
    if self.position == len(self.buffer):
      self.buffer.append(self.generator.next())
    r = self.buffer[self.position]
    self.position += 1
    return r

if __name__ == '__main__':
  def f():
    for x in range(10):
      yield x
  g = PeekableGenerator(f)
  print(g.peek())
  print(g.peek())
  g.rewind()
  print(g.peek())
  print(g.peek())
  print(g.peek())
  g.eat()
  print(g.peek())
  print(g.peek())
  g.rewind()
  print(g.peek())
  while True:
    print(g.peek())

# should print: 0 1 0 1 2 3 4 3 4 5 6 7 8 9 StopIteration
