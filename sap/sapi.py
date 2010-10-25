#!/usr/bin/env python3

# SAP Interpreter. SAP is a SAP Agent Platform.

import sap
import sys

sap_main=[]

def execute():
  for action in sap_main:
    action.execute(sap.Bindings(), set())    

script_lines = []
parsed_lines = 0
current_role_name = ''
current_role_inits = []
current_role_rules = []

def parse_role():
  try:
    l = script_lines[parsed_lines].strip()
    if not l.startswith('role '):
      return False
    # TODO: continue
  except IndexError:
    return False

def parse_main():
  pass

def parse_script(path):
  script = open(path, 'r')
  script_lines = script.readlines()
  script.close()
  parsed_lines = 0
  while parse_role(): pass
  parse_main()

def initialize():
  sap.roles = dict()

def main(argv):
  if '-help' in argv[1:]:
    print('Usage: {0} <agent files>'.format(argv[0]), file=sys.stderr)
    exit(1)
  initialize()
  for s in argv[1:]:
    parse_script(s)
  execute()

if __name__ == '__main__':
  main(sys.argv)
