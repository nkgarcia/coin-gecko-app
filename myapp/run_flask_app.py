from flask import Flask
from flask import Markup
from flask import render_template
from flask import request
from datetime import timezone
from datetime import datetime
import json
import numpy as np
import pandas as pd
from pycoingecko import CoinGeckoAPI

# Initialize Flask
app = Flask(__name__)
# Initialize the coingecko API client
cg = CoinGeckoAPI()


@app.route("/", methods=['GET'])
def dropdown():
    coin_ids = get_trending()
    coin = request.form.get("crypto_dropdown", None)
    if coin is not None:
        return render_template('chart.html', coin_ids=coin_ids, coin_id=coin)
    return render_template('chart.html', coin_ids=coin_ids)


@app.route("/", methods=['GET', 'POST'])
def chart():
    coin_ids = get_trending()
    coin = request.form.get("crypto_dropdown", None)
    if coin is not None:
        data = get_pricing(coin)
        return render_template('chart.html', prices=list(data.price), dates=list(data.datetime), coin_ids=coin_ids, coin=coin)
    return render_template("chart.html", coin_ids=coin_ids)


def get_trending():
    trending = cg.get_search_trending()
    return [coin['item']['id'] for coin in trending['coins']]


def get_pricing(coin_id):
    """Returned DF with a time series of pricing per trending coin with USD numeraire"""
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days='max')
    pricing = data['prices']
    df = pd.DataFrame(pricing, columns=['unix_datetime', 'price'])
    df['datetime'] = df.unix_datetime.apply(lambda dt: unix_to_datetime(dt))
    return df


# convert datetime to unix datetime
def datetime_to_unix(year, month, day):
    '''datetime_to_unix(2021, 6, 1) => 1622505600.0'''
    dt = datetime(year, month, day)
    # Unix epoch 1970-01-01
    timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
    return timestamp


# convert unix to datetime
def unix_to_datetime(unix_time):
    '''unix_to_datetime(1622505700)=> ''2021-06-01 12:01am'''
    ts = int(unix_time/1000 if len(str(unix_time)) > 10 else unix_time) # /1000 handles milliseconds
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d').lower()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
