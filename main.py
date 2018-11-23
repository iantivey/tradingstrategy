import requests
import json

debug = False

api_prefix = 'https://api.iextrading.com/1.0/'
#symbols = ['PTY','JUST','EMB','LQD']
symbols = ['PTY','JUST']

def batch_request():
	api_function = 'stock/market/batch?symbols='
	batch_request_types = ['ohlc']
	api_request = api_prefix + api_function
	for symbol in symbols:
		api_request = api_request + symbol + ","
	api_request = api_request[:len(api_request)-1] + "&types=ohlc"
	if debug:
		print(api_request)
	resp = requests.get(api_request)
	if resp.status_code != 200:
		raise ApiError('Batch request {}'.format(resp.status_code))
	return resp.json()

data = batch_request()

if debug:
	print(data)


for symbol in symbols:
	
	closing_price = data[symbol]["ohlc"]["close"]["price"]
	print(symbol + ": Closing Price = " + str(closing_price))
	#ohlc = ticker["ohlc"]
	#print(ohlc)



#for ohlc in data:
#	print(ohlc)

#resp = requests.get('https://api.iextrading.com/1.0/stock/pty/ohlc')
#if resp.status_code != 200:
#	raise ApiError('GET /blah/ {}'.format(resp.status_code))
#ohlc = resp.json()
#close = ohlc["close"]
#print(close["price"])

