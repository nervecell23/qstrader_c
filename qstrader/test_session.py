from .price_handler.mt4_exported_bar_csv import Mt4CsvBarPriceHandler
from .compat import queue
from research.entry_results import EntryResults
from research.atr_based_samples import ATRBasedSamples
from research.wave_research1 import WaveResearch1
from research.wave_research2 import WaveResearch2
from research.wave_research3 import WaveResearch3

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

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
        self.after_math = None
        self._config_session()
        self.cur_time = None
        self.stats = EntryResults()

    def _config_session(self):
        if self.price_handler == "MT4":
            self.price_handler = Mt4CsvBarPriceHandler(
                    self.config.CSV_DATA_DIR,
                    self.events_queue, self.tickers, start_date=self.start_date,
                    end_date=self.end_date)

        # ======================================================================
        # HERE ADD AFTERMATH PROCESS - each aftermath process is executed after
        # each test is done
        self.aftermath = ATRBasedSamples()
        # ======================================================================

        


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

        # This part of code is used in "Find Entry" project
        #----------------------------------------------------------------
        """
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
        """
        #================================================================
        #self.aftermath.commence(self.strategy.df_price)
        print("------------------------------")
        print("ONE TEST COMPLETE")
        #================================================================
        
        # Investigate how big is retracement after MACD-price divergence
        #----------------------------------------------------------------
        """
        (s1, s2) = self.strategy.macd_dd.performance_test()
        self.strategy.macd_dd.plot()
        print("Mean: {:.4f}  Std: {:.4f}".format(s1, s2))
        """

        # Research #2 phase #1.1(by year = False) / #1.3(by year = True)
        #---------------------------------------------------------------

        test_obj = WaveResearch1(self.strategy.macd_dd, is_byYear=False)
        return test_obj.mt_stats()
        


        

        # Research #2 phase #1.2
        #----------------------------------------------------------------
        """ 
        rslt = Counter()
        for zone in self.strategy.newwave_startpoint_record:
            rslt[zone] += 1
         
        #self.strategy.macd_dd.plot()
        
        return rslt
        """
        # Research #2 phase #2.1
        #---------------------------
        """ 
        test_obj = WaveResearch2(self.strategy.macd_dd)
        test_obj.process()
        return None
        """
        # Research #3
        #---------------------------
        """
        test_obj = WaveResearch3(self.strategy.macd_dd.mt)
        r = test_obj.process()
        """
        # Research #6
        #---------------------------
        """
        r = self.strategy.wr6.ctr_list
        r2 = self.strategy.wr6.non_retrace_ctr_list
        total_real = sum(r)
        print('Total number of fake crossing: {}'.format(self.strategy.wr6.total))
        print('Among which followed by real crossing: {}'.format(total_real))
        p, x = np.histogram(r, range=[0.0, 6.0], bins=6)
        p2, x2 = np.histogram(r2, range=[0.0, max(r2)+1], bins=max(r2)+1)
        print('Distribution:')
        print(p)
        print('Non-retrace Distribution:')
        print(p2)
        x = x[:-1]
        fig, ax = plt.subplots()
        ax.bar(x, p, width=0.2)
        ax.set_xticks(x)
        from pudb import set_trace; set_trace()
        plt.show()
        """

        
        
        
        
        
        

  
