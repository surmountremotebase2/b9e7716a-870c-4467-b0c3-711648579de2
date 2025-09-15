from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import BankPrimeLoanRate, CorporateProfitAfterTax

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the assets involved and the data needed for analysis.
        self.tickers = ["SPY"]  # Token representative of equities market (S&P 500 ETF).
        self.data_list = [BankPrimeLoanRate(), CorporateProfitAfterTax()]

    @property
    def assets(self):
        # Define the assets that the strategy will trade.
        return self.tickers

    @property
    def interval(self):
        # Interval for data pulling and strategy evaluation.
        # Note: Limited by what is available for the data points.
        return "1day"

    @property
    def data(self):
        # Data needed for the strategy: Prime Loan Rate & Corporate Profit After Tax.
        return self.data_list

    def run(self, data):
        allocation_dict = {"SPY": 0.5}  # Default allocation to 50%
        try:
            prime_rate_data = data[("bank_prime_loan_rate",)]
            corp_profit_data = data[("corporate_profit_after_tax",)]
            
            if len(prime_rate_data) > 1 and len(corp_profit_data) > 1:
                # Check if there is an increase in the prime rate indicating a tightening.
                prime_rate_trend = prime_rate_data[-1]["value"] > prime_rate_data[-2]["value"]
                # Check if corporate profits are increasing, indicating strong corporate health.
                profit_trend = corp_profit_data[-1]["value"] > corp_profit_data[-2]["value"]

                # Strategy logic: Increase allocation if corporate profits are rising against rising prime rates.
                if prime_rate_trend and profit_trend:
                    allocation_dict["SPY"] = 0.8  # More confident, increase equity allocation.
                elif not profit_trend:
                    # Reduce allocation if corporate profits are not increasing.
                    allocation_dict["SPY"] = 0.3  # Less confident, reduce equity allocation.
                
                log(f"Allocation set to {allocation_dict['SPY']} for SPY based on latest data trends.")

        except KeyError as e:
            log(f"Data missing for the key: {e}, using default allocation.")
        
        return TargetAllocation(allocation_dict)