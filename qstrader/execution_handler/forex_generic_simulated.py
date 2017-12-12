"""
forex_generic_simulated.py
"""

from .base import AbstractExecutionHandler
from ..event import (FillEvent, EventType)

class ForexGenericSimulatedExecution(AbstractExecutionHandler):
    """
    Things not taken into account yet:
    - Trading session (Time zone)
    - Spread
    """
    
    def __init__(self, event_queue, price_handler, compliance=None):
        self.events_queue = event_queue
        self.price_handler = price_handler
        self.compliance = compliance

    #TODO: Add module that handles spread
    #TODO: Add module that handles ticks
    
    def execute_order(self, event):

        if event.type == EventType.ORDER:
            ticker = event.ticker
            action = event.action
            quantity = event.quantity
            timestamp = self.price_handler.get_last_timestamp(ticker)
            isclose = event.isclose
            action_price = self.price_handler.get_last_close(ticker)
            fill_price = action_price
        # No exchange in FX trading
        exchange = "-"
        # No commission in FX trading
        commission = 0

        fill_event = FillEvent(timestamp, ticker, action, quantity,
                               exchange, fill_price, commission, isclose)
        self.events_queue.put(fill_event)

        if self.compliance is not None:
            self.compliance.record_trade(fill_event)
    
