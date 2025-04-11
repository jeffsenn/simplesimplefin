import csv
import json
import sys
import pprint
import math
import datetime

def ts_to_datetime(ts):
    return datetime.datetime.fromtimestamp(ts)

lastfetch = json.loads(open("status.json","r").read())
with open(sys.argv[1], newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)

headers = rows[0]
data = []
for row in rows[1:]:
  data.append(dict(zip(headers,row)))

debt = 0.0
income = 0.0
peraccount = {}
mint = math.inf
maxt = 0
for t in data:
    aid = t['account_id']
    if not peraccount.get(aid):
        peraccount[aid] = [0.0, 0.0, 0.0, t['institution'] + '-' + t['account']]
    amt = float(t['amount'])
    tm = int(t['transacted_at'])
    maxt = max(tm,maxt)
    mint = min(tm,mint)
    if amt > 0:
        income += amt
        peraccount[aid][0] += amt
    else:
        debt += amt
        peraccount[aid][1] += amt
    peraccount[aid][2] += amt        

ireport = []
oreport = []
nreport = []
for ac in peraccount:
    iamt,oamt,amt,nam = peraccount[ac]
    if math.fabs(iamt) > 0.01:
        a = f"{iamt:,.2f}"
        ireport.append((math.fabs(iamt), f"{a:>14} {nam}"))
    if math.fabs(oamt) > 0.01:
        a = f"{oamt:,.2f}"
        oreport.append((math.fabs(oamt), f"{a:>14} {nam}"))
    if math.fabs(amt) > 0.01:
        a = f"{amt:,.2f}"
        nreport.append((math.fabs(amt), f"{a:>14} {nam}"))

final = f"""Accounts Report - {ts_to_datetime(mint)} - {ts_to_datetime(maxt)}

Total Outgoing: {debt:,.2f}
Total Income  :  {income:,.2f}

Net:
{"\n".join([a[1] for a in reversed(sorted(nreport))])}

In:
{"\n".join([a[1] for a in reversed(sorted(ireport))])}
Out:
{"\n".join([a[1] for a in reversed(sorted(oreport))])}
"""

print(final)
