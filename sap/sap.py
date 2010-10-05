# SAP is a SAP Agent Platform

from multiprocessing import Process, Queue

roles = dict()

class ActionError(Exception):
  def __init__(self, description):
    self.description = description

  def __str__(self):
    return self.description

class MatchError(Exception):
  pass # used for flow control

class Term:
  def __init__(self, tag, children):
    self.tag = tag
    self.children = children
    self._hash = hash(tag)
    for c in children:
      self._hash ^= hash(c)

  def __hash__(self):
    return self._hash

  def __eq__(self, other):
    return self.tag == self.tag and self.children == other.children

  def _match(self, pattern, bindings):
    if pattern.is_variable():
      bindings.add(pattern.tag, self)
    elif (self.tag != pattern.tag or len(self.children) != len(pattern.children)):
      raise MatchError()
    for s, p in zip(self.children, pattern.children):
      s._match(p, bindings)

  def match(self, pattern):
    try:
      b = Bindings()
      self._match(pattern, b)
      return b
    except MatchError:
      return None

term_cache = dict()

def mk_term(tag, children):
  candidate = Term(tag, children)
  if candidate not in term_cache:
    term_cache[candidate] = candidate
  return term_cache[candidate]

class Bindings:
  def __init__(self):
    self.map = dict()

  def apply(self, (tag, arguments)):
    if arguments == [] and tag in self.map:
      return self.map[tag]
    else:
      return (tag, [self.apply(x) for x in arguments])

  def update(self, variable, expression):
    self.map[variable] = expression

  def add(self, variable, expression):
    if variable in self.map and self.map[variable] != expression:
      raise ActionError('trying to bind to a different expression')
    self.update(variable, expression)

class Rule:
  def __init__(self, formula, actions):
    self.formula = formula
    self.actions = actions

  def execute(self, message, state):
    for bindings in state.match(message, self.formula):
      try:
        for action in self.actions:
          action.execute(bindings, state)
      except s:
        print ('Failed to execute rule: ' + s)

class Role:
  def __init__(self, initializers, rules):
    self.initializers = initializers
    self.rules = rules

  def execute(self, message, state):
    for r in self.rules:
      r.execute(message, state)

  def initialize(self, state, arguments):
    n = len(arguments)
    if n not in self.initializers:
      raise ActionError('no initializer with arity ' + str(n))
    self.initializers[n].execute(state, arguments)

class Initializer:
  def __init__(self, variables, actions):
    self.variables = variables
    self.actions = actions

  def execute(self, state, arguments):
    assert len(arguments) == len(self.variables)
    b = Bindings()
    for v, a in zip(self.variables, arguments):
      b.add(v, a)
    for a in self.actions:
      a.execute(b, state)

class Action:
  def execute(self, bindings, state):
    print 'TODO: Implement execute in ', type(self).__name__

class RememberOrForgetAction(Action):
  def __init__(self, type, formula):
    assert (type in ['forget', 'remember'])
    self.type = type
    self.formula = formula

class EnactOrDiactAction(Action):
  def __init__(self, type, role):
    assert (type in ['enact', 'deact'])
    self.type = type
    self.role = role

class SendAction(Action):
  def __init__(self, target, formula):
    self.target = target
    self.formula = formula

class NewAction(Action):
  def __init__(self, agent, role_initializers):
    self.agent = agent
    self.role_initializers = role_initializers

  def execute(self, bindings, state):
    ris = [bindings.apply(x) for x in self.role_initializers]
    new_agent = Agent(ris)
    bindings.update(self.agent, new_agent.queue)
    new_agent.start()

class MentalState:
  def __init__(self):
    self.theory = set()

  def match(self, message, expression):
    result = []
    for f in self.theory:
      result.append(f.match(expression))
    if message:
      result.append(mk_term('received', message).match(expression))
    return result

  def remember(self, expression):
    self.theory.add(expression)

  def forget(self, expression):
    self.theory.remove(expression)

class Agent(Process):
  def __init__(self, role_initializers):
    Process.__init__(self)
    self._active_roles = set()
    self._mental_state = MentalState()
    self.queue = Queue()
    for r, args in role_initializers:
      self._active_roles.add(r)
      roles[r].initialize(self._mental_state, args)

  def _get_message(self):
    try:
      return self.queue.get(timeout = 1)
    except:
      return None

  def run(self):
    while True:
      message = self._get_message()
      for r in self._active_roles:
        roles[r].execute(message, self._mental_state)

