# PyToros

Download leveraged token data from [Toros Finance](https://toros.finance/).

[![PyPI Version](https://img.shields.io/pypi/v/pytoros)](https://github.com/dhruvan2006/pytoros)
[![codecov](https://codecov.io/github/dhruvan2006/pytoros/graph/badge.svg?token=8WH1LQUOGP)](https://codecov.io/github/dhruvan2006/pytoros)
[![Monthly Downloads](https://img.shields.io/pypi/dm/pytoros)](https://github.com/dhruvan2006/pytoros)
[![License](https://img.shields.io/github/license/dhruvan2006/pytoros)](https://github.com/dhruvan2006/pytoros)

## Installation
```bash
pip install pytoros
```

## Usage
```python
import pytoros as toros

token = Token("ARB:BTCBULL3X")
history = token.history()
print(history)
```

## API Documentation

### Token Class

#### `Token(ticker: str)`
- **Parameters**:
  - `ticker` (str): The token's identifier (e.g., `ARB:BTCBULL3X`).
- **Description**:
  Initializes the Token object for fetching data.

#### `history(period: str = "1y", interval: str = "1d")`
- **Parameters**:
  - `period` (str): Time range for historical data. Options: `1d`, `1w`, `1m`, `1y` (default: `1y`).
  - `interval` (str): Time interval between data points. Options: `1h`, `4h`, `1d`, `1w` (default: `1d`).
- **Returns**:
  A `pandas.DataFrame` containing historical price data with the following columns:
  - `Date`: Timestamp of the data point.
  - `Open`: Opening price.
  - `Close`: Closing price.
  - `High`: Highest price during the interval.
  - `Low`: Lowest price during the interval.
