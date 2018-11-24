import requests
import json

debug = False

api_prefix = 'https://api.iextrading.com/1.0/'
symbols = ['PTY','JUST','EMB','LQD']
#symbols = ['PTY','JUST']

def batch_request(batch_request_types, range=False):
	api_function = 'stock/market/batch?symbols='

	api_request = api_prefix + api_function

	for symbol in symbols:
		api_request = api_request + symbol + ","	
	api_request = api_request[:len(api_request)-1] + "&types=" #strip the , off the end of the request URL


	for batch_request_type in batch_request_types:
		api_request = api_request+batch_request_type+','
	api_request = api_request[:len(api_request)-1] #strip the , off the end

	if range != False:
		api_request = api_request + '&range=' + range

	if debug:
		print(api_request)

	resp = requests.get(api_request)

	if resp.status_code != 200:
		raise ApiError(api_request + ':: {}'.format(resp.status_code))

	return resp.json()
#end def batch_request

def json_print(to_print):
	print (json.dumps(to_print, indent=4, sort_keys=True))

def ema_calc(values, time_horizon):
    #calculates time_horizon-days EMA of values. Expects values in list to be newest to oldest
    #EMA<today> = (Price<today> * k) + (EMA<yesterday> * (1-k)
    # where K = 2 / (N + 1)
    # where N = length of EMA
    k = 2 / (time_horizon + 1)

    n = len(values) #this is the index of the latest item in the list of values
    
    #use closing price from time_horizon -1 to seed the calc
    EMA = values[n-time_horizon-1]

    for x in range(n-time_horizon, n):
        EMA_seed = EMA
        EMA = (values[x] * k) + (EMA_seed * (1-k))

    #EMA = today's EMA; EMA_seed = yesterday's EMA
    return [EMA,EMA_seed]
#end ema_calc

def extract_chart_closing_vals(chart_json):
	#extracts the closing values from a chart json object and returns a list ordered newest to oldest
	closing_vals=[]

	for daily_vals in chart_json:
		closing_vals.append(daily_vals['close'])
		if debug:
			print("extract_chart_closing_vals:" + daily_vals['date'] + ": " + str(daily_vals['close']))

	return closing_vals
#end extract_chart_closing_vals

def close_from_ohlc(ohlc_json):
	#returns the closing valud from an OHLC JSON object
	return 0
#end close_from_ohlc

def long_signal(ema_short, ema_long):
	go_long = False

	# if short term signal went over longer term signal then indicate buy
	if(ema_short[0] > ema_long[0]):
		if(ema_short[1] < ema_long[1]):
			go_long = True

	return go_long

def short_signal(ema_short, ema_long):
	go_short = False

	print("EMA Short: " + str(ema_short))
	print("EMA Long: " + str(ema_long))

	#if short term signal just dipped below long term signal then indicate a sell
	if(ema_long[0] > ema_short[0]):
		if(ema_long[1] < ema_short[1]):
			go_short = True
	
	return go_short

historical_data = batch_request(['chart'], '3m')

for symbol in historical_data:
	if debug:
		print (symbol)

	closing_vals = extract_chart_closing_vals(historical_data[symbol]['chart'])
	if debug:
		print("closing values")
		print (closing_vals)

	ema_13 = ema_calc(closing_vals, 13)
	ema_48 = ema_calc(closing_vals, 48)

	if debug:
		print("EMA 13:" + str(ema_13))
		print("EMA 48:" + str(ema_48))
	#print(data)

	if short_signal(ema_13, ema_48):
		print("Sell " + symbol)
	else:
		if long_signal(ema_13, ema_48):
			print("Buy " + symbol)
		else:
			print("Hold " + symbol)

#data2 = batch_request(['ohlc'])

#if debug:
#	print(data2)

#


#for symbol in symbols:
	
#	closing_price = data[symbol]["ohlc"]["close"]["price"]
#	print(symbol + ": Closing Price = " + str(closing_price))
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

