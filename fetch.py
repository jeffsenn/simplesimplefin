import base64
import requests
import pprint
import json
import time
import csv

def new_app_setup(setup_token):
    setup_token = base64.b64decode(setup_token)
    response = requests.post(claim_url)
    access_url = response.text
    return access_url

def get_data(access_url, account=None, pending=False, start=None):
    scheme, rest = access_url.split('//', 1)
    auth, rest = rest.split('@', 1)
    url = scheme + '//' + rest + '/accounts'
    params = []
    if account:
        params.append(f'account={account}')
    else:
        params.append('balances-only=1')
    if pending:
        params.append('pending=1')
    if start:
        params.append(f'start-date={start}')
    if params: url = url + '?' + '&'.join(params)
    username, password = auth.split(':', 1)
    response = requests.get(url, auth=(username, password))
    data = response.json()
    return data

# do something interesting with the data
import datetime
def ts_to_datetime(ts):
    return datetime.datetime.fromtimestamp(ts)

TRANS_ATTRS=('transacted_at','amount','description','payee','memo','id','posted')
def output_transaction(a,t,lis):
    if set(TRANS_ATTRS) != set(t.keys()):
        print("Warning new attribute(s):", set(t.keys()) - set(TRANS_ATTRS))
    ins = a.get('org',{}).get('name','Unknown')
    acc = a.get('name')
    td = f"{ts_to_datetime(t['transacted_at'])}"
    pd = f"{ts_to_datetime(t['posted'])}"
    lis.append([ins,acc,a['id'],td]+[t.get(a) for a in TRANS_ATTRS]+[pd])
    return t['posted']
    
def update(lastfetch):
    transactions = [('institution','account','account_id','date_transacted') + TRANS_ATTRS + ('date_posted',)] # csv header
    url = lastfetch['url']
    print("Getting accounts....")
    data = get_data(url)
    for account in data['accounts']:
        aid = account['id']
        print(f"Fetching {account.get('org',{}).get('name','Unknown')} - {account.get('name')}")
        prevtrans = set(lastfetch.get(aid+"-prev",[]))
        newprev = list(prevtrans)
        newprev_time = lastfetch.get(aid+"-start",0)
        trans = get_data(account=account['id'], start=lastfetch.get(aid+"-start",1))
        lastfetch[aid+'-info'] = account
        skipped = 0
        for account2 in trans['accounts']:
            print(f"{len(account2['transactions'])} transactions.")
            for t in account2['transactions']:
                tid = t['id']
                if tid in prevtrans:
                    skipped += 1
                    continue
                lt = output_transaction(account, t, transactions)
                if lt > newprev_time:
                    lastfetch[aid+"-start"] = lt
                    newprev = [tid]
                elif lt == newprev_time:
                    newprev.append(tid)
            lastfetch[aid+"-start"] = newprev
            if skipped: print("{skipped} skipped.")
    if len(transactions) > 1:
        with open(f"T-{str(int(time.time()))}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(transactions)
    return lastfetch

if __name__ == "__main__":
    try:
        lastfetch = json.loads(open("status.json","r").read())
    except:
        print("Starting from scratch. Provide TOKEN as argument.")
        url = new_app_setup(sys.argv[1])
        lastfetch = {'url':url}
        # save in case something fails
        open("status.json","w").write(json.dumps(lastfetch))
    newstate = update(lastfetch)
    open("status.json","w").write(json.dumps(newstate))
