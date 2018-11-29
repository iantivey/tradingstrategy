
#!/usr/bin/env python3
import requests
import json

debug = False

api_prefix = 'https://api.iextrading.com/1.0/'
symbols = ['PTY','JUST','EMB','LQD','UNG']
active_symbols=['INDA']

fidelity_sector_etfs = ['FENY', 'FNCL','FHLC', 'FIDU', 'FTEC', 'FMAT', 'FCOM', 'FUTY', 'FREL', 'FDIS', 'FSTA']
fidelity_broad_etfs = ['ONEQ', 'FDVV', 'FDRR', 'FDMO', 'FDLO', 'FVAL', 'FQAL', 'FIDI', 'FIVA']
fidelity_bond_etfs = ['FDHY', 'FLDR', 'FBND', 'FLTB', 'FCOR']

ishares = []
ishares.append(['IVV', 'EFA', 'IEFA', 'AGG', 'IEMG', 'IJH', 'IWM', 'IJR', 'LQD', 'EEM', 'TIP', 'IVW', 'USMV', 'IWR', 'SHV', 'SHY'])
ishares.append(['IWB', 'EWJ', 'ITOT', 'IVE', 'PFF', 'EMB', 'HYG', 'FLOT', 'IXUS', 'MBB', 'IAU', 'MUB', 'IGSB', 'IEF', 'ACWI' 'EFAV'])
ishares.append(['SCZ', 'IWV', 'IBB', 'IEI', 'EZU', 'EWZ', 'IJK', 'TLT', 'GOVT', 'HDV', 'IJT', 'IJS', 'IJJ', 'FXI', 'EFV', 'IGIB'])
ishares.append(['ITA', 'IUSG' 'DGRO', 'IUSV', 'SLV', 'EEMV', 'OEF', 'INDA', 'AAXJ', 'MCHI', 'EWY', 'EFG', 'EWT', 'ACWV', 'ACWX', 'HEFA']) 
ishares.append(['SHYG', 'IHI', 'IEUR', 'EWC', 'EWG', 'IUSB', 'STIP', 'EWH', 'ISTB', 'USIG', 'EPP', 'IEV', 'GVI', 'ICF', 'IOO', 'EWU'])
ishares.append(['SUB', 'IGV', 'IYG', 'HEZU', 'SLQD', 'IGM', 'GSG', 'SOXX', 'REM', 'EWA', 'DSI', 'ILF', 'IYY', 'AOR', 'IHF', 'IDEV', 'HEWJ', 'CMF', 'EUFN', 'EWP'])

symbols = symbols + fidelity_sector_etfs + fidelity_broad_etfs + fidelity_bond_etfs
for ishare in ishares:
	symbols = symbols + ishare
#
#symbols = ['MBB']

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
		print('batch_request::api_request::'+api_request)

	resp = requests.get(api_request)

	if resp.status_code != 200:
		raise ApiError(api_request + ':: {}'.format(resp.status_code))

	return resp.json()
#end def batch_request

def json_print(to_print):
	print (json.dumps(to_print, indent=4, sort_keys=True))

def calc_ema_seed(values, time_horizon): #calculates SMA of time period leading into EMA calc period
	try:
		i=0
		m = len(values) - time_horizon - 1
		if debug:
			print("calc_ema_seed::m::" + str(m))
		seed = 0
		for z in range(m - time_horizon, m):
			seed = seed + values[z]
			i = i + 1
			if debug:
				print("calc_ema_seed::i::" + str(i))
				print("calc_ema_seed::z::" + str(z))
				print("calc_ema_seed::values[z]::" + str(values[z]))

		seed = seed / i

		if debug:
			print("EMA_seed::seed::" + str(seed))

	except IndexError:	
		seed = 0

	return seed

def ema_calc3(values, time_horizon):
	#[todays price * multiplier] + [ema(yest) * multiplier]
	#calculate initial value for yesterdays EMA by calculating SMA across first time_horizon values
	for x in range(0 to time_horizon-1):
		SMA = SMA + values[x]

	SMA = SMA / time_horizon	

	EMA = SMA
	#EMA = calc_ema_seed(values, time_horizon)

	vlen = len(values)

	multiplier = 2 / (time_horizon + 1)

	try:
		for x in range(time_horizon, vlen):
			EMA_seed = EMA
			EMA = (values[x] * multiplier) + (EMA_seed * multiplier)

			if debug:
				print('ema_calc3::x::' + str(x))

	except IndexError:
		EMA = 0
		EMA_seed = 0
    return [EMA,EMA_seed]


def ema_calc(values, time_horizon):
    #calculates time_horizon-days EMA of values. Expects values in list to be newest to oldest
    #EMA<today> = (Price<today> * k) + (EMA<yesterday> * (1-k)
    # where K = 2 / (N + 1)
    # where N = length of EMA
    k = 2 / (time_horizon + 1)

    n = len(values) #this is the index of the latest item in the list of values
    
    #############################
    # NEED TO CATCH IndexError here and return 0, 0
    #############################
    #use closing price from time_horizon -1 to seed the calc
    try:
    	EMA = calc_ema_seed(values, time_horizon)
    	if debug:
    		print("ema_calc::EMA'::" + str(EMA))

    	for x in range(n-time_horizon, n):
        	EMA_seed = EMA
        	EMA = (values[x] * k) + (EMA_seed * (1-k))
        	if debug:
        		print("ema_cals::value::" + str(values[x]))
        		print("ema_calc::EMA::" + str(EMA))
    except IndexError:	
    	EMA = 0
    	EMA_seed = 0
