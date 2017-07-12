"""
mt4_exported_bar_csv.py
"""

import os
import pandas as pd
from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent

class Mt4CsvBarPriceHandler(AbstractBarPriceHandler)
	
	def __init__(self, csv_dir, events_queue,
			init_pairs = None,
			start_date = None,
			end_date = None
			calc_returns = False):
		
		self.csv_dir = csv_dir
		self.events_queue = events_queue
		self.continue_backtest = True
		# Purpose of self.pair: Work as a buffer storing ONE entry,
		# this entry is needed for calculating return when the 
		# next entry is loaded
		self.pairs = {}
		self.pairs_data = {}  # The whole data read from CSV are stored here
		if init_pairs is not None:
			for pair in init_pairs:
				substribe_pair(pair)
		self.start_date = start_date
		self.end_date = end_date
		self.bar_stream = self._merge_sort_ticker_data()
		self.calc_returns = calc_returns
		if self.calc_returns:
			self.calc_returns = []


	def _open_pair_price_csv(self, pair):
		
		pair_path = os.path.join(self.csv_dir, "%s.csv" %pair)
		self.pairs_data[pair] = pd.read_csv(pair_path, header=None, parse_dates=[[0,1]],
						index_col=0, names=["Date","Open","High","Low",
									"Close","Vol"])
		self.pairs_data[pair]["Pair"] = pair 

	def subscribe_pair(self, pair):
		
		if pair not in self.pairs:
			try:
				self._open_pair_price_csv(pair)
				dft = pairs_data[pair]
				row0 = dft.iloc[0]
				close = PriceParser.parse(row0["Close"])
				pair_prices = {"close": close, "timestamp": dft.index[0]}
				self.pairs[pair] = pair_prices
			except OSError:
				print("Could not subscribe pair $s"
					"as no data CSV found for pricing" %pair)
		else:
			print("Could not subscribe pair %s"
				"as is already subscribed" %pair)

	def _merge_sort_pair_data(self):
	
		df = pd.concat(self.pairs_data.values()).sort_index()
		start = None
		end = None
		if self.start_date is not None:
			start = df.index.searchsorted(self.start_date)
		if self.end_date is not None:
			end = df.index.searchsorted(self.end_date)
		df["colFromIndex"] = df.index
		df = df.sort_values(by=["colFromIndex","Pair"])
		# According to start and end index, select corresponding data
		if start is None and end is None:
			return df.iterrows()
		elif start is not None and end is None:
			return df.ix[start:].iterrows()
		elif start is None and end is not None:
			return df.ix[:end].iterrows()
		else:
			return df.ix[start:end].iterrows()

	def _create_event(self, index, period, pair, row):
		
		"""
		Obtain all elements of the bar from a row of pair_data
		then return a bar event
		"""

		open_price = PriceParser.parse(row["Open"])
		high_price = PriceParser.parse(row["High"])
		low_price = PriceParser.parse(row["Low"])
		close_price = PriceParser.parse(row["Close"])
		volume = PriceParser.parse(row["Vol"])
		bev = BarEvent(pair, index, period, open_price, high_price,
				low_price, close_price, volume)
		return bev

	def _store_event(self, event):
		
		pair = event.pair
		# If calc_returns flag is True, then calculate and store the full
		# list of returns in a list
		if self.calc_returns:
			prev_close = self.pairs[pair]["close"] / float(PriceParser.PRICE_MULTIPLIER)
			cur_close = event.close / float(PriceParser.PRICE_MULTIPLIER)
			self.pairs[pair]["return"] = cur_close / prev_close - 1.0
			self.calc_returns.append(self.pairs[pair]["return"])
			
		self.pairs[pair]["close"] = event.close_price
		self.pairs[pair]["timestamp"] = event.time

	def stream_next(self):
		try:
			index, row = next(self.bar_stream)
		except StopIteration:
			self.continue_backtest = False
			return
		pair = row["Pair"]
		period = 86400
		bev = self._create_event(index, period, pair, row)
		self._store_event(bev)
		self.events_queue.put(bev)	
		

				
		
