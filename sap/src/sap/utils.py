class PeekableGenerator:
  """Wraps a generator, such that you can rewind after peeking.
  """
  def __init__(self, generator):
    self.generator = generator()
    self.buffer = []
    self.position = 0

  def peek(self):
    if self.position == len(self.buffer):
      self.buffer.append(next(self.generator))
    self.position += 1
    return self.buffer[self.position-1]

  def next(self):
    r = self.peek()
    self.eat()
    return r

  def rewind(self):
    self.position = 0

  def eat(self):
    self.buffer = self.buffer[self.position:]
    self.position = 0

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
