"""
mt4_exported_bar_csv.py
"""

import os
import pandas as pd
from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent

class Mt4CsvBarPriceHandler(AbstractBarPriceHandler):
	
	def __init__(self, csv_dir, events_queue,
			init_tickers = None,
			start_date = None,
			end_date = None,
			calc_returns = False):
		
		self.csv_dir = csv_dir
		self.events_queue = events_queue
		self.continue_backtest = True
		# Purpose of self.ticker: Work as a buffer storing ONE entry,
		# this entry is needed for calculating return when the 
		# next entry is loaded
		self.tickers = {}
		self.tickers_data = {}  # The whole data read from CSV are stored here
		if init_tickers is not None:
			for ticker in init_tickers:
				self.subscribe_ticker(ticker)
		self.start_date = start_date
		self.end_date = end_date
		self.bar_stream = self._merge_sort_ticker_data()
		self.calc_returns = calc_returns
		if self.calc_returns:
			self.calc_returns = []


	def _open_ticker_price_csv(self, ticker):
		
		ticker_path = os.path.join(self.csv_dir, "%s.csv" %ticker)
		self.tickers_data[ticker] = pd.read_csv(
						ticker_path, 
						header=None, 
						parse_dates=True,
						index_col=0, 
						names=["Date","Time","Open","High","Low",
							"Close","Vol"]
						)
		self.tickers_data[ticker]["Ticker"] = ticker 

	def subscribe_ticker(self, ticker):
		if ticker not in self.tickers:
			try:
				self._open_ticker_price_csv(ticker)
				dft = self.tickers_data[ticker]
				row0 = dft.iloc[0]
				close = PriceParser.parse(row0["Close"])
				ticker_prices = {"close": close, "timestamp": dft.index[0]}
				self.tickers[ticker] = ticker_prices
			except OSError:
				print("Could not subscribe ticker $s"
					"as no data CSV found for pricing" %ticker)
		else:
			print("Could not subscribe ticker %s"
				"as is already subscribed" %ticker)

	def _merge_sort_ticker_data(self):
	
		df = pd.concat(self.tickers_data.values()).sort_index()
		start = None
		end = None
		if self.start_date is not None:
			start = df.index.searchsorted(self.start_date)
		if self.end_date is not None:
			end = df.index.searchsorted(self.end_date)
		df["colFromIndex"] = df.index
		df = df.sort_values(by=["colFromIndex","Ticker"])
		# According to start and end index, select corresponding data
		if start is None and end is None:
			return df.iterrows()
		elif start is not None and end is None:
			return df.ix[start:].iterrows()
		elif start is None and end is not None:
			return df.ix[:end].iterrows()
		else:
			return df.ix[start:end].iterrows()

	def _create_event(self, index, period, ticker, row):
		
		"""
		Obtain all elements of the bar from a row of ticker_data
		then return a bar event
		"""
		open_price = PriceParser.parse(row["Open"])
		high_price = PriceParser.parse(row["High"])
		low_price = PriceParser.parse(row["Low"])
		close_price = PriceParser.parse(row["Close"])
		volume = PriceParser.parse(row["Vol"])
		bev = BarEvent(ticker, index, period, open_price, high_price,
				low_price, close_price, volume)
		return bev

	def _store_event(self, event):
			
		ticker = event.ticker
		# If calc_returns flag is True, then calculate and store the full
		# list of returns in a list
		if self.calc_returns is not False:
			prev_close = self.tickers[ticker]["close"] / float(PriceParser.PRICE_MULTIPLIER)
			cur_close = event.close_price / float(PriceParser.PRICE_MULTIPLIER)
			self.tickers[ticker]["return"] = cur_close / prev_close - 1.0
			self.calc_returns.append(self.tickers[ticker]["return"])
			
		self.tickers[ticker]["close"] = event.close_price
		self.tickers[ticker]["timestamp"] = event.time

	def stream_next(self):
		try:
			index, row = next(self.bar_stream)
		except StopIteration:
			self.continue_backtest = False
			return
		ticker = row["Ticker"]
		period = 86400
		bev = self._create_event(index, period, ticker, row)
		self._store_event(bev)
		self.events_queue.put(bev)	
		

				
		
