from .base import AbstractPositionSizer
from qstrader.price_parser import PriceParser

class FixedRisk(AbstractPositionSizer):
    def __init__(self, initial_quantity=100000, max_risk=0.05, max_volatility=0.015):
        self.initial_quantity = initial_quantity
        self.max_risk = max_risk
        self.base_quantity = 100000
        self.max_volatility = max_volatility

    def size_order(self, portfolio, initial_order):
        ticker = initial_order.ticker
        if initial_order.action == "EXIT":
            from pudb import set_trace; set_trace()
            invested_action = portfolio.positions[ticker].action
            if invested_action == "BOT":
                initial_order.action = "SLD"
            else:
                initial_order.action = "BOT"

            initial_order.quantity = abs(portfolio.positions[ticker].quantity)
            return initial_order

        else:
            cur_price = portfolio.price_handler.get_last_close(ticker)
            '''
            The reason for having 'min(size_1, size_2)' is that:
            In the case that the cash available, after deducting 5% for volatility, is not 
            enough for placing the order with 'size_1', we can then only place whatever
            amount we can afford after spending all (95%) we have.
            '''
            size_1 = int(portfolio.cur_cash * self.max_risk // PriceParser.parse(self.max_volatility))
            size_2 = int(portfolio.cur_cash * (1 - self.max_risk) // cur_price)
            initial_order.quantity = min(size_1, size_2)
            initial_order.quantity = self.initial_quantity
             
        return initial_order

