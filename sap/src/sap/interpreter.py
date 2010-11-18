#!/usr/bin/env python3

import re
import sys

from sap import ds
from optparse import OptionParser

sap_main=[]

def execute():
  for action in sap_main:
    action.execute(ds.Bindings(), set())    

script_lines = []
current_script = ''
parsed_lines = 0
current_role_name = ''
current_role_inits = []
current_role_rules = []
current_actions = []
errors = []
warnings = []
offsets = [0]

def report(where, what):
  where.append('{0}:{1}: {2}'
      .format(current_script, parsed_lines + 1, what))

def error(message):
  report(errors, message)

def warning(message):
  report(warnings, message)

# ignores white lines
# throws IndexError iff there's no next line
# processes indent
# trims trailing space, but warns
# TODO: strip comments
def get_next_line():
  global offsets
  global parsed_lines
  l = script_lines[parsed_lines][:-1]
  if l.find('\t') != -1:
    error('I refuse to deal with tabs')
  if l == '':
    parsed_lines += 1
    return get_next_line()
  if l[-1] == ' ':
    warning('trailing whitespace ignored')
    l = l.rstrip()
  m = re.match(r'( *)(.*)', l)
  offset = len(m.group(1))
  if offset not in offsets and offset < offsets[-1]:
    error('bad indentation')
  offsets = [x for x in offsets if x < offset]
  indent = len(offsets)
  offsets.append(offset)
  return indent, m.group(2)

def parse_role_member():
  global parsed_lines
  global current_actions
  try: i, l = get_next_line()
  except IndexError: return False
  m = re.match(r'([a-z]+)', l)
  t = m.group(1)
  te = (", found '" + t + "'") if m else ""
  if not m or t not in ['init','rule']: error("expected 'init' or 'rule'" + te)
  parsed_lines += 1
  current_actions = []
  if t == 'init':
    pass
  else:
    # TODO
    pass
  return True

def parse_role():
  global current_role_inits
  global current_role_rules
  global parsed_lines
  try: i, l = get_next_line()
  except IndexError: return False
  m = re.match(r'role +([a-zA-Z]+):$', l)
  if not m: return False
  parsed_lines += 1
  if i != 0: error("indented 'role'")
  role_name = m.group(1)
  current_role_inits, current_role_rules = [], []
  while parse_role_member(): pass
  ds.roles[role_name] = ds.Role(current_role_inits, current_role_rules)
  return True

def parse_main():
  global parsed_lines
  try: i, l = get_next_line() 
  except IndexError: return False
  if l != 'main': return False
  parsed_lines += 1
  # TODO: continue
  return True

def parse_script(path):
  global current_script
  global parsed_lines
  global script_lines
  current_script = path
  script = open(path, 'r')
  script_lines = script.readlines()
  script.close()
  #print('parse {0} -> {1}'.format(path, script_lines)) #DBG
  parsed_lines = 0
  while parse_role(): pass
  parse_main()
  #print('parsed_lines',parsed_lines) #DBG
  assert (parsed_lines <= len(script_lines))
  if parsed_lines < len(script_lines):
    error('syntax error')

def initialize():
  ds.roles = dict()

def parse_args(command):
  parser = OptionParser()
  parser.add_option('-p', '--print', action='store_true', 
      help='print the agent program (debug)')
  parser.add_option('-d', '--dry', action='store_false', dest='exec',
      default=True, help='do not execute, just parse')
  return parser.parse_args(command)

def main(argv):
  options, files = parse_args(argv)
  files = files[1:]
  initialize()
  for s in files:
    parse_script(s)
  if options.print:
    ds.dump()
  if options.exec:
    execute()

if __name__ == '__main__':
  try:
    main(sys.argv)
  finally:
    for e in errors:
      print('{0} (E)'.format(e))
    for w in warnings:
      print('{0} (W)'.format(w))
