import json
import pprint
lastfetch = json.loads(open("status.json","r").read())
available=0.0
net=0.0
assets=0.0
debt=0.0
for k in lastfetch:
    if k.endswith("-info"):
        a = lastfetch[k]
        n = float(a.get('balance'))
        av = float(a.get('available-balance'))
        net += n
        available += av
        if n > 0:
            assets += n
        else:
            debt += -n
        sn = f"{n:,.2f}"
        sa = f"{av:,.2f}"
        print(f"{sn:>14}\t{sa:>14}\t{a['org']['name']}-{a['name']}")
print("------------------------")
sn = f"{net:,.2f}"
sa = f"{available:,.2f}"
print(f"{sn:>14}\t{sa:>14}")
print("------------------------")
sn = f"{assets:,.2f}"
sa = f"{debt:,.2f}"
print(f"{sn:>14}\t{sa:>14}\tAssets/Debts")

