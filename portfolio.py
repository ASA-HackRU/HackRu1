import yfinance as yf

class portfolio:
    def __init__(self):
        self.stocks = []

    def add_stock(self, company_name: str, price_bought: float, quantity: int):
    
        ticker = self._find_ticker(company_name)
        if not ticker:
            print(f"Could not find ticker for '{company_name}'. Stock not added.")
            return


        current_price = self._get_current_price(ticker)
        if current_price is None:
            print(f"Could not fetch current price for '{company_name}'. Stock not added.")
            return

    
        self.stocks.append({
            "company_name": company_name,
            "ticker": ticker,
            "price_bought": price_bought,
            "quantity": quantity,
            "current_price": current_price,
            "percentage_change": ((current_price - price_bought) / price_bought) * 100
        })

    def _find_ticker(self, company_name: str):
        try:
            search_results = yf.utils.get_tickers(company_name)
            if search_results:
                return search_results[0] 
        except Exception as e:
            print(f"Error finding ticker: {e}")
        return None

    def _get_current_price(self, ticker: str):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            return data["Close"][-1]
        except Exception as e:
            print(f"Error fetching price for ticker {ticker}: {e}")
            return None

    def update_prices(self):
        for stock in self.stocks:
            current_price = self._get_current_price(stock["ticker"])
            if current_price:
                stock["current_price"] = current_price
                stock["percentage_change"] = ((current_price - stock["price_bought"]) / stock["price_bought"]) * 100

    def get_portfolio_table(self):
        self.update_prices()
        table = []
        for stock in self.stocks:
            table.append({
                "Company Name": stock["company_name"],
                "Ticker": stock["ticker"],
                "Price Bought": stock["price_bought"],
                "Quantity": stock["quantity"],
                "Current Price": stock["current_price"],
                "Percentage Change": stock["percentage_change"]
            })
        return table

    def get_portfolio_summary(self):
        total_bought = sum(stock["price_bought"] * stock["quantity"] for stock in self.stocks)
        total_current = sum(stock["current_price"] * stock["quantity"] for stock in self.stocks)
        total_percentage_change = ((total_current - total_bought) / total_bought) * 100 if total_bought else 0
        return {
            "Total Worth": total_current,
            "Total Percentage Growth": total_percentage_change
        }


