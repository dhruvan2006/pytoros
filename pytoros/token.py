import requests
import pandas as pd

class Token:
    """
    A class to represent a leveraged token on Toros Finance
    """
    def __init__(self, ticker: str) -> None:
        """
        Initialize the Token with a contract address.

        :param symbol: str: The token's contract address (e.g., "ARB:BTCBULL3X").
        """
        self.ticker: str = ticker
        splits = ticker.split(':')
        self.chain_name: str = splits[0]
        self.symbol: str = splits[1]

    def _get_chain_id(self, chain_name: str) -> int:
        chain_names = {
            "POL": 137,   # Polygon
            "OP": 10,     # Optimism
            "ARB": 42161, # Arbitrum
            "BASE": 8453, # Base
        }
        
        chain_id = chain_names.get(chain_name.upper())
        if chain_id is None:
            raise ValueError(f"Chain ID not found for chain name: {chain_name}")
        
        return chain_id
    
    def _get_token_address(self, chain_name: str, symbol: str) -> str:
        chain_id = self._get_chain_id(chain_name)
        
        url = "https://toros.finance/_next/data/mw471zlJ9uL1Ee-_If1FI/category/leverage.json?category=leverage"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        products = data.get('pageProps', {}).get('products', {})
        
        for product in products:
            if product.get('chainId') == chain_id and product.get('symbol') == symbol:
                return product.get('address')
        
        raise ValueError(f"Token with symbol '{symbol}' and chain '{chain_name}' not found.")

    def history(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical data for the token.

        :param period: str: The period of price history (can be "1d", "1w", "1m", or "1y", default is "1y").
        :param interval: str: The interval for data points (can be "1h", "4h", "1d", "1w", default is "1d").
        :return: pd.DataFrame: Token's price history as a DataFrame.
        """
        address = self._get_token_address(self.chain_name, self.symbol)
        url = "https://api-v2.dhedge.org/graphql"
        payload = {
            "query": "query GetTokenPriceCandles($address: String!, $period: String!, $interval: String) {\n  tokenPriceCandles(address: $address, period: $period, interval: $interval) {\n    timestamp\n    open\n    close\n    max\n    min\n  }\n}\n",
            "variables": {
                "address": address,
                "period": period,
                "interval": interval,
            },
            "operationName": "GetTokenPriceCandles"
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        candles = data.get("data", {}).get("tokenPriceCandles", [])
        if not candles:
            raise ValueError("No data returned for the specified parameters.")

        df = pd.DataFrame(candles)
        df = df.rename(columns={
            "timestamp": "Date",
            "open": "Open",
            "close": "Close",
            "max": "High",
            "min": "Low"
        })
        
        df["Date"] = pd.to_numeric(df["Date"], errors='coerce')
        df["Date"] = pd.to_datetime(df["Date"], unit='ms')
        df.set_index("Date", inplace=True)
        
        scale_factor = 10**18
        df[["Open", "Close", "High", "Low"]] = df[["Open", "Close", "High", "Low"]].apply(
            lambda x: x.astype(int) / scale_factor
        )
        
        return df
