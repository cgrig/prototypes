from sap import Bindings, Initializer, NewAction, Role, Rule, roles

roles['Mircea'] = Role({0 : Initializer([],[])}, [Rule(("True", []), [NewAction('_', [('Mircea',[])])])])

main = [NewAction('_', [('Mircea',[])])]

for action in main:
  action.execute(Bindings(), set())
