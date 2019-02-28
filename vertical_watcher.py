import requests
from pprint import PrettyPrinter as pprint
import json
from datetime import datetime, timedelta, date
import time
import operator
# from osascript import osascript
import os
import sys

HEADERS = {}
ACCOUNT_NUMBER  = "XXXXXXXXX"
CLIENT_ID       = "EXAMPLE@AMER.OAUTHAP"
REFRESH_TOKEN   = "REFRESH TOKEN"

POST_ACCESS_TOKEN   = "https://api.tdameritrade.com/v1/oauth2/token"
GET_OPTION_CHAIN    = "https://api.tdameritrade.com/v1/marketdata/chains"
GET_TRANSACTIONS    = "https://api.tdameritrade.com/v1/accounts/%s/transactions"    % ACCOUNT_NUMBER
GET_ORDERS          = "https://api.tdameritrade.com/v1/accounts/%s/orders"          % ACCOUNT_NUMBER
GET_ACCOUNT         = "https://api.tdameritrade.com/v1/accounts/%s"                 % ACCOUNT_NUMBER

def get_bearer_token():
    params = {
        'grant_type' : 'refresh_token',
        'refresh_token' : REFRESH_TOKEN,
        'client_id' : CLIENT_ID
    }
    res = requests.post(POST_ACCESS_TOKEN, data=params).json()
    if('access_token' not in res):
        print(res)
        exit()

    HEADERS['Authorization'] = 'Bearer %s' % res['access_token']
    # print(HEADERS['Authorization'])

def get_account_value():
    res = requests.get(GET_TRANSACTIONS, headers=HEADERS).json()
    return res['securitiesAccount']['currentBalances']['liquidationValue']

def get_orders_ytd(symbol):
    start_date = date(date.today().year, 1, 1).strftime("%Y-%m-%d")
    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    params = {
        'symbol' : symbol,
        'fromEnteredTime' : start_date,
        'toEnteredTime' : end_date,
    }

    res = requests.get(GET_ORDERS, params=params, headers=HEADERS).json()
    return res

# def get_quote(symbol):
#     GET_QUOTE = "https://api.tdameritrade.com/v1/marketdata/%s/quotes" % symbol
#     params = {}
#     res = requests.get(GET_OPTION_CHAIN, params=params, headers=HEADERS).json()
#     return res

def get_positions():
    params = {
        'fields':'positions'
    }
    res = requests.get(GET_ACCOUNT, params=params, headers=HEADERS).json()
    return res

def get_option_chain(symbol):
    start_date = datetime.utcnow().strftime("%Y-%m-%d")
    end_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    params = {
        'symbol' : symbol,
        # 'fromEnteredTime' : start_date,
        'toDate' : end_date,
        'strikeCount' : 10,
        # 'strategy' : 'VERTICAL',
        'range': 'NTM'
    }

    res = requests.get(GET_OPTION_CHAIN, params=params, headers=HEADERS).json()

    if 'error' in res:
        print(res)
        return None

    return res

def osx_notify(title, subtitle, message):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))

def send_price_notification(symbol, strike, above=False):
    title = '%s Price Alert' % symbol
    if strike % 5 == 0:
        title += ': STRIKE PASSED'
    subtitle = 'LAST %s %.2f' % ('AT/ABOVE' if above else 'AT/BELOW', strike)
    osx_notify(title, subtitle, '')

if __name__ == '__main__':
    # fills = get_orders_ytd('SPX')
    get_bearer_token()

    # positions = get_positions()['securitiesAccount']['positions']
    # spx_positions = [p for p in positions if p['instrument']['symbol'].startswith('SPX')]
    # spx_avg_prices = [p['averagePrice'] for p in spx_positions]
    # avg_price = abs(reduce(operator.__sub__, spx_avg_prices))

    # print(avg_price)

    # with open('position.json', 'w') as f:
    #     json.dump(spx_positions, f, indent=4)

    # exit()


    last_underlying = 0
    trend = []
    symbol = sys.argv[1] if (len(sys.argv) > 1 and sys.argv[1]) else "SPX"
    vertical_width = 1
    strike = 2809

    while True:
        chain = get_option_chain(symbol)
        if chain is None:
            get_bearer_token()
            continue

        underlying = chain['underlyingPrice']
        underlying_chg = underlying - last_underlying

        alert_strike = round(underlying)

        if last_underlying <= alert_strike and underlying >= alert_strike:
            send_price_notification(symbol, alert_strike, above=True)
            # osascript('tell app "Terminal" to display dialog "SPX at or above %d"' % alert_strike)

        if last_underlying >= alert_strike and underlying <= alert_strike:
            send_price_notification(symbol, alert_strike, above=False)
            # osascript('tell app "Terminal" to display dialog "SPX at or below %d"' % strike)

        if(underlying_chg == 0):
            trend.append(' ')
        elif(underlying_chg > 0):
            trend.append('+')
        else:
            trend.append('-')
        if(len(trend) > 20):
            trend.pop(0)

        exp, dte = chain['callExpDateMap'].keys()[0].split(':')
        calls = chain['callExpDateMap'].values()[0]
        puts = chain['putExpDateMap'].values()[0]

        print('%.2f (%+.02f) [%s]' % (underlying, underlying_chg, ''.join(trend)))
        last_underlying = underlying

        for opt_map, call_put in ((calls, 'C'), (puts, 'P')):
            print('%s (%s dte)' % (call_put, dte))
            opt_map = sorted(opt_map.items(), key=lambda x: x[0])
            opts = [c[1] for c in opt_map]

            for i in range(0, len(opts) - 1):
                lower_leg = opts[i][0]
                upper_leg = opts[i+1][0]

                lower_strike = lower_leg['strikePrice']
                upper_strike = upper_leg['strikePrice']

                vert_string = '%s/%s' % (lower_strike, upper_strike)

                upper_mark = upper_leg['mark']
                lower_mark = lower_leg['mark']
                comp_mark = abs(lower_mark - upper_mark)

                upper_ask = upper_leg['ask']
                upper_bid = upper_leg['bid']

                lower_ask = lower_leg['ask']
                lower_bid = lower_leg['bid']

                comp_ask = abs(upper_ask - lower_ask)
                comp_bid = abs(upper_bid - lower_bid)

                upper_delta = upper_leg['delta']
                lower_delta = lower_leg['delta']
                comp_delta = abs(upper_delta - lower_delta)

                upper_theta = upper_leg['theta']
                lower_theta = lower_leg['theta']
                comp_theta = abs(lower_theta - upper_theta)

                # if(lower_strike > underlying or upper_strike < underlying):
                is_atm = False
                if(lower_strike < underlying and upper_strike > underlying):
                    is_atm = True
                atm_string = '>' if is_atm else ' '

                print('%s %s: M:%.2f (%.2f/%.2f) D:%.2f, T:%.2f' % (atm_string, vert_string, comp_mark, comp_bid, comp_ask, comp_delta, comp_theta))
        time.sleep(1)

    # with open('optchain.json', 'w') as f:
    #     json.dump(chain, f, indent=4)
