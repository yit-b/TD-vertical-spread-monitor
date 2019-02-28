To use this script, you need a TD account with developer access.

Once you have developer access, follow the steps here to obtain a refresh token:
https://developer.tdameritrade.com/content/simple-auth-local-apps

Insert your account number, client ID, and refresh token in the constants at the
head of the script.

Run with `python vertical_watcher.py symbol` where symbol is the underlying you
wish to monitor. Default is SPX. The TD API only supports tradable underlyings
except futures and forex. Some indexes are supported including SPX.

The script sends an OSX alert any time the underlying crosses a strike. If you
aren't using OSX, disable this component.

![Example]()
