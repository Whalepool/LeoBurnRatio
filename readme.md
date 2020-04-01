# Bitfinex LEO Burn to volume Ratio script by @whalepoolbtc - https://whalepool.io   

example run `python calculate.py`

- Imports leo burn data [data/leoburns.data]
- Resamples to 3h period (as the burn is 1m after the 3h open)
- Gets the LEO candle data [ohlcv - data/LEOUSD_3H_2018-01-01-present.csv]
- Merges the 2 data sets, normalises the amount of LEO burned to USD
- Gets the BTC candle data [ohlcv - data/BTCUSD_3H_2018-01-01-present.csv]
- Produces normalsied USD volume from BTCUSD['volume'] * open (since the LEO burn happens 1m after the open)
- Gets an 8 period EMA of (the LEO burn amount in USD and the BTC volume in USD)
- Calculates the correlation (main number top of the chart)
- Calculates a rolling 10 period correlation which gets plotted (orange line)
- Outputs chart

  
For more info join [@whalepoolbtc](https://t.me/whalepoolbtc) on telegram   

## Example output 

![Example output](https://i.imgur.com/Jhbb2dd.png)


