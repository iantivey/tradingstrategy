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

	if debug:
		print("short_signal::ema_short: " + str(ema_short))
		print("short_signal::email_long: " + str(ema_long))

	#if short term signal just dipped below long term signal then indicate a sell
	if(ema_long[0] > ema_short[0]):
		if(ema_long[1] < ema_short[1]):
			go_short = True
	
	return go_short

def ema_crossover_signal(values, short_horizon, long_horizon):
	signal = 0
	ema_short = ema_calc(values, short_horizon)
	ema_long = ema_calc(values, long_horizon)

	if short_signal(ema_short, ema_long):
		signal = -1
	else:
		if long_signal(ema_short, ema_long):
			signal = 1
		else:
			signal = 0

	return signal

def signals_to_string(signal):
	switcher = {
		-1: "sell",
		0: "hold",
		1: "buy"
	}
	return switcher.get(signal, "signal_error")

#main()
historical_data = batch_request(['chart'], '1y')

for symbol in historical_data:
	print (symbol)

	closing_vals = extract_chart_closing_vals(historical_data[symbol]['chart'])
	
	if debug:
		print("closing values")
		print (closing_vals)

	print("13-48 cross signal")
	print(signals_to_string(ema_crossover_signal(closing_vals, 13, 48)))

	print("50-200 cross signal")
	print(signals_to_string(ema_crossover_signal(closing_vals, 50, 200)))

	#print(data)





