import mircea

roles = dict()
roles["Captain"] = Role(
  interface = DebugFormatter,
  inits = [
    Init(
      args=['ball', 'name'], 
      body=[
        RememberAction(
          T('&&', [
            T('LeftAgent', [T('x', [])]),
            T('==', [
              T('Name', [T('x', [])]),
              T('string', [T('ge', [])])
            ])]))
      

)
