from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / "library" / name).read_text(encoding="utf-8"))

b = load("broad_responses.json")
s = load("specific_responses.json")
d = load("final_decision_responses.json")
c = load("conversation_control_responses.json")
r = load("route_catalog.json")

assert len(b["groups"]) == 9
assert sum(2 for _ in b["groups"]) == 18
assert len(s["responses"]) == 48
assert len(d["responses"]) == 2
assert len(c["responses"]) == 6
assert 18 + 48 + 2 + 6 == 74
assert len(r["routes"]) == 65

codes = [x["route_code"] for x in r["routes"]]
assert len(codes) == len(set(codes)), "Duplicate route codes"
assert "BC_OPENING" not in codes, "Fixed opening must not be selectable"

response_codes=[]
for g in b["groups"]:
    response_codes += [g["preferred"]["response_code"], g["alternative"]["response_code"]]
response_codes += [x["response_code"] for x in s["responses"] + d["responses"] + c["responses"]]
assert len(response_codes) == 74
assert len(response_codes) == len(set(response_codes)), "Duplicate response codes"

print("Validation passed: 9 broad groups, 18 broad texts, 48 specific, 2 decision, 6 control, 74 selectable texts, 65 API route codes.")
