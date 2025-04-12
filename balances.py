import json
import pprint
import time
import datetime
TOO_OLD = 3600*24*3

lastfetch = json.loads(open("status.json","r").read())
available=0.0
net=0.0
assets=0.0
debt=0.0
now = time.time()
for k in lastfetch:
    if k.endswith("-info"):
        a = lastfetch[k]
        n = float(a.get('balance'))
        av = a.get('available-balance')
        av = float(av) if av else n # available defaults to balance
        net += n
        available += av
        if n > 0:
            assets += n
        else:
            debt += -n
        sn = f"{n:,.2f}"
        sa = f"{av:,.2f}"
        pn = f"{n-av:,.2f}"
        bdate = lastfetch.get(k).get("balance-date")
        warn = f" **{round((now - bdate)/3600)} hours ago**" if now - bdate > TOO_OLD else ''
        if warn == '':
            warn = " --not recent--" if now - lastfetch.get(k[:-5]+"-updated",0) > 3600*24*3 else ''
        ava = f" ({pn} pending) " if av != 0.0 and av != n else ""
        print(f"{sn:>14}\t{a['org']['name']}-{a['name']}{ava}{warn}")        
print("------------------------")
sn = f"{net:,.2f}"
sa = f"{available:,.2f}"
print(f"{sn:>14} = {assets:,.2f} (asset) - {debt:,.2f} (debt)")

