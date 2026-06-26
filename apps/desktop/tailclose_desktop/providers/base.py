from typing import Protocol

from tailclose_desktop.models import StockQuote


class ProviderError(RuntimeError):
    """Raised when a market data provider cannot return data."""


class QuoteProvider(Protocol):
    def current_quotes(self) -> list[StockQuote]:
        """Return the provider's current A-share quotes."""
