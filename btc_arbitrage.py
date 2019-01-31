
import requests, time
import pandas as pd
from datetime import datetime


def exchange_coinbase():

	global bid_coinbase, ask_coinbase
	bid_tick = requests.get('https://api.coinbase.com/v2/prices/sell?currency=USD')
	ask_tick = requests.get('https://api.coinbase.com/v2/prices/buy?currency=USD')
	ls_coinbase.append((ask_tick,bid_tick))

	if 'error' in bid_tick.json() or 'error' in ask_tick.json():
		print ('Error Received, reattempt will be attempted after 5 mins!')
		print ('Ask Tick:',ask_tick.json())
		print ('Bid Tick:',bid_tick.json())
		time.sleep(300)

	else:
		bid_coinbase = float(bid_tick.json()['data']['amount'])
		ask_coinbase = float(ask_tick.json()['data']['amount'])
	

def exchange_cex():

	global bid_cex, ask_cex
	tick = requests.get('https://cex.io/api/ticker/BTC/USD')
	ls_cex.append(tick)

	if 'error' in tick.json():
		print ('Error Received, reattempt will be attempted after 5 mins!')
		print ('Tick:',tick.json())
		time.sleep(300)
	else:
		bid_cex = tick.json()['bid']
		ask_cex = tick.json()['ask']
	

def check_arb():
	global bid_coinbase, ask_coinbase, bid_cex, ask_cex, commission_coinbase, commission_cex

	trade = 0
	if bid_coinbase*(1 - commission_coinbase/100) - ask_cex*(1 + commission_cex/100) > 0:
		trade = 'Buy on CEX, Sell on Coinbase' 
		print (trade)
	elif bid_cex*(1 - commission_cex/100) - ask_coinbase*(1 + commission_coinbase/100) > 0:
		trade = 'Buy on Coinbase, Sell on CEX'
		print (trade)
	return trade





commission_coinbase = 1.49	#in percentage, https://support.coinbase.com/customer/en/portal/articles/1826294-how-are-fees-applied-when-i-buy-or-sell-digital-currency-
commission_cex = 0.25		#in percentage, https://www.finder.com/sg/cex-io-bitcoin-review
quantity = 1 # 1 bitcoin


ask_coinbase = None
bid_coinbase = None
ask_cex = None
bid_cex = None
arb_pt = 0


ls_coinbase = []
ls_cex = []
data = []


last_hour = datetime.now().hour
while True:
	current_time = datetime.now()
	current_hour = current_time.hour
	
	exchange_coinbase()
	exchange_cex()

	print ('Time:',current_time)
	print ('Coinbase\tAsk:',ask_coinbase,'\tBid:',bid_coinbase)
	print ('CEX\t\tAsk:',ask_cex,'\tBid:',bid_cex)
	
	arb = check_arb()
	if arb != 0:
		arb_pt += 1

	if data[-1]['Ask_Coinbase'] != ask_coinbase or data[-1]['Bid_Coinbase'] != bid_coinbase or data[-1]['Ask_CEX'] != ask_cex or data[-1]['Bid_CEX'] != bid_cex:
		data.append({'Ask_Coinbase':ask_coinbase,'Bid_Coinbase':bid_coinbase,'Ask_CEX':ask_cex,'Bid_CEX':bid_cex,'Arb':arb,'Time':current_time})
	
	print ('Total arbitrage points:\t',arb_pt)
	print ('\n')
	
	if current_hour != last_hour:
		last_hour = current_hour
		df = pd.DataFrame(data)
		df.to_csv('data.csv')