from dataclasses import dataclass
from datetime import datetime
from pickletools import float8


@dataclass
class CandlestickData:
    open_price: float
    close_price: float
    high_price: float
    low_price: float


@dataclass
class HighsAndLows:
    high_today: float
    high_last_7_days: float
    high_last_30_days: float
    high_last_365_days: float
    high_all_time: float
    low_today: float
    low_last_7_days: float
    low_last_30_days: float
    low_last_365_days: float
    low_all_time: float


@dataclass
class Quote:
    cusip: int
    symbol: str
    description: str
    datetime_of_quote: datetime
    exchange_name: str
    delayed: bool
    ask_price: float
    ask_size: int
    bid_price: float
    bid_size: int
    candlestick_data: CandlestickData
    highs_and_lows: HighsAndLows
    mark: float
    last_price: float
    last_size: int
    regular_market_last_price: float
    regular_market_last_size: int
    total_volume: int
    volatility: float
    dividend_amount: float
    dividend_data: datetime
    dividend_yield: float
    pe_ratio: float
