from .base import AbstractPositionSizer
from qstrader.price_parser import PriceParser 

class MoreLossLessLots(AbstractPositionSizer):
    """
    Position size is inversely proportional to
    the number of loss trades in the history
    """
    # initial order is the recommended order size
    # determined by the strategy
    def __init__(self, initial_quantity=0):
        self.initial_quantity = initial_quantity
        self.max_risk = 0.05
        self.decrease_factor = 3.0
        self.init_lot = 0.1
        
        self.base_quantity = 100000
    
    def size_order(self, portfolio, initial_order):
        # Deal with EXIT action: 
       
        if initial_order.action == "EXIT":

            ticker = initial_order.ticker
  
            invested_action = portfolio.positions[ticker].action
            if invested_action == "BOT":
                initial_order.action = "SLD"
            else:
                initial_order.action = "BOT"

            initial_order.quantity = abs(portfolio.positions[ticker].quantity)
            return initial_order


        """
        lot = self.init_lot
        free_margin = PriceParser.display(portfolio.free_margin)
        lot = round(free_margin*self.max_risk/1000.0,1)
        ticker = initial_order.ticker
        cur_timestamp = portfolio.price_handler.get_last_timestamp(ticker)
        loss = 0
        # Find number of loss in the past month
        for pos in portfolio.closed_positions:
            if pos.open_timestamp.year == cur_timestamp.year and\
                pos.open_timestamp.month == cur_timestamp.month:
                if pos.realised_pnl < 0:
                    loss += 1
        
        if loss > 1:
            lot = round(lot - lot*loss/self.decrease_factor,1)

        if lot < 0.1:
            lot = 0.1

        initial_order.quantity = int(lot*self.base_quantity)
        """
        if initial_order.quantity < 0:
            from pudb import set_trace; set_trace()
        return initial_order
