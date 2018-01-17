from .base import AbstractRiskManager
from ..event import OrderEvent


class ExampleRiskManager(AbstractRiskManager):
    def refine_orders(self, portfolio, sized_order):
        """
        This ExampleRiskManager object simply lets the
        sized order through, creates the corresponding
        OrderEvent object and adds it to a list.
        """

        order_event = OrderEvent(
            ticker=sized_order.ticker,
            action=sized_order.action,
            quantity=sized_order.quantity,
            isclose=sized_order.isclose,
            signal_id=sized_order.signal_id
        )
        return [order_event]
