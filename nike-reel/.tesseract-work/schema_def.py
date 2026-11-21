import json,sys
S='/tmp/claude-0/-home-user-claude-test-2-0-/190debff-ba0e-5a86-8caf-b1266af9565a/scratchpad/schema/'
src = sys.argv[1]; names = sys.argv[2:]
d=json.load(open(S+src)); dd=d.get('$defs',{})
def short(o, depth=0):
    if isinstance(o, dict):
        if '$ref' in o: return o['$ref'].split('/')[-1]
        if 'anyOf' in o: return ' | '.join(short(x) for x in o['anyOf'])
        if o.get('type')=='array': return 'array<'+short(o.get('items',{}))+'>'
        if 'enum' in o: return 'enum'+str(o['enum'])
        if 'const' in o: return repr(o['const'])
        return o.get('type','?')
    return str(o)
for n in names:
    m = dd.get(n)
    if m is None:
        print('!! no def', n, [k for k in dd if n.lower() in k.lower()][:12]); continue
    print('==', n, '(required:', m.get('required'), ')')
    for k,v in m.get('properties',{}).items():
        desc = (v.get('description') or '')[:110]
        print(f'   {k}: {short(v)}' + (f'  # {desc}' if desc else ''))
