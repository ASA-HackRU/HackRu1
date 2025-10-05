import os
import json
import threading
import yfinance as yf

class PortfolioStore:
    def __init__(self, filename="data/portfolio.json"):
        self.filename = filename
        self.lock = threading.Lock()
        self.stocks = []
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.stocks = json.load(f)
            else:
                self._save()
        except Exception:
            self.stocks = []
            self._save()

    def _save(self):
        with self.lock:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.stocks, f, indent=2, ensure_ascii=False)

    def _find_ticker(self, company_name: str):
        name = (company_name or "").strip()
        if not name:
            return None

        try:
            search_results = yf.utils.get_tickers(name)
            if search_results:
                return search_results[0]
        except Exception:
            pass


        tokens = name.split()
        guesses = [tokens[0].upper(), name.upper().replace(" ", "")]
        for g in guesses:
            try:
                data = yf.Ticker(g).history(period="1d")
                if not data.empty:
                    return g
            except Exception:
                pass

        return None

    def _get_current_price(self, ticker: str):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if data is None or data.empty:
                return None
            price = float(data["Close"][-1])
            return price
        except Exception:
            return None

    def add_stock(self, company_name: str, price_bought: float, quantity: int):
        if not company_name or price_bought is None or quantity is None:
            return {"error": "invalid input"}

        ticker = self._find_ticker(company_name)
        if not ticker:
            return {"error": "ticker_not_found"}

        current_price = self._get_current_price(ticker)
        if current_price is None:
            return {"error": "price_fetch_failed"}

        stock = {
            "company_name": company_name,
            "ticker": ticker,
            "price_bought": float(price_bought),
            "quantity": int(quantity),
            "current_price": float(current_price),
            "percentage_change": ((current_price - float(price_bought)) / float(price_bought)) * 100
        }

        self.stocks.append(stock)
        self._save()
        return {"stock": stock}

    def get_all(self):
       
        self.update_prices()
        return self.stocks

    def update_prices(self):
        changed = False
        for s in self.stocks:
            ticker = s.get("ticker")
            if not ticker:
                continue
            price = self._get_current_price(ticker)
            if price is not None:
                s["current_price"] = float(price)
                try:
                    s["percentage_change"] = ((price - float(s["price_bought"])) / float(s["price_bought"])) * 100
                except Exception:
                    s["percentage_change"] = 0.0
                changed = True
        if changed:
            self._save()
        return True
