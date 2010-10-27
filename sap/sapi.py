#!/usr/bin/env python3

# SAP Interpreter. SAP is a SAP Agent Platform.

import sap
import sys

from optparse import OptionParser

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
    role_name = l[5:].strip()[:-1]
    s
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

def parse_args(command):
  parser = OptionParser()
  parser.add_option('-p', '--print', action='store_true', 
      help='print the agent program (debug)')
  parser.add_option('-d', '--dry', action='store_false', dest='exec',
      default=True, help='do not execute, just parse')
  return parser.parse_args(command)

def main(argv):
  options, files = parse_args(argv)
  initialize()
  for s in files:
    parse_script(s)
  if options.print:
    sap.dump()
  if options.exec:
    execute()

if __name__ == '__main__':
  main(sys.argv)
