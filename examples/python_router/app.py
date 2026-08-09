#!/usr/bin/env python3
"""Interactive BC response-library reference implementation — protocol v6.3.

Run:
    python app.py
Then type:
    start

The model returns only a semantic route. All virtual-character speech is selected locally
from response_library.json. There is no final-recommendation stage: final
recommendations become *enabled* after G01-G08 have each played at least once,
while follow-up questions remain allowed.
"""
from __future__ import annotations
import argparse, json, os, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
API_URL = "https://api.openai.com/v1/responses"

REQUIRED_BROAD_GROUPS = {
    "G01_SHIRT_OVERVIEW", "G02_SHIRT_LIKES",
    "G03_SHIRT_WARDROBE", "G04_SHIRT_REPLACEABILITY",
    "G05_HOODIE_OVERVIEW", "G06_HOODIE_LIKES",
    "G07_HOODIE_WARDROBE", "G08_HOODIE_REPLACEABILITY",
}

def load_dotenv(path: Path) -> None:
    if not path.exists(): return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key,value=line.split("=",1); key=key.strip(); value=value.strip().strip('"').strip("'")
        if key and key not in os.environ: os.environ[key]=value

load_dotenv(Path(__file__).resolve().parent/".env")
LIBRARY=json.load(open(BASE_DIR/"library"/"response_library.json",encoding="utf-8"))
RESULT_SCHEMA=json.load(open(BASE_DIR/"prompts"/"route_result.schema.json",encoding="utf-8"))
ROUTER_PROMPT = (BASE_DIR / "prompts" / "routing_prompt.md").read_text(encoding="utf-8")
BROAD_GROUPS=LIBRARY["broadGroups"]
RESPONSES=LIBRARY["responses"]
OPENING=LIBRARY["fixedOpening"]
VALID_ROUTES=set(RESULT_SCHEMA["properties"]["routeCode"]["enum"])

class ConversationState:
    def __init__(self): self.reset()
    def reset(self):
        self.started=False; self.ended=False; self.active_item="unknown"; self.turn_index=0
        self.played_broad_groups=set(); self.broad_counts=defaultdict(int); self.recent_turns=[]
    @property
    def final_recommendation_enabled(self):
        return REQUIRED_BROAD_GROUPS.issubset(self.played_broad_groups)
    @property
    def missing_required_broad_groups(self):
        return sorted(REQUIRED_BROAD_GROUPS-self.played_broad_groups)
    def request(self,user_text,input_mode):
        return {
            "protocolVersion":"6.3", "turnIndex":self.turn_index+1,
            "finalRecommendationEnabled":self.final_recommendation_enabled,
            "inputMode":input_mode, "activeItem":self.active_item,
            "rawInputText":user_text, "playedBroadGroups":sorted(self.played_broad_groups),
            "recentTurns":self.recent_turns[-4:],
        }
    def resolve_response(self,route_code):
        if route_code in BROAD_GROUPS:
            self.broad_counts[route_code]+=1
            group=BROAD_GROUPS[route_code]
            code=group["preferred"] if self.broad_counts[route_code]%2==1 else group["alternative"]
            self.played_broad_groups.add(route_code)
            return code, RESPONSES[code]
        if route_code not in RESPONSES: raise KeyError(f"No local response for route {route_code}")
        return route_code, RESPONSES[route_code]
    def update_after_turn(self,user_text,result,response_code,response):
        self.turn_index+=1; route=result["routeCode"]
        if result["routeCategory"]!="control":
            if route in BROAD_GROUPS: self.active_item=BROAD_GROUPS[route]["target"]
            elif route.startswith("BC_SPC"):
                n=int(route[6:8]); self.active_item="first_top" if n<=21 else "second_top" if n<=38 else "both"
            elif route.startswith("BC_DEC"): self.active_item="both"
        self.recent_turns.append({
            "turnIndex":self.turn_index,
            "participantText":user_text,
            "correctedParticipantText":result["correctedInputText"],
            "utteranceType":result["utteranceType"],
            "routeCode":route,
        })
        self.recent_turns=self.recent_turns[-4:]
        if response.get("endsConversation"): self.ended=True

def extract_output_text(data):
    for item in data.get("output",[]):
        if item.get("type")!="message": continue
        for content in item.get("content",[]):
            if content.get("type")=="output_text" and isinstance(content.get("text"),str): return content["text"]
    raise RuntimeError("Responses API returned no output_text item.")

