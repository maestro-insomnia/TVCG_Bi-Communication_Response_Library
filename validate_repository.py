from pathlib import Path
import json, re

ROOT=Path(__file__).resolve().parent
lib=json.loads((ROOT/'library'/'response_library.json').read_text(encoding='utf-8'))
cat=json.loads((ROOT/'library'/'route_catalog.json').read_text(encoding='utf-8'))
req=json.loads((ROOT/'prompts'/'route_request.schema.json').read_text(encoding='utf-8'))
res=json.loads((ROOT/'prompts'/'route_result.schema.json').read_text(encoding='utf-8'))
prompt=(ROOT/'prompts'/'router_prompt_compact_v2.md').read_text(encoding='utf-8')

assert lib['version']=='6.3'
assert len(lib['broadGroups'])==9
assert len(lib['responses'])==75
assert sum(v['category']=='broad' for v in lib['responses'].values())==18
assert sum(v['category']=='specific' for v in lib['responses'].values())==48
assert sum(v['category']=='decision' for v in lib['responses'].values())==2
assert sum(v['category']=='control' for v in lib['responses'].values())==7
assert 'BC_CTL07_CONTINUE_ASKING' in lib['responses']

expected_required={
 'G01_SHIRT_OVERVIEW','G02_SHIRT_LIKES','G03_SHIRT_WARDROBE','G04_SHIRT_REPLACEABILITY',
 'G05_HOODIE_OVERVIEW','G06_HOODIE_LIKES','G07_HOODIE_WARDROBE','G08_HOODIE_REPLACEABILITY'
}
assert expected_required.issubset(lib['broadGroups'])
assert 'G09_CURRENT_PREFERENCE' in lib['broadGroups']

routes=set(res['properties']['routeCode']['enum'])
assert len(routes)==66
assert routes==set(cat.keys())
local_routes=set(lib['broadGroups']) | {c for c in lib['responses'] if not c.startswith('BC_BRD')}
assert routes==local_routes
assert 'BC_OPENING' not in routes
assert req['properties']['protocolVersion']['const']=='6.3'

# Every logical route must appear literally in the finalized prompt catalog/rules.
missing=[r for r in sorted(routes) if r not in prompt]
assert not missing, f'Route codes missing from prompt: {missing}'

# Every Broad mapping must resolve to two real local responses.
for g,m in lib['broadGroups'].items():
    assert m['preferred'] in lib['responses']
    assert m['alternative'] in lib['responses']
    assert lib['responses'][m['preferred']]['category']=='broad'
    assert lib['responses'][m['alternative']]['category']=='broad'

print('Repository validation passed.')
print('Protocol: 6.3')
print('Logical routes: 66')
print('Selectable responses: 75 (18 Broad, 48 Specific, 2 Decision, 7 Control)')
print('Fixed opening: separate / not router-selectable')
print('Prompt: router_prompt_compact_v2.md')
