"""Collection of python protocols and classes that define the broker API"""
import re
from datetime import datetime
from typing import Protocol
from typing import Callable
from typing import Any
from typing import Union
from typing import Tuple
from dataclasses import dataclass
from eepythontools.threading import RunRepeatedly


class Stop:
    """Defines the stop portion of an order."""

    # stop_type is one of "$" or "%"
    stop_type: str
    # stop is the numerical portion of the stop
    stop: Union[float, None]

    @classmethod
    def stop_from_string(
        cls, self: "Stop", stop_as_string: Union[str, None]
    ) -> Tuple[str, Union[float, None]]:
        """Convert a string describing a stop to a stop_type and stop"""
        if not isinstance(stop_as_string, str):
            raise TypeError("Stop initialization parameters are invalid.")
        stop_string_parser = re.compile(
            r"^(:P<dollar_sign_before>$)?(:P<plus_or_minus_before>[-+])?(:P<dollar_sign_after_plus_or_minus>$)?(:P<whole_number>\d+(:P<decimal>\.\d*)?|\.\d+)(:P<exponent>[eE][-+]?\d+)?(:P<trailing_percent_or_dollar_sign>[%$])?$"
        )
        parser_result = stop_string_parser.match(stop_as_string)

        if parser_result is None:
            raise ValueError("Unable to parse stop string: " + stop_as_string)

        self.stop_type = (
            parser_result.group("dollar_sign_before")
            if parser_result.group("dollar_sign_before") is not None
            else parser_result.group("dollar_sign_after_plus_or_minus")
            or parser_result.group("trailing_percent_or_dollar_sign")
        )

        if self.stop_type is None:
            raise ValueError("Syntax error in stop string: " + stop_as_string)
        self.stop = (
            float(parser_result.group("whole_number"))
            if parser_result.group("decimal") is None
            else float(parser_result.group("whole_number"))
            + float(parser_result.group("decimal"))
            if parser_result.group("whole_number") is not None
            else float(parser_result.group("decimal"))
        )

        if self.stop is None:
            raise ValueError("Syntax error in stop string: " + stop_as_string)

        return self.stop_type, self.stop

    def __init__(self, stop_type: str, stop: Union[float, None] = None):
        if stop is None:
            self.stop_type, self.stop = Stop.stop_from_string(
                self, stop_as_string=stop_type
            )
        else:
            self.stop_type = stop_type
            self.stop = stop


@dataclass
class Quote:
    high_52week: float
    low_52week: float
    ask_price: float
    ask_size: int
    bid_price: float
    bid_size: int
    close_price: float
    cusip: int
    delayed: bool
    description: str
    dividend_amount: float
    dividend_data: datetime
    dividend_yield: float
    exchange_name: str
    high_price: float
    last_price: float
    last_size: int
    low_price: float
    mark: float
    open_price: float
    pe_ratio: float
    regular_market_last_price: float
    regular_market_last_size: int
    symbol: str
    total_volume: int
    volatility: float


class Broker(Protocol):
    streaming_quotes: dict[str, RunRepeatedly]

    """To support a new broker simply create a class that implements this."""

    def buy(
        self,
        instrument: str,
        quantity: float,
        limit_price: Union[float, None] = None,
        stop: Union[Stop, None] = None,
    ) -> bool:
        """Buy an instrument.
        If limit_price = None then order a market buy.
        If stop != None then order is a stop order (see Stop class)."""
        raise NotImplementedError

    def sell(
        self,
        instrument: str,
        quantity: float,
        limit_price: Union[float, None] = None,
        stop: Union[Stop, None] = None,
    ) -> bool:
        """Sell an instrument.  If limit_price = None then market sell.
        If limit_price = None then order a market sell.
        If stop != None then order is a stop order (see Stop class)."""
        raise NotImplementedError

    def quote(self, instrument: str) -> Quote:
        """Get current price quote for instrument."""
        raise NotImplementedError

    def start_streaming_quotes(
        self, instrument: str, receiver_function: Callable[[Quote], Any]
    ) -> bool:
        """Begin receiving streaming quotes for instrument."""
        # Implementation below requests a quote every 30 seconds.
        # If a broker provides a streaming quote interface, use theirs!
        # If you need quotes for more than 2 instruments, do not use this!
        # Why? Most brokers dislike getting too many requests per minute.
        self.streaming_quotes[instrument] = RunRepeatedly(
            30, receiver_function, self.quote, instrument
        )
        self.streaming_quotes[instrument].start()
        return True

    def stop_streaming_quotes(self, instrument: str) -> bool:
        """Stop receiving streaming quotes for instrument."""
        # See start_streaming_quotes for why this implementation is limited
        self.streaming_quotes[instrument].stop()
        del self.streaming_quotes[instrument]
        return True
