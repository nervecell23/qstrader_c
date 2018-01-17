from .position import Position
import pandas as pd


class Portfolio(object):
    def __init__(self, price_handler, cash):
        """
        On creation, the Portfolio object contains no
        positions and all values are "reset" to the initial
        cash, with no PnL - realised or unrealised.

        Note that realised_pnl is the running tally pnl from closed
        positions (closed_pnl), as well as unrealised_pnl
        from currently open positions.
        """
        self.price_handler = price_handler
        self.init_cash = cash
        self.equity = cash
        self.cur_cash = cash
        self.positions = {}
        self.closed_positions = []
        self.realised_pnl = 0
        self.margin =0
        self.free_margin = 0

        # Equity data is updated everytime when new price bar
        # arrives. Flag 'new_pos_closed' is raised when a 
        # position is closed; flag 'new_order_closed' is raised
        # whenever an order is closed. The equity chart will
        # look different when use different flag to sample the
        # equity data.
        self.new_pos_closed = True
        self.new_order_closed = True

    def _update_portfolio(self, ticker):
        """
        Updates the value of all positions that are currently open.
        Value of closed positions is tallied as self.realised_pnl.
        """
        self.unrealised_pnl = 0
        self.equity = self.realised_pnl
        self.equity += self.init_cash

        for signal_id in self.positions:
            pt = self.positions[signal_id]
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            pt.update_market_value(bid, ask)
            self.unrealised_pnl += pt.unrealised_pnl

            #======DEBUG
            """
            t = self.price_handler.get_last_timestamp('EURUSD')
            if t.month == 1:
                from pudb import set_trace; set_trace()
            """

            self.equity += (
                pt.market_value - pt.cost_basis + pt.realised_pnl
            )
            self.margin += pt.margin
            self.free_margin = self.equity - self.margin
        
    def _add_position(
        self, action, ticker, signal_id,
        quantity, price, commission
    ):
        """
        Adds a new Position object to the Portfolio. This
        requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is added, the Portfolio values
        are updated.
        """
        if signal_id not in self.positions:
            open_timestamp = self.price_handler.get_last_timestamp(ticker)           

            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            position = Position(
                action, ticker, signal_id, quantity,
                price, commission, bid, ask,
                open_timestamp
            )
            self.positions[signal_id] = position
            self._update_portfolio(ticker)
        else:
            print(
                "Order %s is already in the positions list. "
                "Could not add a new position." % signal_id
            )

    def _modify_position(
        self, action, ticker, signal_id,
        quantity, price, commission
    ):
        """
        Modifies a current Position object to the Portfolio.
        This requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is modified, the Portfolio values
        are updated.
        """
        if signal_id in self.positions:
            self.positions[signal_id].transact_shares(
                action, quantity, price, commission
            )
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            self.positions[signal_id].update_market_value(bid, ask)

            if self.positions[signal_id].quantity == 0:
                closed= self.positions.pop(signal_id)
                closed.close_timestamp = self.price_handler.get_last_timestamp(ticker)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)
                self.new_pos_closed = True

            self._update_portfolio(ticker)
        else:
            print(
                "Order %s not in the current position list. "
                "Could not modify a current position." % signal_id
            )

    def transact_position(
        self, action, ticker, signal_id,
        quantity, price, commission, isclose
    ):
        """
        Handles any new position or modification to
        a current position, by calling the respective
        _add_position and _modify_position methods.

        Hence, this single method will be called by the
        PortfolioHandler to update the Portfolio itself.
        """
        if action == "BOT":
            self.cur_cash -= ((quantity * price) + commission)
        elif action == "SLD":
            self.cur_cash += ((quantity * price) - commission)

        if signal_id not in self.positions:
            self._add_position(
                action, ticker, signal_id, quantity,
                price, commission
            )
        else:
            self._modify_position(
                action, ticker, signal_id, quantity,
                price, commission
            )

        if isclose == True:
            self.new_order_closed = True;
