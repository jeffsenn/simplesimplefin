import base64
import requests
import pprint
import json
import time
import csv
import os
import dbm

ERR_FILE="err.txt"
TIME_OVERLAP=3*3600*24 # 3 days

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
    
def update(lastfetch, db):
    transactions = [('institution','account','account_id','date_transacted') + TRANS_ATTRS + ('date_posted',)] # csv header
    all_errs = []
    url = lastfetch['url']
    print("Getting accounts....")
    data = get_data(url)
    now = int(time.time())
    all_errs.extend(data.get('errors'))
    for account in data['accounts']:
        aid = account['id']
        newprev_time = lastfetch.get(aid+"-start",None)
        if newprev_time: newprev_time -= TIME_OVERLAP
        else: newprev_time = 1
        trans = get_data(url, account=account['id'], start=newprev_time)
        lastfetch[aid+'-info'] = account
        lastfetch[aid+'-updated'] = now
        skipped = 0
        all_errs.extend(trans.get('errors'))        
        for account2 in trans['accounts']:
            cnt = len(account2['transactions'])
            if account2['id'] != aid: raise Exception("account id mismatch",aid, account2)
            for t in account2['transactions']:
                tid = t['id']
                tidb = tid.encode('utf8')
                if db.get(tidb):
                    skipped += 1
                    continue
                db[tidb] = json.dumps(t).encode('utf8')
                lt = output_transaction(account, t, transactions)
                if lt > newprev_time:
                    lastfetch[aid+"-start"] = lt
                    newprev_time = lt
            lastfetch[aid+"-start"] = newprev_time
            print(f"{cnt-skipped:>4}/{skipped:>4} : {account.get('org',{}).get('name','Unknown')} - {account.get('name')}")
    if len(transactions) > 1:
        fn = f"T-{str(int(time.time()))}.csv"
        with open(fn, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(transactions)
        print(":OUTPUT:",fn)
        
    if os.path.exists(ERR_FILE): os.remove(ERR_FILE)
    if len(all_errs):
        e = "\n".join(list(set(all_errs)))
        open(ERR_FILE, 'w').write(e)
        print(":ERRORS:\n", e)
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
    with dbm.open('trans.db', 'c') as db:
        newstate = update(lastfetch, db)
    open("status.json","w").write(json.dumps(newstate))
