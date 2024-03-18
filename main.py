import requests as r
from bs4 import BeautifulSoup
from dataclasses import dataclass
from tabulate import tabulate

@dataclass
class Stock :
    ticker : str
    exchange : str
    price: float = 0
    currency: str = 'USD'
    inr_price : float = 0

    def __post_init__(self):
        price_info = get_price_information(self.ticker, self.exchange)

        if price_info['ticker'] == self.ticker:
            self.price = price_info['price']
            self.currency = price_info['currency']
            self.inr_price = price_info['inr_price']

@dataclass
class Position:
    stock : Stock
    quantity : int   

@dataclass
class Portfolio:
    positions: list[Position]

    def get_total_value(self): 
        total_value = 0
        
        for position in self.positions:
            total_value += position.quantity * position.stock.inr_price
            
        return total_value

def get_fx_to_inr(currency):
    fx_url= f"https://www.google.com/finance/quote/{currency}-INR"
    resp = r.get(fx_url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    fx_rate = soup.find("div", attrs={'data-last-price': True})
    fx = float(fx_rate['data-last-price'])
    return fx

def get_price_information(ticker, exchange):
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
    resp = r.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    price_div = soup.find("div", attrs={'data-last-price': True})
    price = float(price_div['data-last-price'])
    currency = price_div['data-currency-code']
    inr_price = price
    if currency != 'INR':
        fx = get_fx_to_inr(currency)
        inr_price = round(price * fx,2)

    return {
        "ticker" : ticker,
        "exchange" : exchange,
        "price" : price,
        "currency" : currency,
        "inr_price" : inr_price
    }

def display_portfolio_summary(portfolio):
    if not isinstance(portfolio,Portfolio):
        raise TypeError("Provide valid instance of Portfolio class type")
    
    portfolio_value = portfolio.get_total_value()
    
    position_data = []
    
    for position in portfolio.positions:
        position_data.append([
            position.stock.ticker,
            position.stock.exchange,
            position.quantity,
            position.stock.inr_price,
            position.quantity * position.stock.inr_price,
            position.quantity * position.stock.inr_price / portfolio_value
        ])
    
    print(tabulate(position_data,
                   headers=['Ticker','Exchange','Quantity','Price', 'Market Value', '% Allocation'],
                    tablefmt = 'psql',
                    floatfmt = '.2f'
            ))
    
    print(f'Total portfolio value : {portfolio_value: ,.2f}')


if __name__ == "__main__":
    # print(get_price_information('SHOP','TSE'))
    # print(get_fx_to_inr("EUR"))
    shop = Stock('SHOP','TSE')
    msft = Stock('MSFT', 'NASDAQ')
    googl = Stock('GOOGL', 'NASDAQ')
    pf = Portfolio([Position(shop, 10), Position(msft,2), Position(googl, 30)])
    display_portfolio_summary(pf)
    