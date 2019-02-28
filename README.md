# TD-vertical-spread-monitor
This is a simple python script for monitoring at-the-money vertical option chains
utilizing the TD Ameritrade API.

## Usage
Run with `python vertical_watcher.py symbol` where `symbol` is the underlying you
wish to monitor. Default is SPX. The TD API supports tradable underlyings
except futures and forex. Some indexes are supported including SPX.


### Headers
`2787.80 (+0.01) [+++ +-+----  ++-++-+]`<br/>
`last price (change) [trendline]`

`C (0 dte)`<br/>
`Call/Put (days to expiration)`

`2765.0/2770.0: M:5.15 (4.90/5.40) D:0.00, T:0.00`<br/>
`low/high legs: M:mark (bid / ask)  D:Delta  T:theta`

## Setup
To use this script, you need a TD account with developer access.

Once you have developer access, follow the steps here to obtain a refresh token:
https://developer.tdameritrade.com/content/simple-auth-local-apps

Insert your account number, client ID, and refresh token in the constants at the
head of the script.

The script sends an OSX alert any time the underlying crosses a strike. If you
aren't using OSX, disable this component.

![Example](https://raw.githubusercontent.com/BorsosWyatt/TD-vertical-spread-monitor/master/vert_watcher.png)
