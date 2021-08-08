"""Collection of python protocols and classes that define the broker API"""
import re
from abc import abstractmethod
from typing import Protocol
from typing import Callable
from typing import Any
from typing import Union
from typing import Tuple
from eepythontools.process_tools import RunRepeatedly
from stock_trader import Quote


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


class Broker(Protocol):
    requested_quotes_streams: dict[str, RunRepeatedly]

    """To support a new broker simply create a class that implements this."""

    @abstractmethod
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

    @abstractmethod
    def sell(
        self,
        instrument: str,
        quantity: float,
        limit_price: Union[float, None] = None,
        stop: Union[Stop, None] = None,
    ) -> bool:
        """
        sell sells an instrument.  If limit_price = None then market sell.
        If limit_price = None then order a market sell.
        If stop != None then order is a stop order (see Stop class).

        :param instrument: The instrument to sell.
        :type instrument: str
        :param quantity: The number to sell.
        :type quantity: float
        :param limit_price: Limit price, defaults to None which sells at market.
        :type limit_price: Union[float, None], optional
        :param stop: [description], The Stop that triggers this order or None.
        :type stop: Union[Stop, None], optional
        :return: Whether order was successfully sent.
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, instrument: str) -> Quote:
        """
        get_quote gets current price quote for instrument.

        :param instrument: The instrument we want a quote for.
        :type instrument: str
        :raises NotImplementedError: [description]
        :return: The Quote (see Quote class for details).
        :rtype: Quote
        """
        raise NotImplementedError

    def start_streaming_quotes(
        self, instrument: str, receiver_function: Callable[[Quote], Any]
    ) -> bool:
        """Begin receiving streaming quotes for instrument."""
        # Implementation below requests a quote every 30 seconds.
        # If a broker provides a streaming quote interface, use theirs!
        # If you need quotes for more than 2 instruments, do not use this!
        # Why? Most brokers dislike getting too many requests per minute.
        self.requested_quotes_streams[instrument] = RunRepeatedly(
            30, receiver_function, self.get_quote, instrument
        )
        self.requested_quotes_streams[instrument].start()
        return True

    def stop_streaming_quotes(self, instrument: str) -> bool:
        """Stop receiving streaming quotes for instrument."""
        # See start_streaming_quotes for why this implementation is limited
        self.requested_quotes_streams[instrument].stop()
        del self.requested_quotes_streams[instrument]
        return True
