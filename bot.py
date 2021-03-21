import numpy as np

class SimpleBreakoutExample(QCAlgorithm):

    def Initialize(self):
        self.SetCash(100000)
     
        self.SetStartDate(2017,9,1)
        self.SetEndDate(2021,3,21)
        
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        self.lookback = 20
        
        self.ceiling, self.floor = 30, 10
        
        self.initialStopRisk = 0.98
        self.trailingStopRisk = 0.9
        
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 20), \
                        Action(self.EveryMarketOpen))


    def OnData(self, data):
       
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)

 
    def EveryMarketOpen(self):
        
        close = self.History(self.symbol, 31, Resolution.Daily)["close"]
        todayvol = np.std(close[1:31])
        yesterdayvol = np.std(close[0:30])
        deltavol = (todayvol - yesterdayvol) / todayvol
        self.lookback = round(self.lookback * (1 + deltavol))
       
        if self.lookback > self.ceiling:
            self.lookback = self.ceiling
        elif self.lookback < self.floor:
            self.lookback = self.floor
        
        self.high = self.History(self.symbol, self.lookback, Resolution.Daily)["high"]
        
        if not self.Securities[self.symbol].Invested and \
                self.Securities[self.symbol].Close >= max(self.high[:-1]):
            self.SetHoldings(self.symbol, 1)
            self.breakoutlvl = max(self.high[:-1])
            self.highestPrice = self.breakoutlvl
        
        
        if self.Securities[self.symbol].Invested:
            
            if not self.Transactions.GetOpenOrders(self.symbol):
                self.stopMarketTicket = self.StopMarketOrder(self.symbol, \
                                        -self.Portfolio[self.symbol].Quantity, \
                                        self.initialStopRisk * self.breakoutlvl)
            
            
            if self.Securities[self.symbol].Close > self.highestPrice and \
                    self.initialStopRisk * self.breakoutlvl < self.Securities[self.symbol].Close * self.trailingStopRisk:
              
                self.highestPrice = self.Securities[self.symbol].Close
          
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.Securities[self.symbol].Close * self.trailingStopRisk
                self.stopMarketTicket.Update(updateFields)
                
        
                self.Debug(updateFields.StopPrice)
         
            self.Plot("Data Chart", "Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))