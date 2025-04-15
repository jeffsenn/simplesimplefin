import json
import os
lastfetch = json.loads(open("status.json","r").read())
open("status.json","w").write(json.dumps({'url':lastfetch['url']}))
os.remove("trans.db")


