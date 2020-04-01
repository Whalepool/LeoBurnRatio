import pandas as pd 
from pprint import pprint
from datetime import datetime
import talib as ta

dataset = []
node = []
counter = 0 

fname = 'data/leoburns.data'
with open(fname) as f:
    lines = f.read().splitlines() 

for l in lines: 
  counter += 1 
  if counter == 4:
    counter = 1
    dataset.append(node)
    node = []

  if counter == 1:
    node.append(datetime.strptime(l, '%Y-%m-%d %H:%M:%S'))
  if counter == 2:
    node.append(l)
  if counter == 3:
    node.append(float(l.replace(',','')))


leodf = pd.DataFrame(dataset)
leodf.columns = ['Timestamp','TxId','leo_burn_amount']
leodf.set_index(leodf['Timestamp'], inplace=True)
leodf.sort_index(inplace=True)

leodf_resampled = leodf.resample('3H', closed='left', label='left').mean()
leodf_resampled = leodf_resampled.shift(-1)


leo_candles = pd.read_csv('data/LEOUSD_3H_2018-01-01-present.csv', parse_dates=[0], infer_datetime_format=True)
leo_candles.set_index(leo_candles['timestamp'], inplace=True)
leo_candles.sort_index(inplace=True)
leo_candles.rename(columns={'open': 'leo_open', 'volume': 'leo_volume'}, inplace=True)
leo_candles.drop(['timestamp','high','low','close'], axis=1, inplace=True)


output = pd.concat([leo_candles, leodf_resampled], axis=1)
output['burn_amount_usd'] = output['leo_burn_amount'] * output['leo_open']


btc_candles = pd.read_csv('data/BTCUSD_3H_2018-01-01-present.csv', parse_dates=[0], infer_datetime_format=True)
btc_candles.set_index(btc_candles['timestamp'], inplace=True)
btc_candles.sort_index(inplace=True)
btc_candles.rename(columns={'open': 'btc_open', 'volume': 'btc_volume'}, inplace=True)
btc_candles.drop(['timestamp','high','low','close'], axis=1, inplace=True)
btc_candles['btc_usd_volume'] = btc_candles['btc_volume'] * btc_candles['btc_open']


output = pd.concat([output, btc_candles], axis=1)
output['burn_amount_usd_EMA'] = ta.EMA(output['burn_amount_usd'].ffill(), 8)
output['btc_usd_volume_EMA'] = ta.EMA(output['btc_usd_volume'], 8)



import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch
import matplotlib.patches as mpatches
# from matplotlib.finance import candlestick_ohlc
from matplotlib.ticker import ScalarFormatter, NullFormatter


output['m2dates'] = output.index.map(mdates.date2num)
number_correlation = output['burn_amount_usd_EMA'].corr(output['btc_usd_volume_EMA'])
output['corr'] = output['burn_amount_usd_EMA'].rolling(10).corr(output['btc_usd_volume_EMA'])
output['corr_smoothed'] = ta.EMA(output['corr'], 8)
output = output['2019-06-01 00:00':]

pprint(output.to_csv('output.csv', encoding='utf-8'))

pprint(output.tail(20))

fig = plt.figure(facecolor='black', figsize=(22, 12), dpi=100)

# Plot into a rectangle
rect1 = [0.1, 0.1, 1, 1]

# Add this rectangle to the figure
ax1 = fig.add_axes(rect1, facecolor='#f6f6f6')  

# Add the title to the axis
ax1.set_title( 'LEO Burns to BTC USD Price correlation: '+str(number_correlation), fontsize=20, fontweight='bold')

# Set the date as the x axis 
ax1.xaxis_date()
fig.autofmt_xdate()

ax1.plot(output.index.values, output['burn_amount_usd_EMA'], color='blue') 
ax1.set_xlabel("8 EMA USD LEO Burn amount", fontsize=10)
ax1.tick_params(axis='y', colors='blue')

ax1t = ax1.twinx()
ax1t.plot(output.index.values, output['btc_usd_volume_EMA'], color='red')    
ax1t.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
ax1t.set_xlabel("8 EMA Smoothed USD Normalised BTCUSD volume", fontsize=10)
ax1t.tick_params(axis='y', colors='red')

ax2t = ax1.twinx()
ax2t.plot( output.index.values, output['corr_smoothed'], color='orange')
ax2t.spines["right"].set_position(("axes", 1.05))
ax2t.set_xlabel("Rolling 10 day window correlation", fontsize=10)
ax2t.tick_params(axis='y', colors='orange')


h = [
  mpatches.Patch(color='blue', label='USD normalised LEO burn amount'),
  mpatches.Patch(color='red', label='USD normalised BTCUSD volume'),
  mpatches.Patch(color='orange', label='Rolling 10 day window correlation'),
]

ax1.legend(handles=h, loc='upper left')


filename = 'output.png'
plt.savefig(filename, bbox_inches='tight')