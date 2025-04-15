This is a simple, command line/text/spreadsheet compatible utility for aggregating transaction data from your financial institutions.

Probably works for many major US bank & credit institutions.

Makes use of simplefin bridge (https://beta-bridge.simplefin.org/)

You have to:
 - set up an account there
 - set up an "app" and get the "setup token" (save that! see below)
 - pay a small amount to enable intetgration
 - go to "my account" and add institutions
 - install `python` on your computer
 - install requests module: `pip install requests`
 - might need dbm module installed if it doesn't come with your python
 - edit 'env' file for parameters
 
Authorize this script for you:

  `python fetch.py <setup token from above>`

This script keeps sensitive state in `status.json` and `trans.db`, and outputs transactions to CSV files `T-<time>.csv`

You should run every 24 hours:

    python fetch.py

You can run to report your current balances and net:

    python balances.py`

You can run to report per account transaction flow:

    python summarize.py T-<time>.csv

Clear all state to start over with (does not delete transaction files):

    python clear.py

Caveats:
 - assumes all accounts use same currency (could be extended)