#    print(values)
    if debug:
    	print('EMA-' + str(time_horizon) + ': ' + str(EMA))
    #EMA = today's EMA; EMA_seed = yesterday's EMA
    return [EMA,EMA_seed]
#end ema_calc

def ema_calc2(values, time_horizon):
	n = len(values)

	multiplier = 2 / (time_horizon + 1)

	#calculate initial EMA using SMA
	try:
		m = n - time_horizon - 1
		EMA = 0
		for z in range(m - time_horizon, m):
			EMA = EMA + values[z]

		EMA = EMA / time_horizon

		for x in range(n-time_horizon, n):
			EMA_seed = EMA
			EMA = (values[x] - EMA_seed) * multiplier + EMA_seed
			if debug:
				print("ema_calc::value::" + str(values[x]))
				print("ema_calc::EMA" + str(time_horizon) + "::" + str(EMA))

	except IndexError:
		EMA = 0
		EMA_seed = 0

	return [EMA,EMA_seed]

def extract_chart_closing_vals(chart_json):
	#extracts the closing values from a chart json object and returns a list ordered newest to oldest
	closing_vals=[]

	for daily_vals in chart_json:
		closing_vals.append(daily_vals['close'])
		if debug:
			print("extract_chart_closing_vals::date::" + daily_vals['date'] + "::close::" + str(daily_vals['close']))

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
		print("short_signal::ema_short:: " + str(ema_short))
		print("short_signal::email_long:: " + str(ema_long))

	#if short term signal just dipped below long term signal then indicate a sell
	if(ema_long[0] > ema_short[0]):
		if(ema_long[1] < ema_short[1]):
			go_short = True
	
	return go_short

def ema_crossover_signal(values, short_horizon, long_horizon):
	signal = 0
	ema_short = ema_calc3(values, short_horizon)
	ema_long = ema_calc3(values, long_horizon)

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

def run_calcs():
	#main()
	historical_data = batch_request(['chart'], '2y')

	long_symbols_13_48 = []
	short_symbols_13_48 = []
	hold_symbols_13_48 = []
	long_symbols_50_200 = []
	short_symbols_50_200 = []
	hold_symbols_50_200 = []

	for symbol in historical_data:
		if debug:
			print ('main::symbol::' + symbol)
		closing_vals = extract_chart_closing_vals(historical_data[symbol]['chart'])
		
		if debug:
			print("main::closing values count::"+str(len(closing_vals)))
			print("main::closing values::")
			print (closing_vals)

		#calculate the 13 day / 48 day cross over
		
		signal_13_48 = ema_crossover_signal(closing_vals, 13, 48)
		if signal_13_48 == -1:
			short_symbols_13_48.append(symbol)
		if signal_13_48 == 1:
			long_symbols_13_48.append(symbol)
		if signal_13_48 == 0:
			hold_symbols_13_48.append(symbol)
		
		if debug:
			print("main::13-48 cross signal::")
			print(signals_to_string(signal_13_48))

		signal_50_200 = ema_crossover_signal(closing_vals, 50, 200)

		if signal_50_200 == -1:
			short_symbols_50_200.append(symbol)
		if signal_50_200 == 1:
			long_symbols_50_200.append(symbol)
		if signal_50_200 == 0:
			hold_symbols_50_200.append(symbol)

		if debug:
			print("main::50-200 cross signal::")
			print(signals_to_string(signal_50_200))

		#print(data)
	print("-----------------------------------------------------------------")
	print("Today's Long Symbols:")
	print("13/48 - " + str(long_symbols_13_48))
	print("50/200 - " + str(long_symbols_50_200))

	print("Today's Short Symbols:")
	print("13/48 - " + str(short_symbols_13_48))
	print("50/200 - " + str(short_symbols_50_200))

	print("Today's Hold Symbols:")
	print("13/48 - " + str(hold_symbols_13_48))
	print("50/200 - " + str(hold_symbols_50_200))

	results = [short_symbols_13_48, hold_symbols_13_48, long_symbols_13_48, short_symbols_50_200, hold_symbols_50_200, long_symbols_50_200]
	return results
#end def run_calcs

#main
from http.server import BaseHTTPRequestHandler, HTTPServer
 
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  # GET
	def do_GET(self):
		ema_results = run_calcs()
		# Send response status code
		self.send_response(200)
 
        # Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()
 
		# Send message back to client
		message = "Todays Short Symbols: <br /> 13\\48:" + str(ema_results[0]) + "<br /><br />"
		message = message + "Todays Long Symbols: <br /> 13\\48:" + str(ema_results[2]) + "<br /><br />"
		message = message + "Todays Short Symbols: <br /> 50\\200:" + str(ema_results[3]) + "<br /><br />"
		message = message + "Todays Long Symbols: <br /> 50\\200:" + str(ema_results[5]) + "<br /><br />"
        
		# Write content as utf-8 data
		self.wfile.write(bytes(message, "utf8"))
		return
 
def run():
  print('starting server...')
 
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8081)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()
 
 
run()