def call_router(request_obj,*,api_key,model,reasoning_effort,timeout):
    api_schema={k:v for k,v in RESULT_SCHEMA.items() if k not in {"$schema","title"}}
    payload={
        "model":model,
        "instructions":ROUTER_PROMPT,
        "input":json.dumps(request_obj,ensure_ascii=False),
        "text":{"format":{"type":"json_schema","name":"bc_route_result_v63","strict":True,"schema":api_schema}},
        "reasoning":{"effort":reasoning_effort},
        "max_output_tokens":450,
        "store":False,
    }
    req=urllib.request.Request(API_URL,data=json.dumps(payload,ensure_ascii=False).encode(),headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as resp: data=json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail=e.read().decode("utf-8",errors="replace"); raise RuntimeError(f"OpenAI API HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e: raise RuntimeError(f"Network error calling OpenAI API: {e}") from e
    if data.get("status") not in (None,"completed"): raise RuntimeError(f"OpenAI response status is {data.get('status')}: {data.get('incomplete_details')}")
    result=json.loads(extract_output_text(data))
    if result.get("routeCode") not in VALID_ROUTES: raise RuntimeError(f"Model returned invalid routeCode: {result.get('routeCode')}")
    return result,data

def print_debug(state,result,response_code,raw_api=None):
    print("[debug] correctionStatus:",result["correctionStatus"])
    print("[debug] punctuationStatus:",result["punctuationStatus"])
    print("[debug] utteranceType:",result["utteranceType"])
    print("[debug] informationRequestCount:",result["informationRequestCount"])
    print("[debug] routingBasisText:",result["routingBasisText"])
    print("[debug] correctedInputText:",result["correctedInputText"])
    print("[debug] semanticTarget:",result["semanticTarget"])
    print("[debug] intentClass:",result["intentClass"])
    print("[debug] routeCode:",result["routeCode"])
    print("[debug] responseCode:",response_code)
    print("[debug] confidence:",result["confidence"])
    print("[debug] finalRecommendationEnabled(after turn):",state.final_recommendation_enabled)
    if raw_api: print("[debug] usage:",json.dumps(raw_api.get("usage",{}),ensure_ascii=False))

def help_text():
    print("Commands:")
    print("  start   start/reset and play the fixed opening")
    print("  /state  show dialogue state, missing Broad groups, and final-recommendation switch")
    print("  /debug  toggle routing/debug output")
    print("  /reset  reset and immediately play the opening")
    print("  /help   show commands")
    print("  /quit   exit")

def main():
    parser=argparse.ArgumentParser(description="Interactive BC semantic-router reference — protocol v6.3")
    parser.add_argument("--model",default=os.getenv("OPENAI_MODEL","gpt-5.6-luna"))
    parser.add_argument("--reasoning",default=os.getenv("OPENAI_REASONING_EFFORT","low"),choices=["none","low","medium","high","xhigh"])
    parser.add_argument("--input-mode",default=os.getenv("INPUT_MODE","typed"),choices=["typed","asr"])
    parser.add_argument("--timeout",type=int,default=int(os.getenv("OPENAI_TIMEOUT_SECONDS","60")))
    args=parser.parse_args()
    api_key=os.getenv("OPENAI_API_KEY","").strip(); state=ConversationState(); debug=os.getenv("SHOW_ROUTING_DEBUG","0")=="1"
    print(f"BC Router Reference v6.3 | model={args.model} | inputMode={args.input_mode}")
    print("Type 'start' to begin. Type /help for commands.")
    while True:
        try: text=input("You: ").strip()
        except (EOFError,KeyboardInterrupt): print("\nBye."); return 0
        if not text: continue
        low=text.lower()
        if low in {"/quit","quit","exit"}: print("Bye."); return 0
        if low=="/help": help_text(); continue
        if low=="/debug": debug=not debug; print(f"Debug {'ON' if debug else 'OFF'}."); continue
        if low=="/state":
            print(json.dumps({
                "activeItem":state.active_item,
                "playedBroadGroups":sorted(state.played_broad_groups),
                "missingRequiredBroadGroups":state.missing_required_broad_groups,
                "finalRecommendationEnabled":state.final_recommendation_enabled,
                "broadCounts":dict(state.broad_counts),"turnIndex":state.turn_index,"ended":state.ended,
            },ensure_ascii=False,indent=2)); continue
        if low in {"start","/reset"}:
            state.reset(); state.started=True; print("Character:",OPENING); continue
        if not state.started or state.ended: print("Type 'start' to begin a new conversation."); continue
        if not api_key:
            print("[error] OPENAI_API_KEY is not set. Add your key to .env, then restart the program."); continue
        req_obj=state.request(text,args.input_mode)
        try:
            result,raw=call_router(req_obj,api_key=api_key,model=args.model,reasoning_effort=args.reasoning,timeout=args.timeout)
            response_code,response=state.resolve_response(result["routeCode"])
            state.update_after_turn(text,result,response_code,response)
            if debug: print_debug(state,result,response_code,raw)
            print("Character:",response["text"])
            if state.ended: print("[conversation ended] Type 'start' to begin a new conversation.")
        except Exception as e: print("[error]",e)

if __name__=="__main__": raise SystemExit(main())
