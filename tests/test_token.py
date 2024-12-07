import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pytoros import Token

class TestToken(unittest.TestCase):
    @patch('requests.get')
    def test_get_token_address_success(self, mock_get):
        mock_html = '''
        <html>
            <body>
                <script id="__NEXT_DATA__" type="application/json">
                    {
                        "props": {
                            "pageProps": {
                                "categoryMap": {
                                    "Leverage": [
                                        {"chainId": 42161, "symbol": "BTCBULL3X", "address": "0x1234567890abcdef"}
                                    ]
                                }
                            }
                        }
                    }
                </script>
            </body>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        token = Token("ARB:BTCBULL3X")

        address = token._get_token_address()
        self.assertEqual(address, '0x1234567890abcdef')
    
    @patch('requests.get')
    def test_get_token_address_not_found(self, mock_get):
        # Mock the HTML response with an empty "Leverage" array
        mock_html = '''
        <html>
            <body>
                <script id="__NEXT_DATA__" type="application/json">
                    {
                        "props": {
                            "pageProps": {
                                "categoryMap": {
                                    "Leverage": []
                                }
                            }
                        }
                    }
                </script>
            </body>
        </html>
        '''
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        token = Token("ARB:BTCBULL3X")
        
        with self.assertRaises(ValueError):
            token._get_token_address()
    
    @patch('requests.post')
    def test_history_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'tokenPriceCandles': [
                    {'timestamp': 1635225600000, 'open': 5000000000000000000, 'close': 5100000000000000000, 'max': 5200000000000000000, 'min': 4900000000000000000}
                ]
            }
        }
        mock_post.return_value = mock_response

        token = Token("ARB:BTCBULL3X")

        df = token.history(period="1y", interval="1d")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.index[0], pd.to_datetime(1635225600000, unit='ms'))
        self.assertEqual(df['Open'].iloc[0], 5.0)
        self.assertEqual(df['Close'].iloc[0], 5.1)   
    
    @patch('requests.post')
    def test_history_no_data(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'tokenPriceCandles': []}}
        mock_post.return_value = mock_response

        token = Token("ARB:BTCBULL3X")

        with self.assertRaises(ValueError):
            token.history(period="1y", interval="1d")

class LiveTestToken(unittest.TestCase):

    def test_get_token_address_live(self):
        token = Token("ARB:BTCBULL3X")
        address = token._get_token_address()
        self.assertEqual(address, "0xad38255febd566809ae387d5be66ecd287947cb9")
    
    def test_get_token_history(self):
        token = Token("ARB:BTCBULL3X")
        data = token.history()
        self.assertEqual(pd.to_datetime('2024-02-22'), data.index[0])

if __name__ == '__main__':
    unittest.main()
