from .price_handler.mt4_exported_bar_csv import Mt4CsvBarPriceHandler
from .compat import queue
from research.entry_results import EntryResults

class TestingSession(object):

    def __init__(
        self, config, strategy, tickers,
        start_date, end_date, events_queue,
        price_handler,
        session_type="backtest"):
        """
        Set up the backtest variables according to
        what has been passed in.
        """
        self.config = config
        self.strategy = strategy
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.events_queue = events_queue
        self.session_type = session_type
        self.price_handler = price_handler
        self._config_session()
        self.cur_time = None
        self.stats = EntryResults()

    def _config_session(self):
        if self.price_handler == "MT4":
            self.price_handler = Mt4CsvBarPriceHandler(
                    self.config.CSV_DATA_DIR,
                    self.events_queue, self.tickers, start_date=self.start_date,
                    end_date=self.end_date)

    def _continue_loop_condition(self):
        if self.session_type == "backtest":
            return self.price_handler.continue_backtest

    def _run_session(self):
        while self._continue_loop_condition():
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                self.price_handler.stream_next()
            else:
                self.cur_time = event.time
                self.strategy.calculate_signals(event)

    def start_trading(self, single_run=False, testing=False):
        self._run_session()
        b = self.strategy.total_processed 
        a = self.strategy.total_signals
        self.stats.calculate_results(self.strategy.result_d, self.strategy.l_p_ratio, method='WIN_RATE')
        if single_run is True:
            print("---------------------------------")
            print("TEST COMPLETE ({})".format(self.strategy.entry_type))
            print("***")
            print("Signal generated: {}  Processed: {}".format(a,b))
            print("***")
            print("Mean successful rate: {:.4f}, Var: {:.4f}, ctr_flat: {}".format(self.stats.mean, self.stats.std, self.strategy.ctr_flat))
            
            print("***")
            '''
            print("none:{}, surface:{}, peak_A:{}, dive:{}, bottom_A:{}".format(
                self.strategy.ctr_none,
                self.strategy.ctr_surface,
                self.strategy.ctr_peak_A,
                self.strategy.ctr_dive,
                self.strategy.ctr_bottom_A))
            '''
        else:
            return self.stats.mean, self.stats.std
        
        

  
