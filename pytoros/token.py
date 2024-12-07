import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

class Token:
    """
    A class to represent a leveraged token on Toros Finance.
    """
    CHAIN_IDS = {
        "POL": 137,     # Polygon
        "OP": 10,       # Optimism
        "ARB": 42161,   # Arbitrum
        "BASE": 8453,   # Base
    }
    TOROS_URL = "https://toros.finance/"
    GRAPHQL_URL = "https://api-v2.dhedge.org/graphql"
    SCALE_FACTOR = 10**18

    def __init__(self, ticker: str) -> None:
        """
        Initialize the Token with a ticker string.

        :param ticker: str: The token's ticker in "CHAIN:SYMBOL" format (e.g., "ARB:BTCBULL3X").
        """
        if ':' not in ticker:
            raise ValueError("Ticker must be in 'CHAIN:SYMBOL' format.")

        self.ticker: str = ticker
        self.chain_name, self.symbol = ticker.split(':', 1)

    def _get_chain_id(self) -> int:
        chain_id = self.CHAIN_IDS.get(self.chain_name.upper())
        if chain_id is None:
            raise ValueError(f"Invalid chain name '{self.chain_name}'. Valid options: {', '.join(self.CHAIN_IDS.keys())}")
        return chain_id
    
    def _get_token_address(self) -> str:
        response = requests.get(self.TOROS_URL, timeout=10)
        response.raise_for_status()
        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")

        if script_tag:
            try:
                json_data = json.loads(script_tag.string)
                chain_id = self._get_chain_id()
                leverage = json_data["props"]["pageProps"]["categoryMap"]["Leverage"]
                for token in leverage:
                    if token["chainId"] == chain_id and token["symbol"] == self.symbol:
                        return token["address"]
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

        raise ValueError(f"Token with symbol '{self.symbol}' and chain '{self.chain_name}' not found.")

    def history(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical data for the token.

        :param period: str: Period of price history ("1d", "1w", "1m", "1y").
        :param interval: str: Interval for data points ("1h", "4h", "1d", "1w").
        :return: pd.DataFrame: Token's price history as a DataFrame.
        """
        valid_periods = {"1d", "1w", "1m", "1y"}
        valid_intervals = {"1h", "4h", "1d", "1w"}

        if period not in valid_periods:
            raise ValueError(f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}")
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval '{interval}'. Valid options: {', '.join(valid_intervals)}")

        address = self._get_token_address()
        payload = {
            "query": """query GetTokenPriceCandles($address: String!, $period: String!, $interval: String) {
                tokenPriceCandles(address: $address, period: $period, interval: $interval) {
                    timestamp
                    open
                    close
                    max
                    min
                }
            }""",
            "variables": {
                "address": address,
                "period": period,
                "interval": interval,
            },
            "operationName": "GetTokenPriceCandles"
        }

        response = requests.post(self.GRAPHQL_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        candles = data.get("data", {}).get("tokenPriceCandles", [])
        if not candles:
            raise ValueError("No data returned for the specified parameters.")

        df = pd.DataFrame(candles).rename(columns={
            "timestamp": "Date",
            "open": "Open",
            "close": "Close",
            "max": "High",
            "min": "Low"
        })

        df["Date"] = pd.to_datetime(pd.to_numeric(df["Date"], errors='coerce'), unit='ms')
        df.set_index("Date", inplace=True)
        df[["Open", "Close", "High", "Low"]] = df[["Open", "Close", "High", "Low"]].apply(
            lambda x: x.astype(float) / self.SCALE_FACTOR
        )
        return df