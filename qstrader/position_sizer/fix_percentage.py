class FixedPercentage:

"""
For use in Quantconnect

Total loss for each position is limited to a fixed percentage of a value V.
V is initialised as the account balance, when a position is closed with positive profit,
V will be updated as the latest account balance, if the profit is negative, V remains
unchanged.

"""

    def __init__(self, qca):
        self.qca = qca
        self.v = None
        self.PERCENTAGE = 0.03

    def size_order(self):
        last_profit = self.qca.Portfolio[self.qca.ticker].LastTradeProfit
        maxLoss_priceDiff = self.qca.fabowave.fab_bin[2] - self.qca.fabowave.fab_bin[1]

        if self.v is None:
            self.qca.Debug("Last profit: {}.".format(last_profit))
            self.v = self.qca.remainingCash

        else:
            self.qca.Debug("Last profit: {}.".format(last_profit))
            if last_profit > 0:
                #Update self.v
                self.v += last_profit
                self.qca.Debug("self.v updated")

        max_loss = self.v * self.PERCENTAGE

        return round(max_loss / maxLoss_priceDiff,1)


