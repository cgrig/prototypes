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
  sap.roles = dict()
  while parse_role(): pass
  parse_main()

def interpret(path):
  parse_script(path)
  execute()


def main(argv):
  interpret(argv[1])
  # TODO: arg check, usage msg

if __name__ == '__main__':
  main(sys.argv)
