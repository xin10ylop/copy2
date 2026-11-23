# Buys of copyable size paid in tokens the floats do not hold, over the five copied wallets (Nov 23). Run in the scratchpad
# with the five wallets' hist_* folders (own_only.py).
import json, collections, urllib.request, time
OURS=("3NZ9JMVB","pumpCmXq","SPCXxcqX","TTWofwAg","he1iusmf","98kfF7rm")
bots=(("qqq","H9kuqGKN",1.3),("www","CqCAzte8",0.5),("eee","CgyPomTG",0.5),("rrr","3XeFcZKS",0.5),("ttt","6LwMLkCe",0.5))
SOLM="So11111111111111111111111111111111111111112"
def get(u):
    for a in range(6):
        try: return json.load(urllib.request.urlopen(u,timeout=30))
        except Exception: time.sleep(5*(a+1))
    return None
allq=set(); data={}
for b,w,mn in bots:
    tr=[e for l in open(f"hist_{w}/{w}_trades.jsonl") for e in (json.loads(l)["trades"] or [])]
    by=collections.defaultdict(list)
    for e in tr: by[e["m"]].append(e)
    data[b]=(by,mn); allq|={e["quote"] for e in tr if e["quote"] and not e["quote"].startswith("1111")}
qs=sorted(allq); P={}
for i in range(0,len(qs),40):
    r=get("https://lite-api.jup.ag/price/v3?ids="+",".join(qs[i:i+40]+[SOLM])); P.update({k:v for k,v in (r or {}).items() if v}); time.sleep(1)
su=P[SOLM]["usdPrice"]
tot=collections.defaultdict(collections.Counter); days={}
for b,(by,mn) in data.items():
    ts=[]
    for m,es in by.items():
        es.sort(key=lambda e:(e["slot"],not e["buy"]))
        if not es[0]["buy"]: continue
        q=es[0]["quote"] or ""; ts.append(es[0]["t"])
        if q.startswith("1111") or not q or q[:8] in OURS or q not in P: continue
        if es[0]["q"]*P[q]["usdPrice"]/su/10**P[q]["decimals"]>=mn: tot[q][b]+=1
    days[b]=(max(ts)-min(ts))/86400
rows=sorted(tot.items(), key=lambda kv: -sum(kv[1][b]/days[b] for b in kv[1]))
print("copyable-size buys paid in tokens we don't hold, a day")
for q,c in rows[:12]:
    j=get("https://lite-api.jup.ag/tokens/v2/search?query="+q); time.sleep(1)
    j=j[0] if j else {}
    pd={b:c[b]/days[b] for b in c}
    print(f"  {str(j.get('symbol')):10s} {q}  {sum(pd.values()):4.2f}/day  " + ", ".join(f"{b} {c[b]}" for b in c) + f"   [{j.get('name')}; liquidity ${j.get('liquidity') or 0:,.0f}]")
print({b: round(d,1) for b,d in days.items()})
