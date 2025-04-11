Makes use of simplefin bridge (https://beta-bridge.simplefin.org/)

You have to:
 -- set up an account there
 -- set up an "app" and get the "setup token" (save that! see below)
 -- pay a small amount to enable intetgration
 -- go to "my account" and add institutions
 -- install 'python' on your computer
 -- install requests module: 'pip install requests'
 
Authorize this script for you:

  python fetch.py <setup token from above>

This script keeps sensitive state in "status.json", and outputs transactions to CSV files "T-<time>.csv"

You should run every 24 hours:

  python fetch.py

You can run to report your current balances and net:

  python balances.py

